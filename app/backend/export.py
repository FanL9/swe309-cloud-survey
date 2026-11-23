"""CSV export in the format agreed with C3: response_id,rating,submitted_at."""

import csv
import io
from pathlib import Path

EXPORT_FIELDS = ("response_id", "rating", "submitted_at")


def export_text(store):
    """All stored responses as CSV text (used by the staff download)."""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=EXPORT_FIELDS, extrasaction="ignore",
                            lineterminator="\n")
    writer.writeheader()
    rows = store.list_all()
    writer.writerows(rows)
    return buffer.getvalue(), len(rows)


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
