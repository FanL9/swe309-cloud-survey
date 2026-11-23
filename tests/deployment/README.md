# Deployment tests (C2)

Checks executed against the live PythonAnywhere deployment on 2026-11-23.
Evidence files are stored in `evidence/C2/`.

| ID | Test | Expected | Actual | Evidence |
|----|------|----------|--------|----------|
| DT-01 | `GET https://changxuzhu.pythonanywhere.com/` | 200 with survey form | 200, form rendered | E02 |
| DT-02 | `GET http://.../` | Redirect to HTTPS | `302` with `Location: https://...` | E07 |
| DT-03 | Submit a valid response via the form | Stored, redirect to thank-you page | Stored; dashboard count increased | E03 |
| DT-04 | `POST /api/responses` with rating `Excellent` | Rejected | `400 invalid_rating` | E04 |
| DT-05 | Reload the web app, then query the row count | Same count as before | `app started ... responses=6`; 6 before and after | E05 |
| DT-06 | Incognito `GET /staff/` | Redirect to login | `302` to `/staff/login` | E06 |
| DT-07 | Incognito `GET /staff/export.csv` | No file, redirect to login | `302`, no download | E06 |
| DT-08 | Inspect the session cookie | `Secure`, `HttpOnly`, `SameSite=Lax` | All three present | E07 |
| DT-09 | Inspect `app.log` after the tests above | method, path, status, duration; no comments or IPs | As expected | E08 |
| DT-10 | Login POST without a valid CSRF token | Rejected | `400` | E11 |
| DT-11 | `grep -rn "scrypt:"` across the repository | No match | No output; only `.env.example` exists | E10 |

## Not executed (design only)

- Peak-load test: the free tier allows 100 CPU seconds per day.
- Backup and restore drill.
- Alert delivery.
- Autoscaling behaviour.
- Encryption at rest.

Each excluded item must be described as "design only" in the report.

