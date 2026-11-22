# C-II local PySpark rating count

AI-assisted engineering working material; the coursework prohibits AI-generated
submission material (assignment p. 2). This is not a claim of independent student
authorship or a ready-to-submit group report. Review the course rules with the lecturer.

Tested target: Windows, **Python 3.12**, Java 17, PySpark 3.5.7 / Py4J 0.10.9.7,
`local[2]`, four shuffle partitions, adaptive execution disabled for this demo.
No cloud account, Hadoop service, Hive installation or third-party `winutils.exe`
is needed. Install Java from an official distribution (e.g. Eclipse Temurin).
Set `JAVA_HOME` to that installation. Do not commit the runtime or virtual environment.

## Reproduce from the repository root

```powershell
py -3.12 -m venv .venv/c3-runtime
.venv/c3-runtime/Scripts/python.exe -m pip install -r processing/spark/requirements.txt
# If Java is not already configured, set JAVA_HOME to your Java 17 directory.
# This computer also has a checksum-verified portable Temurin in .venv/java/.
.venv/c3-runtime/Scripts/python.exe processing/spark/verify_c3.py
```

The runner executes **both** datasets, verifies the explicit reference totals and
all row dispositions, runs the edge-case tests, and records sanitized real output
under `evidence/C3/`. It exits nonzero if any command/check fails. It overwrites only
the named C3 result/evidence files; input CSVs and other members' files are not changed.
`verification.json` records source hashes and is invalidated before each run so a
failed rerun cannot retain a stale passing result. Windows/PySpark may emit nonfatal
native-Hadoop or socket ResourceWarnings; use exit codes and the checks, not the
absence of warnings, as evidence of success.
Scoped `.gitattributes` preserve C3 text as LF so source/input hashes survive a
Windows checkout, and mark the C3 PDF binary. The synthetic-data attributes name
only the two C3 CSV files; they do not change other members' files.

For a separate export (keep the shell's Java/Python configuration from the runner):

```powershell
$env:PYSPARK_PYTHON = (Resolve-Path .venv/c3-runtime/Scripts/python.exe).Path
.venv/c3-runtime/Scripts/python.exe processing/spark/rating_count.py --input path/to/export.csv --output-dir path/to/new-results --partitions 4
```

CSV needs `response_id,rating,submitted_at` (UTF-8, optional BOM; extra columns are
ignored). These are the existing **provisional**, not team-approved, C1 fields.
No changes to `coordination/interfaces.md` or C1 were made. Missing/extra cells and
duplicate headers fail explicitly; a header-only CSV returns zero for each rating.

The adapter assigns a one-based `source_row` in physical CSV-record order. Spark
`row_number` over each exact response ID keeps the earliest record **before** rating
validation; other occurrences are `duplicate`, including conflicting ratings.
Blank/whitespace-only IDs are `invalid_id`. Only exact `Good`, `OK`, `Poor` pass;
`Gd`, `good`, blank and ` Good ` do not. This does not silently repair data. An invalid
first occurrence is not replaced by a later valid duplicate. The row audit gives
exactly one disposition per input record.

`submitted_at` is preserved, not validated or used to filter dates. Results describe
the **whole supplied export**, not automatically a previous-day report. The C1/C2
caller must supply a consistent, day-scoped export for a daily report. No XMDrive,
Cloud Storage, scheduler, live database or dashboard integration was executed here.

## Result contract (C3 proposal only)

Each output folder contains:

| File | Fields / meaning |
|---|---|
| `counts.csv` | `rating,count`; always Good, OK, Poor, including zeroes |
| `cleaned.csv` | Original three fields; only accepted unique IDs, original order |
| `audit.csv` | `source_row,response_id,rating,submitted_at,id_occurrence,status` |
| `summary.json` | Totals, rules, input SHA-256, UTC run time and observed runtime |
| `execution-plan.txt` | Actual Spark formatted plan, including exchanges and aggregation |

Python reads the small CSV (maximum 10 MiB) to attach stable row order, then uses
parameterized Spark SQL VALUES (CSV values are bound literals, never SQL text). This
avoids the Python-worker socket failures encountered with createDataFrame on this
Windows machine. Spark performs
the window, filtering, shuffles and grouping. Python writes the collected small
results to ordinary CSV so no native Hadoop Windows writer is required. Full input
and audit are on the driver; this is a bounded local implementation, not a scalable
distributed file reader. Do not remove the size guard and call this a cluster pipeline.
For a large export, use a distributed data source with a persistent ingestion ordinal
and distributed output, rather than collecting input or the full audit.

See [trace](../../docs/C3-data-processing/hand-trace.md),
[reference count](../../docs/C3-data-processing/reference-count.md),
[technical notes](../../docs/C3-data-processing/report.md), and
[C3 evidence](../../evidence/C3/README.md).
