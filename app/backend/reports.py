"""Read the C3 batch result (PySpark rating counts) for the report page.

C3 writes `counts.csv` (rating,count) and, next to it, `summary.json` with the
cleaning totals. The path comes from C3_COUNTS_PATH. In development, if it is
unset, the repository copy under data/aggregated/c3/extended/ is used.
These figures are batch results over an exported file, not live data.
"""

import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .config import APP_DIR
from .logging_setup import LOGGER_NAME
from .storage import MYT
from .validation import RATINGS

log = logging.getLogger(LOGGER_NAME)

REPO_C3_COUNTS = APP_DIR.parent / "data" / "aggregated" / "c3" / "extended" / "counts.csv"


def resolve_c3_path(config):
    if config["C3_COUNTS_PATH"]:
        return Path(config["C3_COUNTS_PATH"])
    if config["APP_ENV"] == "development" and REPO_C3_COUNTS.exists():
        return REPO_C3_COUNTS
    return None


def load_c3_batch(path):
    """Return a dict describing the batch result, or {'error': ...}."""
    if path is None:
        return {"error": "C3_COUNTS_PATH is not set."}
    try:
        with Path(path).open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None or not {"rating", "count"} <= set(reader.fieldnames):
                return {"error": "The C3 file must have the columns rating,count."}
            counts = {r: 0 for r in RATINGS}
            for row in reader:
                if row["rating"] in counts:
                    counts[row["rating"]] = int(row["count"])
    except FileNotFoundError:
        return {"error": f"C3 file not found: {Path(path).name}"}
    except (OSError, ValueError) as exc:
        log.warning("c3 batch unreadable path=%s error=%s", path, exc)
        return {"error": "The C3 file could not be read."}

    result = {
        "counts": counts,
        "total": sum(counts.values()),
        "file": Path(path).name,
        "generated_at": None,
        "cleaning": None,
    }
    summary_path = Path(path).with_name("summary.json")
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            result["cleaning"] = {k: summary.get(k) for k in
                                  ("input_rows", "accepted", "duplicate", "invalid_rating", "invalid_id")}
            stamp = summary.get("generated_at_utc")
            if stamp:
                result["generated_at"] = datetime.fromisoformat(stamp).astimezone(MYT)
        except (OSError, ValueError) as exc:
            log.warning("c3 summary unreadable path=%s error=%s", summary_path, exc)
    if result["generated_at"] is None:
        mtime = Path(path).stat().st_mtime
        result["generated_at"] = datetime.fromtimestamp(mtime, timezone.utc).astimezone(MYT)
    return result


def percentages(counts):
    total = sum(counts.values())
    return {r: (round(100 * counts[r] / total, 1) if total else 0.0) for r in counts}
