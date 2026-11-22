"""C-II: a bounded, local-mode PySpark rating count with a row-level audit.

CSV ingestion is on the driver to attach a stable export-row ordinal. Cleaning,
deduplication and aggregation run in Spark SQL, not a Python Counter substitute.
The 10 MiB cap is deliberate: this is a teaching/local prototype, not a cluster ETL.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
from datetime import datetime, timezone

from pyspark.sql import SparkSession, Window, functions as F
from pyspark.sql.types import LongType, StringType, StructField, StructType

RATINGS = ("Good", "OK", "Poor")
SCHEMA = StructType([
    StructField("source_row", LongType(), False),
    StructField("response_id", StringType(), False),
    StructField("rating", StringType(), False),
    StructField("submitted_at", StringType(), False),
])
REQUIRED = ("response_id", "rating", "submitted_at")


def read_export(path: Path) -> list[tuple]:
    """Accept C1's provisional three-column CSV without changing C1's interface."""
    if path.stat().st_size > 10 * 1024 * 1024:
        raise ValueError("Local CSV adapter accepts at most 10 MiB; use a distributed reader for larger exports")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError("CSV needs unique column names and a header")
        if not set(REQUIRED).issubset(reader.fieldnames):
            raise ValueError("CSV must contain response_id,rating,submitted_at")
        rows = []
        for number, row in enumerate(reader, start=1):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Malformed CSV record {number}: column count differs from header")
            rows.append((number, *(row[name] for name in REQUIRED)))
    return rows


def create_session(partitions: int = 4) -> SparkSession:
    if partitions < 1:
        raise ValueError("partitions must be positive")
    # Avoid worker/driver Python-version mismatches on machines with several Pythons.
    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    os.environ.setdefault("SPARK_LOCAL_IP", "127.0.0.1")
    spark = (SparkSession.builder.appName("Member3-C3-rating-count")
             .master("local[2]")
             .config("spark.driver.host", "127.0.0.1")
             .config("spark.driver.bindAddress", "127.0.0.1")
             .config("spark.ui.enabled", "false")
             .config("spark.ui.showConsoleProgress", "false")
             .config("spark.sql.session.timeZone", "Asia/Kuala_Lumpur")
             .config("spark.sql.shuffle.partitions", str(partitions))
             .config("spark.sql.adaptive.enabled", "false")
             .getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def classify(frame):
    """First physical CSV record wins per exact ID, BEFORE rating validation.

    Do not trim/case-fold/correct ratings or IDs. Blank/whitespace-only IDs are
    invalid. Conflicting later records are duplicates, not rating corrections.
    """
    ranked = frame.withColumn("id_occurrence", F.row_number().over(
        Window.partitionBy("response_id").orderBy("source_row")))
    return ranked.withColumn("status",
        F.when(F.length(F.trim(F.col("response_id"))) == 0, F.lit("invalid_id"))
         .when(F.col("id_occurrence") > 1, F.lit("duplicate"))
         .when(F.col("rating").isin(*RATINGS), F.lit("accepted"))
         .otherwise(F.lit("invalid_rating")))


def make_frame(spark, rows):
    """Bound local fixture -> Spark SQL, without Python-worker/RDD serialization.

    All CSV values are bound parameters, never interpolated SQL. This bounded
    adapter avoids native Windows Python-worker socket failures. All downstream
    data processing still runs in the real Spark execution engine.
    """
    columns = SCHEMA.fieldNames()
    if not rows:
        return spark.sql("SELECT CAST(NULL AS BIGINT) source_row, "
                         "CAST(NULL AS STRING) response_id, CAST(NULL AS STRING) rating, "
                         "CAST(NULL AS STRING) submitted_at WHERE FALSE")
    bindings = {}
    values = []
    for index, row in enumerate(rows):
        placeholders = []
        for column, value in zip(columns, row):
            key = f"p{index}_{column}"
            bindings[key] = value
            placeholders.append(":" + key)
        values.append("(" + ",".join(placeholders) + ")")
    return spark.sql("SELECT CAST(source_row AS BIGINT) source_row, response_id, rating, submitted_at "
                     "FROM VALUES " + ",".join(values) + " AS export(" + ",".join(columns) + ")",
                     args=bindings)


def aggregate(classified):
    return classified.filter(F.col("status") == "accepted").groupBy("rating").count()


def collect_results(classified) -> tuple[list[dict], list[dict], dict]:
    # Collecting is intentional for the bounded local prototype and its small audit.
    audit = [r.asDict() for r in classified.orderBy("source_row").collect()]
    found = {r["rating"]: r["count"] for r in aggregate(classified).collect()}
    counts = [{"rating": rating, "count": found.get(rating, 0)} for rating in RATINGS]
    statuses = {name: sum(r["status"] == name for r in audit)
                for name in ("accepted", "duplicate", "invalid_rating", "invalid_id")}
    summary = {"input_rows": len(audit), **statuses,
               "counts": {r["rating"]: r["count"] for r in counts}}
    assert len(audit) == sum(statuses.values()), "Row conservation failed"
    assert sum(found.values()) == statuses["accepted"], "Rating total failed"
    accepted_ids = [r["response_id"] for r in audit if r["status"] == "accepted"]
    assert len(accepted_ids) == len(set(accepted_ids)), "Accepted IDs are not unique"
    return audit, counts, summary


def write_csv(path: Path, rows: list[dict], fields: tuple[str, ...]):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run_job(spark, input_path: Path, output_dir: Path, partitions: int) -> dict:
    if partitions < 1:
        raise ValueError("partitions must be positive")
    outputs = ("counts.csv", "cleaned.csv", "audit.csv", "summary.json", "execution-plan.txt")
    if input_path.resolve() in [(output_dir / name).resolve() for name in outputs]:
        raise ValueError("Output must not overwrite the input")
    rows = read_export(input_path)
    spark.conf.set("spark.sql.shuffle.partitions", str(partitions))
    frame = make_frame(spark, rows).repartition(partitions)
    classified = classify(frame).cache()
    try:
        audit, counts, summary = collect_results(classified)
        summary.update({
            "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
            "input_name": input_path.name,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "scope": "whole supplied CSV; no implicit day filter",
            "deduplication": "first CSV record per exact response_id, before rating validation",
            "rating_policy": "exact Good, OK, Poor; no trimming or case folding",
            "runtime": {"spark": spark.version, "python": platform.python_version(),
                        "java": spark.sparkContext._jvm.java.lang.System.getProperty("java.version"),
                        "os": platform.system(), "master": spark.sparkContext.master,
                        "repartitioned_input": frame.rdd.getNumPartitions(),
                        "shuffle_partitions": int(spark.conf.get("spark.sql.shuffle.partitions")),
                        "adaptive_execution": spark.conf.get("spark.sql.adaptive.enabled"),
                        "region": "local computer; no cloud region"},
        })
        output_dir.mkdir(parents=True, exist_ok=True)
        write_csv(output_dir / "counts.csv", counts, ("rating", "count"))
        fields = ("source_row", "response_id", "rating", "submitted_at", "id_occurrence", "status")
        write_csv(output_dir / "audit.csv", audit, fields)
        write_csv(output_dir / "cleaned.csv", [r for r in audit if r["status"] == "accepted"], REQUIRED)
        (output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        plan = spark.sparkContext._jvm.PythonSQLUtils.explainString(aggregate(classified)._jdf.queryExecution(), "formatted")
        (output_dir / "execution-plan.txt").write_text(plan.rstrip() + "\n", encoding="utf-8")
        return summary
    finally:
        classified.unpersist()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--partitions", type=int, default=4)
    args = parser.parse_args()
    if args.partitions < 1:
        parser.error("--partitions must be positive")
    spark = create_session(args.partitions)
    try:
        result = run_job(spark, args.input, args.output_dir, args.partitions)
        print(json.dumps({k: result[k] for k in ("input_name", "input_rows", "accepted", "duplicate", "invalid_rating", "invalid_id", "counts", "runtime")}, indent=2))
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
