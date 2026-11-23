# Cloud Deployment Basics

Course:SWE309 - Introduction to Cloud Computing  
Mission:Cloud Deployment  
Status:Deployed and verified on PythonAnywhere free tier (2026-11-23)

## 1. Purpose

This document records the basic concepts required for the cloud deployment task and establishes an initial deployment checklist.

The objective is to understand how the survey application can be hosted, configured, secured, monitored and maintained in a cloud environment.

## 2. Basic Deployment Concepts

| Concept | Explanation | Relevance to the Survey System |
|---|---|---|
| Application | The software that provides the system functions | Accepts and validates survey responses |
| Runtime | The environment required to execute the application | Python version and required libraries |
| Container Image | A packaged application environment | Can package the application and its dependencies |
| Container | A running instance created from an image | Runs the survey application |
| Hosting Service | The platform that runs the application | Provides the environment for the survey system |
| Database | A structured system for storing records | Stores survey responses |
| Object Storage | Storage for files and exported data | Stores CSV exports and reports |
| Port | A network endpoint used by an application | Allows the hosting service to route requests |
| HTTPS | Encrypted communication over HTTP | Protects communication between users and the application |
| Monitoring | Collecting system health and performance information | Helps identify errors and resource usage |

## 3. Proposed Deployment Workflow and Result

The workflow below was executed, not planned. Each step lists its actual outcome.

| Step | Action | Result |
|---|---|---|
| 1 | Upload `swe309-cloud-survey-main.zip` via the Files page and unzip | Extracted to `/home/CHANGXUZHU/swe309-cloud-survey-main` |
| 2 | Confirm runtime | Python 3.10.12; Flask 3.1.3, gunicorn 27.0.1 from `app/requirements.txt` |
| 3 | Create virtualenv | `mkvirtualenv --python=/usr/bin/python3.10 survey-env` |
| 4 | Install dependencies | `pip install -r requirements.txt` succeeded |
| 5 | Create web app | Manual configuration, Python 3.10, not the Flask template |
| 6 | Set source code, working directory, virtualenv | `.../app`, `.../app`, `~/.virtualenvs/survey-env` |
| 7 | Configure WSGI | `/var/www/CHANGXUZHU_pythonanywhere_com_wsgi.py` imports `from wsgi import app as application` |
| 8 | Set environment variables | APP_ENV, SECRET_KEY, STAFF_USERNAME, STAFF_PASSWORD_HASH in the WSGI file only |
| 9 | Enable Force HTTPS and reload | `http://` returns 302 to `https://` |
| 10 | Verify | Survey form served, responses stored, staff area reachable after login |

Two configuration problems were found and fixed during this step:

- The web app had PythonAnywhere password protection enabled, which returned
  `401 Authorization Required` for every request before it reached Flask. It was
  disabled, because it would also block survey respondents.
- The repository's Dockerfile defaults `DATABASE_PATH` to `/tmp/survey.db`, which
  is not persistent. The cloud deployment sets the database path to the account
  disk instead.

## 4. Important Deployment Considerations

### 4.1 Application and Runtime

The hosting environment must support the application's programming language and required dependencies.

The exact runtime version and startup command must be confirmed with the application developer.

### 4.2 Persistent Storage

Application files and persistent data should be considered separately.

The deployment design must ensure that survey responses remain available after an application restart or instance replacement.

### 4.3 Security

The deployment plan should consider:

- HTTPS for encrypted communication.
- Access control for authorised staff.
- Environment variables for application configuration.
- Secret management for credentials and sensitive values.
- Protection of personal data.

Actual credentials and secret values must never be committed to GitHub.

### 4.4 Monitoring

The proposed monitoring approach should consider:

- Application logs.
- Request errors.
- Application availability.
- CPU and memory usage.
- Request latency.
- Resource consumption.

### 4.5 Scaling

The hosting solution should be able to handle changes in the number of incoming requests.

The system should also release unnecessary resources when demand decreases, where the selected platform supports this feature.

## 5. Current Project Status

The application is deployed and publicly reachable at
https://changxuzhu.pythonanywhere.com over HTTPS.

Verified on 2026-11-23:

- The survey form loads and accepts submissions; six synthetic responses were stored.
- The staff dashboard and response list show the stored records after login.
- Invalid ratings are rejected with HTTP 400.
- Unauthenticated requests to `/staff/`, `/staff/responses` and `/staff/export.csv`
  are redirected to the login page (HTTP 302).
- The SQLite file `app/instance/survey.db` persisted across a web-app reload; the
  startup log reports `responses=6` and the row count is unchanged.
- Session cookies carry `Secure`, `HttpOnly` and `SameSite=Lax`.

Evidence for each item is indexed in `evidence/C2/README.md` (E01 to E12).

## 6. Confirmed Application Facts

| Item | Confirmed value |
|---|---|
| Language and framework | Python 3.10.12, Flask 3.1.3 |
| Production server | gunicorn 27.0.1 (not used on PythonAnywhere, which supplies its own WSGI server) |
| Entry point | `app/wsgi.py`, exposing `app` |
| Health check | `GET /health` returns JSON status |
| Persistent data | SQLite at `app/instance/survey.db` on the account disk |
| Logs | `app/logs/app.log`, plus stdout captured by the platform |
| Configuration | Environment variables read in `app/backend/config.py` |
| Secrets | `SECRET_KEY` and `STAFF_PASSWORD_HASH` set only in the WSGI file, never committed |

## 7. Limitations and Remaining Work

- The free tier allows 100 CPU seconds per day, 512 MiB disk and one worker. It is a
  verification environment, not a production platform.
- No load test was performed; peak behaviour is design-only and derived from the
  B2 assumptions (see `c2-e12-peak-design.md`).
- No automated backup, alerting or log aggregation is configured.
- The storage layer implements SQLite only; `STORAGE_BACKEND=firestore` is a
  reserved value with no implementation behind it.
- The production design recommended in B1/B2 remains Google Cloud Run with a
  managed database; that deployment was not executed within this assignment.
- The free account expires one month after signup, so the public URL is temporary.
