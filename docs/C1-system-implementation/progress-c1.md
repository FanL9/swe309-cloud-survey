# C1 input for the progress report (Member 4)

Draft for the group's one-page progress report, due 27 November 2026, 23:59.
About 220 words; the leader can shorten or merge it into the group table.

## Work completed (with evidence)

- **Survey prototype (C-I core, done).** Flask 3.1.3 + SQLite, run locally.
  Accepts only Good, OK or Poor (others return HTTP 400), keeps responses after
  a restart, logs every request and submission, and exports
  `response_id,rating,submitted_at` CSV in the C3 format. The CSV has been
  uploaded to XMDrive. *Evidence:* `evidence/C1/` (10 screenshots, log, database
  dumps); PRs #3–#6.
- **Enhancements (done).** Staff login, ID lookup, filters, dashboard with
  charts, and a printable daily report showing the C3 batch counts separately
  from live data.
- **Deployment readiness (done).** Environment-based configuration, `/health`
  endpoint and a Dockerfile; 67 automated tests and the Docker build pass on
  GitHub Actions for every change.

## Problems encountered

- Cloud Run's disk is temporary, so SQLite data would be lost on restart.
  Storage is isolated in one module; C2 must choose Firestore or a platform
  with a persistent disk.
- No Docker on the local machine: solved by building and testing the image on
  GitHub Actions.

## Next actions

| Action | Owner | Target |
|---|---|---|
| Support the C2 deployment; add a Firestore store if C2 chooses it | Member 4, with Member 5 | 10 Dec |
| Prepare the live demo and a backup screen recording | Member 4 | 20 Dec |
| Final check of the C-I write-up against the deployed version | Member 4 | 22 Dec |
