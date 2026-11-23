# PythonAnywhere (free Beginner tier)

Platform actually adopted for the C2 verification deployment: **PythonAnywhere**.
Alibaba Cloud was not used because new-user student verification is closed;
Google Cloud requires a payment method at sign-up, and the assignment timeline
did not allow waiting for billing verification.

## Platform facts

| Item | Value |
|---|---|
| Plan | Beginner (free), no payment card required |
| Limits | 100 CPU seconds/day, 512 MiB disk, 1 web app, 1 worker |
| Account expiry | One month after signup |
| Public endpoint | https://changxuzhu.pythonanywhere.com |
| Python | 3.10.12 |
| Dependencies | Flask 3.1.3, gunicorn 27.0.1 (from `app/requirements.txt`) |

This is a verification environment. The production design recommended in B1/B2
remains Google Cloud Run.

## Steps

1. Upload the repository zip through **Files** and unzip it into `~/swe309-cloud-survey-main`.
2. Create the virtualenv: `mkvirtualenv --python=/usr/bin/python3.10 survey-env`.
3. Install dependencies: `cd ~/swe309-cloud-survey-main/app && pip install -r requirements.txt`.
4. **Web** -> Add a new web app -> **Manual configuration** (not the Flask template,
   which would create its own entry point) -> Python 3.10.
5. Set Source code and Working directory to `/home/CHANGXUZHU/swe309-cloud-survey-main/app`,
   and Virtualenv to `/home/CHANGXUZHU/.virtualenvs/survey-env`.
6. Replace `/var/www/CHANGXUZHU_pythonanywhere_com_wsgi.py` with the content of
   `wsgi.example` in this folder, filling in the three secret values.
7. Set **Force HTTPS** to Enabled, press **Reload**.
8. Verify: `GET /health`, submit one response, open `/staff/`, reload again and
   confirm the response count is unchanged.

## Configuration

Environment variables are set in the platform WSGI file only, never in the repository.

| Variable | Value |
|---|---|
| `APP_ENV` | `production` |
| `SECRET_KEY` | 64 hex characters from `secrets.token_hex(32)` |
| `STAFF_USERNAME` | staff login name |
| `STAFF_PASSWORD_HASH` | output of `python hash_password.py` (scrypt) |

`DATABASE_PATH`, `LOG_FILE` and `EXPORT_DIR` keep their defaults from
`app/backend/config.py`, which resolve inside the application directory on the
account disk. The Dockerfile default `/tmp/survey.db` is not used in the cloud.

## Verified on 2026-11-23

- Survey form served over HTTPS; HTTP returns `302` to HTTPS.
- Six synthetic responses stored; dashboard count went from 0 to 6.
- Database survived a web-app reload (`app started ... responses=6`).
- Unauthenticated `/staff/` and `/staff/export.csv` return `302` to the login page.
- Invalid rating returns `400 invalid_rating`; login without a CSRF token returns `400`.
- Session cookie carries `Secure`, `HttpOnly`, `SameSite=Lax`.

Evidence: `evidence/C2/README.md`, items E01–E12.

## Known limitations

- One worker: no concurrency and no autoscaling.
- 100 CPU seconds per day: a load test is not possible on this tier.
- No backup, alerting, log rotation or encryption at rest.
- The account and public URL expire one month after signup.
- Storage is SQLite only; `STORAGE_BACKEND=firestore` is a reserved value with no
  implementation behind it.

## Troubleshooting

- `401 Authorization Required` before the application is reached means platform
  password protection is enabled; disable it or respondents cannot open the form.
- A login loop with correct credentials usually means the request used `http://`
  (the session cookie is `Secure`) or the secret key is not fixed in the WSGI file.
- Every change to the WSGI file or environment variables requires **Reload**.
