# C2 证据
实际云部署、HTTPS、云端持久化、权限、日志监控和功能验证；隐藏账户标识及凭据。

## Evidence index (C2, PythonAnywhere deployment, 2026-11-23)

| ID | File | Type | What it proves |
|----|------|------|----------------|
| E01 | c2-e01-pa-free-plan.png | screenshot | Free tier requires no payment card: 100 CPU s/day, 512 MiB disk, 1 web app / 1 worker |
| E01 | c2-e01-pa-account.png | screenshot | Account plan is Beginner (free) |
| E02 | c2-e02-survey-home.png | screenshot | Public HTTPS endpoint serves the survey form |
| E03 | c2-e03-dashboard.png | screenshot | Responses submitted in the cloud appear in the staff dashboard |
| E03 | c2-e03-responses.png | screenshot | Six stored responses with IDs listed in the staff area |
| E04 | c2-e04-invalid-rating.txt | command output | Rating outside Good/OK/Poor is rejected with HTTP 400 |
| E05 | c2-e05-persist.txt | command output | SQLite file on disk; count = 6 before and after web-app reload |
| E06 | c2-e06-staff-redirect.png | screenshot | Unauthenticated /staff/ redirects to the login page |
| E07 | c2-e07-https-cookie.txt | command output | HTTP redirects to HTTPS; session cookie is Secure, HttpOnly, SameSite=Lax |
| E08 | c2-e08-app-log.txt | log excerpt | Request/audit logging: method, path, status, duration, staff actions; no comments or IPs |
| E09 | c2-e09-quota.png | screenshot | CPU seconds used today against the 100 s/day free quota |
| E10 | c2-e10-secret-check.txt | command output | No scrypt hash in the repository; only .env.example exists |
| E11 | c2-e11-csrf.txt | command output | Login POST without a valid CSRF token returns HTTP 400 |
| E12 | c2-e12-peak-design.md | design note | Peak arithmetic derived from B2 assumptions; design only, not measured |

Notes:
- All data is synthetic. No real respondent data, passwords or keys are included.
- E01 to E11 were produced on the live deployment; E12 is a design calculation.
- The PythonAnywhere deployment is the verification environment. The production
  design referenced in B1/B2 remains Google Cloud Run.
