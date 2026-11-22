# C-II requirement-to-evidence checklist

Scope: assignment p. 9 C-II and p. 14 data-processing rubric. This is a technical
working package; the course's ban on AI-generated submissions prevents claiming it
as independently authored submission material or claiming a student's hand execution.

| Requirement | Evidence | Boundary |
|---|---|---|
| Table 2 exclusions and reasons | `hand-trace.md`, Table 2 audit CSV | All 12 original ID/rating pairs preserved |
| Map pairs, shuffle groups, reduce totals | `hand-trace.md` | Reference arithmetic, to be independently checked by Member3 |
| Extend Table 2 to >=30 synthetic responses | `data/synthetic/c3-responses.csv` | 40 input records, 30 accepted unique IDs |
| Duplicates and invalid ratings handled | Full `audit.csv`, expected ledger, tests | Deterministic first occurrence; no correction guesses |
| Real PySpark local or lab Hive | `rating_count.py`, `run.txt`, `verification.json` | PySpark chosen; Hive is not claimed or required |
| Code, input, output | Spark code, two input CSVs, both result directories | Real outputs, not screenshots fabricated from expected numbers |
| Check against manual count | Reference count, explicit ledger, automated comparison | Reference is supplied; student manual verification is still required |
| Partitions | `report.md`, execution plans and 2/4/5 partition tests | Four logical partitions do not mean four machines |
| Spark vs Hadoop MapReduce | `report.md`, sources [2]-[4], [7] | No universal speedup assertion |
| Single-machine limitations | `report.md`, runtime master `local[2]` | No distributed performance/failover claim |
| Company A's actual scale | Table 1 arithmetic in `report.md` | Estimates, not a 50 requests/s load test |
| Short reflection | `report.md` | Actual environment problem, limitation and proposed improvement |
| Other members' current work preserved | `evidence/C3/sync-check.json` | Protected tracked files checked against fetched upstream/main |
| Group report format, signatures, rubric | Existing team integration responsibility | C3 does not replace, sign or alter those files |
