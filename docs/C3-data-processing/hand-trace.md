# C-II / Table 2 reference hand trace

## Original records and exclusions

The assignment p. 9 Table 2 contains exactly **12 records**, in three conceptual
input splits. `data/synthetic/c3-table2.csv` preserves every ID/rating and the order;
its timestamps are added fictional metadata, not timestamps provided in Table 2.

| Split | CSV record numbers | Original records | Exclusions before rating map |
|---|---|---|---|
| 1 | 1-4 | r01 Good; r02 Poor; r03 Good; r04 OK | None |
| 2 | 5-8 | r05 OK; r06 Good; r07 Poor; r08 Good | None |
| 3 | 9-12 | r09 OK; r07 Poor; r10 Good; r11 Gd | Record 10: duplicate r07 (first at 7); record 12: Gd is not an allowed rating |

Deduplicate **globally by response ID**, retaining the earliest CSV record, then
validate its rating. Per-split deduplication alone would miss the r07 duplicate
across splits 2 and 3. In a distributed implementation this ID step itself needs a
keyed shuffle before the subsequent rating-count stage. A duplicate is not another
survey response, and Gd must not be guessed to mean Good.

## Map output after cleaning

| Split | Emitted pairs (in original order) |
|---|---|
| 1 | (Good,1), (Poor,1), (Good,1), (OK,1) |
| 2 | (OK,1), (Good,1), (Poor,1), (Good,1) |
| 3 | (OK,1), (Good,1) |

Exactly 10 pairs are emitted; excluded records emit no pair. The count job is
conceptual MapReduce. The actual PySpark code uses a window and DataFrame aggregation,
not three literal map/reduce processes corresponding to this printed table.

## Shuffle groups and reduce output

| Key | Values grouped after shuffle | Sum / final reduce pair |
|---|---|---|
| Good | [1,1,1,1,1] | (Good,5) |
| OK | [1,1,1] | (OK,3) |
| Poor | [1,1] | (Poor,2) |

Conservation: **12 input = 1 duplicate + 1 illegal rating + 10 accepted**.
The reduce total is **5 + 3 + 2 = 10**, and the ten retained IDs are r01-r10.
If r07 were counted twice, Poor would incorrectly become 3 and the total 11.

The three printed input splits are logical units of input work. They are neither
GFS chunks nor the four Spark partitions configured in the local experiment.
