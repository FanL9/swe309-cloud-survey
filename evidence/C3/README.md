# C-II evidence index

These are AI-assisted technical working materials. The assignment p. 2 prohibits
AI-generated submissions. No student manual execution, independent authorship,
cloud deployment, screenshot, signature or approval is fabricated.

| Evidence | Location |
|---|---|
| Original Table 2 ID/rating records with synthetic timestamps | `data/synthetic/c3-table2.csv` |
| 40-record extension, including 30 accepted unique IDs | `data/synthetic/c3-responses.csv` |
| Explicit trace and extended reference count | `docs/C3-data-processing/hand-trace.md`, `reference-count.md` |
| Per-row expected decisions and totals | `tests/processing/expected-ledger.csv`, `expected-counts.json` |
| Actual program, pinned dependency file, reproduction runner | `processing/spark/` |
| Actual counts, cleaned CSV, row audit, runtime, execution plan | `data/aggregated/c3/table2/` and `extended/` |
| Actual sanitized command output and edge-test results | [run.txt](run.txt) |
| Automated comparisons and observed versions | [verification.json](verification.json) |
| Upstream revision and protected-file check | [sync-check.json](sync-check.json) |
| Readable PDF working packet and its builder | `docs/C3-data-processing/c3-working-notes.pdf`, `build_notes.py` |

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
