# C-I: survey prototype (C1)

## Implementation and results

The prototype is a Flask 3.1.3 web application [1], run locally on Windows with
Python 3.13.2. A respondent chooses Good, OK or Poor on the survey page, or a
client posts JSON to `/api/responses`. The server, not the browser, checks the
rating against exactly those three strings, with no trimming or case folding, so
the rule matches the C-II pipeline. Any other value returns HTTP 400 and is not
stored (Fig. C1-4).

Valid responses are written to a SQLite file through Python's `sqlite3` module
[2], each with a generated response ID and a Malaysia-time timestamp. Because the
data lives in a file rather than in the running process, the three test responses
were still present after the server was stopped and started again (Figs. C1-5 and
C1-6; the startup log reports `responses=3`).

Python's `logging` module [3] records every request with its status code and
duration, each accepted or rejected submission with the reason, and each start
with the stored count. Comments and IP addresses are never logged. The stored
responses are exported as `response_id,rating,submitted_at`, the format C-II
consumes, and the CSV was uploaded manually to XMDrive as the shared copy for the
daily report [4] (Fig. C1-10).

Beyond the brief, authorised staff can sign in, look up a response by its ID,
filter responses, view a live dashboard and print a daily report. The report
shows the C-II batch counts beside the live figures but labels them separately.
Staff passwords are stored only as salted hashes [5].

## Executed and proposed

Executed locally: all of the above, plus 67 automated tests and a Docker image
build and smoke test run by GitHub Actions. Proposed only: cloud hosting, managed
storage in place of SQLite, and an automated export in place of the manual XMDrive
upload (see the deployment plan).

## References

[1] Pallets, "Flask 3.1.3," PyPI. https://pypi.org/project/Flask/3.1.3/ (accessed Nov. 23, 2026).

[2] Python Software Foundation, "sqlite3 — DB-API 2.0 interface for SQLite databases," Python 3.13 Documentation. https://docs.python.org/3.13/library/sqlite3.html (accessed Nov. 23, 2026).

[3] Python Software Foundation, "logging — Logging facility for Python," Python 3.13 Documentation. https://docs.python.org/3.13/library/logging.html (accessed Nov. 23, 2026).

[4] XMUM LINC, "Online Storage." https://linc.xmu.edu.my/online-storage/ (accessed Nov. 18, 2026).

[5] Pallets, "Utilities: werkzeug.security," Werkzeug 3.1.x Documentation. https://werkzeug.palletsprojects.com/en/stable/utils/ (accessed Nov. 23, 2026).
