# C2 peak-load design (design only)

No load test was run: the PythonAnywhere free tier allows 100 CPU seconds per day,
so a 10-minute stress test would exceed the daily quota. The numbers below are
derived from the B2 architecture assumptions, not measured.

| Item | Value | Source |
|------|-------|--------|
| Peak arrival rate | 50 req/s for 600 s = 30,000 requests | B2 assumption |
| Mean service time | 0.5 s per request | B2 assumption |
| Required concurrency | 50 x 0.5 = 25 | Little's law |
| Cloud Run capacity | 4 instances x concurrency 20 = 80 | B2 |
| DB connections | 5 per instance x 4 = 20 | B2, within Cloud SQL limit |
| PythonAnywhere free tier | 1 worker, 100 CPU s/day | PA free plan |
| Verdict | Free tier cannot absorb the peak; production design stays on Cloud Run | derived |
