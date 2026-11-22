"""End-to-end reference checks and edge cases; run from repository root."""
import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("rating_count", ROOT / "processing/spark/rating_count.py")
job = importlib.util.module_from_spec(spec)
spec.loader.exec_module(job)
EXPECTED = json.loads((ROOT / "tests/processing/expected-counts.json").read_text(encoding="utf-8"))


class RatingCountTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = job.create_session()

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def process(self, rows, partitions=4):
        self.spark.conf.set("spark.sql.shuffle.partitions", str(partitions))
        frame = job.make_frame(self.spark, rows).repartition(partitions)
        return job.collect_results(job.classify(frame))

    def test_table2_and_extended_match_reference_and_row_ledger(self):
        table = job.read_export(ROOT / "data/synthetic/c3-table2.csv")
        extended = job.read_export(ROOT / "data/synthetic/c3-responses.csv")
        self.assertEqual(table, extended[:12], "Must extend, not replace Table 2")
        self.assertGreaterEqual(len(extended), 30)
        for name, rows in (("table2", table), ("extended", extended)):
            with self.subTest(dataset=name):
                audit, counts, summary = self.process(rows)
                self.assertEqual(summary, EXPECTED[name])
                with (ROOT / "tests/processing/expected-ledger.csv").open(newline="", encoding="utf-8") as f:
                    ledger = list(csv.DictReader(f))[:len(rows)]
                actual = [{k: str(row[k]) for k in ledger[0]} for row in audit]
                self.assertEqual(actual, ledger)

    def test_stable_after_reordering_and_different_partition_counts(self):
        rows = job.read_export(ROOT / "data/synthetic/c3-responses.csv")
        audit2, _, result2 = self.process(list(reversed(rows)), 2)
        audit5, _, result5 = self.process(rows, 5)
        self.assertEqual(result2, EXPECTED["extended"])
        self.assertEqual(result5, result2)
        self.assertEqual(audit2, audit5)
        self.assertEqual(audit2[13]["rating"], "OK")
        self.assertEqual(audit2[39]["status"], "duplicate")

    def test_invalid_first_is_not_repaired_by_later_valid_duplicate(self):
        rows = [(1, "x", "Gd", ""), (2, "x", "Good", ""), (3, "y", "Poor", "")]
        audit, _, result = self.process(rows)
        self.assertEqual([r["status"] for r in audit], ["invalid_rating", "duplicate", "accepted"])
        self.assertEqual(result["counts"], {"Good": 0, "OK": 0, "Poor": 1})

    def test_exact_ratings_and_missing_ids(self):
        rows = [(1, "", "Good", ""), (2, " ", "OK", ""), (3, "a", "good", ""),
                (4, "b", " Good ", ""), (5, "c", "", ""), (6, "d", "OK", "")]
        audit, _, result = self.process(rows)
        self.assertEqual(result["invalid_id"], 2)
        self.assertEqual(result["invalid_rating"], 3)
        self.assertEqual(result["counts"], {"Good": 0, "OK": 1, "Poor": 0})

    def test_empty_export_and_zero_categories(self):
        _, counts, result = self.process([])
        self.assertEqual(result["input_rows"], 0)
        self.assertEqual(counts, [{"rating": r, "count": 0} for r in job.RATINGS])

    def test_parameter_binding_preserves_quotes_unicode_and_sql_text(self):
        identifier = "r'; DROP TABLE export; -- 问卷"
        audit, _, result = self.process([(1, identifier, "Good", "t'1")])
        self.assertEqual(audit[0]["response_id"], identifier)
        self.assertEqual(audit[0]["submitted_at"], "t'1")
        self.assertEqual(result["counts"], {"Good": 1, "OK": 0, "Poor": 0})

    def test_csv_contract_and_malformed_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.csv"
            for text in ("rating\nGood\n", "response_id,rating,submitted_at\na,Good\n",
                         "response_id,rating,submitted_at\na,Good,t,extra\n",
                         "response_id,rating,rating,submitted_at\na,Good,Good,t\n"):
                path.write_text(text, encoding="utf-8")
                with self.subTest(text=text), self.assertRaises(ValueError):
                    job.read_export(path)
            path.write_text("\ufeffsubmitted_at,rating,response_id\nt,Good,a\n", encoding="utf-8")
            self.assertEqual(job.read_export(path), [(1, "a", "Good", "t")])

    def test_artifacts_are_consistent_and_do_not_change_source(self):
        source = ROOT / "data/synthetic/c3-responses.csv"
        before = source.read_bytes()
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            summary = job.run_job(self.spark, source, out, 4)
            self.assertEqual({k: summary[k] for k in EXPECTED["extended"]}, EXPECTED["extended"])
            with (out / "cleaned.csv").open(newline="", encoding="utf-8") as f:
                clean = list(csv.DictReader(f))
            self.assertEqual(len(clean), 30)
            self.assertEqual(len({row["response_id"] for row in clean}), 30)
            with (out / "audit.csv").open(newline="", encoding="utf-8") as f:
                self.assertEqual(len(list(csv.DictReader(f))), 40)
            self.assertEqual(json.loads((out / "summary.json").read_text()), summary)
            self.assertIn("HashAggregate", (out / "execution-plan.txt").read_text())
        self.assertEqual(source.read_bytes(), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
