"""Export stored responses to CSV for the daily report / XMDrive upload.

Usage (from the app/ folder):
    python export_csv.py                  # -> instance/exports/responses-<timestamp>.csv
    python export_csv.py --out my.csv     # -> my.csv
"""

import argparse
import logging
from pathlib import Path

from backend.config import load_config
from backend.export import write_export
from backend.logging_setup import LOGGER_NAME, setup_logging
from backend.storage import make_store, now_myt


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", help="output CSV path")
    args = parser.parse_args()

    config = load_config()
    setup_logging(config)
    log = logging.getLogger(LOGGER_NAME)
    store = make_store(config)
    store.init_schema()

    out = Path(args.out) if args.out else (
        Path(config["EXPORT_DIR"]) / f"responses-{now_myt():%Y%m%d-%H%M%S}.csv"
    )
    rows = write_export(store, out)
    log.info("export written rows=%d path=%s", rows, out)
    print(f"Exported {rows} responses to {out.resolve()}")


if __name__ == "__main__":
    main()
