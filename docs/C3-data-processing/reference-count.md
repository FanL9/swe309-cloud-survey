# C-II / Extended-data reference count

This is explicit reference arithmetic prepared independently of the Spark algorithm.

`data/synthetic/c3-responses.csv` starts with the exact 12 Table 2 ID/rating records
and appends 28 fictional records: **40 total, 35 distinct IDs, 30 accepted unique
responses**. This satisfies either a 30-input-record or a 30-valid-response reading.
All timestamps are fictional, on 22 November 2026 in UTC+08:00. No real respondents
or personal data are used. Do not combine the Table 2 and extended CSVs as two
independent daily exports; one is the prefix of the other.

| Rating | Accepted response IDs | Count |
|---|---|---:|
| Good | r01, r03, r06, r08, r10, r12, r15, r18, r21, r24, r27, r30 | 12 |
| OK | r04, r05, r09, r13, r16, r19, r22, r25, r28, r31 | 10 |
| Poor | r02, r07, r14, r17, r20, r23, r26, r29 | 8 |

The twenty new accepted IDs r12-r31 contribute **7 Good + 7 OK + 6 Poor**.
Adding Table 2's 5/3/2 gives **12/10/8**, total **30**.

| CSV record | ID | Value | Exclusion |
|---:|---|---|---|
| 10 | r07 | Poor | Duplicate of record 7 |
| 12 | r11 | Gd | Illegal exact value |
| 33 | r12 | Good | Duplicate of record 13 |
| 34 | r15 | Good | Duplicate of record 16 |
| 35 | r20 | Poor | Duplicate of record 21 |
| 36 | r32 | Excellent | Illegal exact value |
| 37 | r33 | good | Wrong case |
| 38 | r34 | empty string | Missing rating |
| 39 | r35 | ` Good ` | Whitespace makes this a different exact value |
| 40 | r13 | Poor | Conflicting duplicate of record 14 (OK); first record wins |

**40 = 5 duplicates + 5 illegal ratings + 30 accepted**, with no missing IDs in
this fixture. Reference and implementation use the same declared rule; this is a
policy choice, not proof that the first record always represents the true response.
The independent ledger `tests/processing/expected-ledger.csv` states a disposition
for every input record. `verify_c3.py` checks every ID/rating/status against actual
Spark output in addition to checking category totals, input-prefix preservation,
cleaned-ID uniqueness and row conservation. Tests also cover invalid-first/valid-later
duplicates, all-zero output, empty IDs, malformed CSV and different partition counts.
