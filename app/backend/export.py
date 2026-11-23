"""CSV export in the format agreed with C3: response_id,rating,submitted_at."""

import csv
from pathlib import Path

EXPORT_FIELDS = ("response_id", "rating", "submitted_at")


def write_export(store, path):
    """Write all stored responses to `path`; return the number of rows."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = store.list_all()
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=EXPORT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)
