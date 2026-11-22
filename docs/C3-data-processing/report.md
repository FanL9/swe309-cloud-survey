# C-II: data processing

Member3 has confirmed manual review of the report content.

## Results and interpretation

The Table 2 reference trace excludes the second r07 and the illegal rating Gd.
After global ID deduplication, the rating-map stage emits ten pairs; shuffle groups
five ones under Good, three under OK and two under Poor. Reduction gives 5/3/2,
summing to ten. The full trace and exclusions appear in `hand-trace.md`.

The extended export preserves those twelve input records and adds twenty-eight,
including repeated IDs and invalid spellings. Its explicit reference ledger expects
30 accepted responses: Good 12, OK 10 and Poor 8. Five duplicates and five illegal
ratings account for the other ten records. The pipeline retains the first CSV record
for each exact ID before validation, so r13's later Poor cannot replace its earlier
OK. It never converts Gd or good into Good. Audit rows retain the source ordinal and
exclusion reason; malformed CSV structure fails rather than silently dropping fields.

PySpark uses ordered `row_number` windows for IDs and `groupBy("rating").count()`
for accepted records [1]. An explicit ledger, rather than the aggregation program
itself, supplies expected row outcomes and totals. The reproduction runner verifies
both datasets, every row disposition, conservation, unique cleaned IDs and edge cases.
Machine-readable run results and actual execution plans are in `evidence/C3/` and
`data/aggregated/c3/`.

A partition is a logical unit of parallel work, not a separate computer. This demo
repartitions input into four parts and sets four shuffle partitions, with adaptive
coalescing disabled. ID windows move equal IDs together; the later rating aggregation
groups equal ratings [2,3]. Tests change partition counts and reverse input delivery
after attaching source ordinals. Stable results require an explicit ID tie-breaker;
arbitrary `dropDuplicates` does not define the conflicting record to retain.

Spark's DAG execution and reusable cached intermediates reduce repeated disk
materialisation between jobs, especially for iterative or interactive workloads
[2,4]. SQL/DataFrame APIs simplify multi-stage pipelines. This explains its broad
replacement of chained Hadoop MapReduce analytics; it does not make Spark faster
for every one-pass count, eliminate shuffle/spill, or replace Hadoop storage.

`local[2]` runs two task threads on one Windows machine, sharing its CPU, memory and
disk [5]. It demonstrates Spark semantics, not multi-node speedup or host-failure
resilience. The local adapter reads the bounded input on the driver and collects
the audit; that is another scalability limit. At 500 responses of approximately
1 KB daily, Company A produces about 0.5 MB/day and 547.5 MB over 1,095 days
(decimal units, excluding indexes, backups and leap days). Even a conservative
30,000 submissions in a ten-minute 50-request/s peak would be about 30 MB.
These estimates do not justify a distributed batch cluster; a SQL aggregate or
small scheduled local job is more proportionate. This is a workload inference,
not a measured throughput claim.

## Reflection and integration boundary

The first actual run failed with a Python 3.13 Windows worker socket error
(`WinError 10038`). Switching to Python 3.12 alone did not fix it. The successful route binds the
small CSV as parameterized Spark SQL VALUES, avoiding Python-worker ingestion;
all cleaning and aggregation still execute in Spark. The tested interpreter is
Python 3.12, with Java 17 and pinned PySpark dependencies.
The remaining prototype limitation is bounded driver-side CSV ingestion and audit
collection. A proposed improvement is persistent ingestion ordinals plus distributed
input/output if measured volume demands it. No multi-node experiment, cloud deployment,
daily scheduler or C1 database integration was executed.

The three-column C1 interface remains provisional and unchanged. The job counts the
complete supplied CSV; it does not filter timestamps. C1/C2 must provide a consistent
day-scoped export before this can be called an operational daily report. The local
PySpark 3.5.7 pin matches Member2's B-II proposed version; Member2's text is preserved.
This C-II fragment does not claim C-I validation, persistence, logs or XMDrive evidence.

## Evidence and scope

- [Exact Table 2 map/shuffle/reduce trace](hand-trace.md)
- [Extended reference arithmetic](reference-count.md)
- [Official source register](sources.md) ([1]-[5], checked 22 November 2026)
- [Reproduction instructions](#reproduction-and-result-contract)
- [Evidence index](#execution-evidence)
- [Requirement checklist](requirements-checklist.md)

Keep the main C-II prose within the group's combined Part C budget of approximately
800 words; trace tables, full input, code and run evidence belong in appendices.
Do not replace the complete group report, contribution record or rubric with this fragment.

## Reproduction and result contract

Tested target: Windows, **Python 3.12**, Java 17, PySpark 3.5.7 / Py4J 0.10.9.7,
`local[2]`, four shuffle partitions, adaptive execution disabled for this demo.
No cloud account, Hadoop service, Hive installation or third-party `winutils.exe`
is needed. Install Java from an official distribution (e.g. Eclipse Temurin).
Set `JAVA_HOME` to that installation. Do not commit the runtime or virtual environment.

### Reproduce from the repository root

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

### Result contract (C3 proposal only)

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

## Test coverage

Eight real-Spark tests cover reference totals and every row disposition, Table 2 prefix preservation, partition/order invariance (2, 4 and 5 partitions), conflicting duplicates, invalid-first deduplication, strict ratings and missing IDs, empty input, malformed/BOM CSV, SQL parameter binding, output consistency and unchanged source bytes. Expected fixtures are separate from the Spark implementation.

To run the tests alone after configuring Java and Python as above:

```powershell
.venv/c3-runtime/Scripts/python.exe -m unittest discover -s tests/processing -v
```

## Execution evidence

| Evidence | Location |
|---|---|
| Original Table 2 ID/rating records with synthetic timestamps | `data/synthetic/c3-table2.csv` |
| 40-record extension, including 30 accepted unique IDs | `data/synthetic/c3-responses.csv` |
| Explicit trace and extended reference count | `docs/C3-data-processing/hand-trace.md`, `reference-count.md` |
| Per-row expected decisions and totals | `tests/processing/expected-ledger.csv`, `expected-counts.json` |
| Actual program, pinned dependency file, reproduction runner | `processing/spark/` |
| Actual counts, cleaned CSV, row audit, runtime, execution plan | `data/aggregated/c3/table2/` and `extended/` |
| Actual sanitized command output and edge-test results | [run.txt](../../evidence/C3/run.txt) |
| Automated comparisons and observed versions | [verification.json](../../evidence/C3/verification.json) |
| Upstream revision and protected-file check | [sync-check.json](../../evidence/C3/sync-check.json) |
| PDF report and its builder | `docs/C3-data-processing/c3-working-notes.pdf`, `build_notes.py` |

Paths in the table are repository-relative. The CSVs and text records are primary
evidence, not synthetic terminal screenshots. To reproduce: run
`.venv/c3-runtime/Scripts/python.exe processing/spark/verify_c3.py` from the repository root.
Runtime binaries and failed-run raw output stay under ignored `.venv/`.

Windows Python-worker ingestion failed (WinError 10038 was observed on Python
3.13); switching to 3.12 alone also failed. Parameterized SQL VALUES ingestion
avoids those workers. Python 3.12 is the tested successful route. Nonfatal Hadoop-native/winutils warnings do not establish a Hadoop
installation and are retained in the actual transcript. This job does not use native
Hadoop output writers. No external winutils binary was downloaded.

Do not substitute this C-II packet for the complete 2,250-2,750-word group report,
signed contribution record or marking rubric. C-I prototype/XMDrive/cloud evidence
belongs to C1/C2 and was not modified or marked complete by this work.

## PDF build

The PDF contains results, the Table 2 trace, the complete row audit, runtime evidence, references and the executed program appendix. After successful verification:

```powershell
.venv/c3-runtime/Scripts/python.exe -m pip install reportlab==4.4.9
.venv/c3-runtime/Scripts/python.exe docs/C3-data-processing/build_notes.py
```

[Open the C-II PDF report](c3-working-notes.pdf).
