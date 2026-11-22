# C-II: data processing - technical working notes

**AI-assisted working material, not a ready-to-submit assessment section.** The
assignment p. 2 prohibits AI-generated submission material. No independent student
authorship, manual execution, signed contribution or lecturer approval is claimed.

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
`data/aggregated/c3/`; these are execution evidence, not a student hand-count claim.

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
- [Reproduction instructions](../../processing/spark/README.md)
- [Evidence index](../../evidence/C3/README.md)
- [Requirement checklist](requirements-checklist.md)

Keep the main C-II prose within the group's combined Part C budget of approximately
800 words; trace tables, full input, code and run evidence belong in appendices.
Do not replace the complete group report, contribution record or rubric with this fragment.
