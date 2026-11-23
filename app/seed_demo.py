"""Fill the local database with synthetic responses spread over recent days,
so the dashboard and charts have something to show in demos.

Usage (from the app/ folder, development only):
    python seed_demo.py              # 14 days, about 15-35 responses per day
    python seed_demo.py --days 30

All data is synthetic. Refuses to run when APP_ENV=production.
"""

import argparse
import random
from datetime import timedelta

from backend.config import load_config
from backend.storage import make_store, now_myt

COMMENTS = [
    None, None, None, "Fast checkout", "Friendly staff", "Delivery was a bit slow",
    "Easy to use website", "Waited too long for support", "Will buy again",
    "Average experience", "Package arrived damaged", "Quick reply from support",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--seed", type=int, default=309, help="random seed (repeatable output)")
    args = parser.parse_args()

    config = load_config()
    if config["APP_ENV"] == "production":
        raise SystemExit("Refusing to seed demo data in production.")
    store = make_store(config)
    store.init_schema()

    rng = random.Random(args.seed)
    today = now_myt().replace(hour=0, minute=0, second=0)
    added = 0
    for back in range(args.days - 1, -1, -1):
        day = today - timedelta(days=back)
        # A campaign day in the middle produces a visible peak.
        n = rng.randint(15, 35) * (3 if back == args.days // 2 else 1)
        weights = (0.55, 0.28, 0.17) if back % 5 else (0.40, 0.32, 0.28)
        for _ in range(n):
            when = day + timedelta(seconds=rng.randint(8 * 3600, 22 * 3600))
            if when > now_myt():
                continue
            rating = rng.choices(("Good", "OK", "Poor"), weights=weights)[0]
            store.add(rating, rng.choice(COMMENTS), submitted=when)
            added += 1
    print(f"Added {added} synthetic responses over {args.days} days to {config['DATABASE_PATH']}")


if __name__ == "__main__":
    main()
