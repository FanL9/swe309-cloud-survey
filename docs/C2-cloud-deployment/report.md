## Part C-I — Cloud deployment (C2)

### 1. Platform and eligibility

The service was verified on PythonAnywhere's free Beginner tier, selected because registration requires no payment card and a public HTTPS endpoint at https://changxuzhu.pythonanywhere.com was available the same day. The tier allows 100 CPU seconds per day, 512 MiB of disk, one web app and one worker, so it is used as a verification environment while Cloud Run remains the production recommendation from B1.

### 2. Configuration

The web app uses manual configuration, keeping the repository's wsgi.py as the entry point, with dependencies installed in a Python 3.10 virtual environment. Force HTTPS returns 302 to the encrypted endpoint. SQLite is stored on the account disk at app/instance/survey.db; the dashboard count moved from 0 to 6 responses, including repeated test submissions, and after a reload the log records `app started ... responses=6`. SECRET_KEY and the staff scrypt hash are set only in the platform WSGI file, while the repository contains only an empty .env.example.

### 3. Peak handling

The B2 model assumes 50 req/s for 600 s, that is 30,000 requests, which at 0.5 s per request requires about 25 concurrent requests; four Cloud Run instances at concurrency 20 provide 80 slots, with 5 database connections each giving 20 in total. This is a design calculation only: the free tier's single worker and 100 CPU seconds per day cannot absorb even a few hundred requests, so peak handling is valid on Cloud Run, not on this deployment.

### 4. Problems, fixes and limits

Three issues were encountered. Platform password protection returned 401 before requests reached Flask and was disabled; the Dockerfile's /tmp database path was replaced with persistent storage; and a login POST without a CSRF token returned 400, confirming the protection works. Authorisation was verified by an incognito request to /staff/export.csv returning 302 with no file, and validation by an out-of-range rating `Excellent` returning `400 invalid_rating`. No load test, backup, alerting, encryption at rest or autoscaling exists, and the account expires after one month.

### Demonstrated versus design only

| Feature | Demonstrated in cloud | Design only |
|---|---|---|
| HTTPS with HTTP-to-HTTPS redirect | Yes (302 verified) | — |
| Persistent storage across restart | Yes (6 rows unchanged) | — |
| Staff authentication and CSRF | Yes (302 / 400 verified) | — |
| Request and audit logging | Yes (app.log) | — |
| Alerting, backup, log rotation | — | Yes |
| Autoscaling and peak capacity | — | Yes (Cloud Run) |
| Encryption at rest | — | Yes |

Evidence: E01–E12 in `evidence/C2/README.md`.
