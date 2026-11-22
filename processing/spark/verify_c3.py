"""Run real Spark jobs/tests and compare artifacts to the independent fixtures."""
import csv
from datetime import datetime, timezone
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "evidence/C3"


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def main():
    if sys.version_info[:2] != (3, 12):
        raise SystemExit("Use the tested Python 3.12 environment (.venv/c3-runtime).")
    if not os.environ.get("JAVA_HOME"):
        candidates = [p for p in (ROOT / ".venv/java").glob("*") if (p / "bin/java.exe").is_file()]
        if len(candidates) != 1:
            raise SystemExit("Set JAVA_HOME to an official Java 17 runtime.")
        os.environ["JAVA_HOME"] = str(candidates[0])
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    os.environ["SPARK_HOME"] = str(Path(importlib.util.find_spec("pyspark").origin).parent)
    os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"
    os.environ["PYTHONUTF8"] = "1"
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    # Invalidate a prior success before starting, so a failed rerun cannot leave
    # stale passing evidence next to a new failed transcript.
    (EVIDENCE / "verification.json").write_text(json.dumps({"status": "running"}) + "\n", encoding="utf-8")
    transcript = ["C3 actual execution transcript; AI-assisted working material.",
                  "Local paths and the OS account directory are redacted; no fabricated screenshot."]
    commands = []
    for dataset in ("table2", "responses"):
        out = "table2" if dataset == "table2" else "extended"
        commands.append([sys.executable, "processing/spark/rating_count.py", "--input",
                         f"data/synthetic/c3-{dataset}.csv", "--output-dir", f"data/aggregated/c3/{out}"])
    commands.append([sys.executable, "-m", "unittest", "discover", "-s", "tests/processing", "-p", "test_*.py", "-v"])
    run_results = []
    for command in commands:
        display = "python " + " ".join(command[1:])
        print("Running:", display, flush=True)
        result = subprocess.run(command, cwd=ROOT, capture_output=True, encoding="utf-8", errors="replace")
        output = result.stdout + result.stderr
        # Do not publish OS account identifiers or absolute local paths.
        for private, replacement in ((str(ROOT), "<repo>"), (str(ROOT).replace("\\", "/"), "<repo>"),
                                     (os.environ.get("USERPROFILE", ""), "<user>")):
            if private:
                output = output.replace(private, replacement)
        transcript.extend(["\n$ " + display, output, f"Exit code: {result.returncode}"])
        (EVIDENCE / "run.txt").write_text("\n".join(transcript) + "\n", encoding="utf-8")
        run_results.append({"command": display, "exit_code": result.returncode})
        if result.returncode:
            (EVIDENCE / "verification.json").write_text(json.dumps({
                "status": "failed", "commands": run_results}, indent=2) + "\n", encoding="utf-8")
            print("FAILED; see evidence/C3/run.txt", flush=True)
            return result.returncode
    expected = json.loads((ROOT / "tests/processing/expected-counts.json").read_text(encoding="utf-8"))
    ledger = read_csv(ROOT / "tests/processing/expected-ledger.csv")
    verified = {}
    for name in ("table2", "extended"):
        folder = ROOT / "data/aggregated/c3" / name
        summary = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
        assert {k: summary[k] for k in expected[name]} == expected[name]
        audit = read_csv(folder / "audit.csv")
        assert [{k: row[k] for k in ledger[0]} for row in audit] == ledger[:summary["input_rows"]]
        counts = read_csv(folder / "counts.csv")
        assert {r["rating"]: int(r["count"]) for r in counts} == expected[name]["counts"]
        clean = read_csv(folder / "cleaned.csv")
        assert len(clean) == summary["accepted"] == sum(summary["counts"].values())
        assert len({r["response_id"] for r in clean}) == len(clean)
        verified[name] = {"summary_and_every_row_match_reference": True, **expected[name],
                          "input_sha256": summary["input_sha256"], "runtime": summary["runtime"]}
    table = read_csv(ROOT / "data/synthetic/c3-table2.csv")
    extended = read_csv(ROOT / "data/synthetic/c3-responses.csv")
    assert extended[:12] == table and len(extended) >= 30
    sources = ("processing/spark/rating_count.py", "processing/spark/verify_c3.py", "processing/spark/requirements.txt",
               "tests/processing/test_rating_count.py", "tests/processing/expected-counts.json",
               "tests/processing/expected-ledger.csv")
    manifest = {"status": "passed", "verified_at_utc": datetime.now(timezone.utc).isoformat(),
                "source_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sources},
                "commands": run_results, "datasets": verified,
                "table2_preserved_as_prefix": True,
                "limitations": ["Single machine only", "No C1/C2/cloud integration executed",
                                "Reference ledger is AI-assisted; student hand verification not claimed"]}
    (EVIDENCE / "verification.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("PASS: Table 2 5/3/2; extended 12/10/8; all 40 row dispositions and edge tests verified.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        EVIDENCE.mkdir(parents=True, exist_ok=True)
        (EVIDENCE / "verification.json").write_text(json.dumps({
            "status": "failed", "error_type": type(error).__name__}) + "\n", encoding="utf-8")
        raise
