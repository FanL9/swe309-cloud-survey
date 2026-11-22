# C-II data-processing verification

From the repository root, after installing the pinned runtime:

```powershell
.venv/c3-runtime/Scripts/python.exe processing/spark/verify_c3.py
```

`expected-counts.json` and `expected-ledger.csv` are explicit fixtures independent of
the Spark implementation. These are AI-assisted reference arithmetic, not proof of a
student's own hand calculation. Full totals and every row outcome are compared.

Eight tests cover the two reference datasets and prefix preservation, partition/order
invariance (2 and 5 vs the normal 4), conflicting IDs, invalid-first deduplication,
strict values/missing IDs, empty input/zero categories, malformed/reordered/BOM CSV,
SQL parameter binding for quotes/Unicode, real output files and preservation of input bytes. All tests use real local Spark;
no mock replaces cleaning or aggregation. See `evidence/C3/run.txt` for the actual result.

Run tests alone after setting `JAVA_HOME`, `PYSPARK_PYTHON` and `SPARK_HOME` as in the
Python runner: `.venv/c3-runtime/Scripts/python.exe -m unittest discover -s tests/processing -v`.
