"""Response storage.

Routes only talk to a ResponseStore, never to SQLite directly. The local
prototype uses SQLiteResponseStore; a cloud store (e.g. Firestore, as B1
recommends) can be added as another class with the same methods without
touching the routes.
"""

import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .validation import RATINGS

# Malaysia has no daylight saving, so a fixed offset is exact and avoids
# depending on tzdata being installed (it is not on Windows by default).
MYT = timezone(timedelta(hours=8), "MYT")

_ID_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no 0/O, 1/I: easy to read aloud

SCHEMA_VERSION = 1
SCHEMA = """
CREATE TABLE IF NOT EXISTS responses (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    response_id  TEXT    NOT NULL UNIQUE,
    rating       TEXT    NOT NULL CHECK (rating IN ('Good', 'OK', 'Poor')),
    comment      TEXT,
    submitted_at TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_responses_submitted_at ON responses (submitted_at);
CREATE INDEX IF NOT EXISTS idx_responses_rating ON responses (rating);
"""


def now_myt():
    return datetime.now(MYT).replace(microsecond=0)


def new_response_id(when):
    suffix = "".join(secrets.choice(_ID_ALPHABET) for _ in range(6))
    return f"R{when:%Y%m%d}-{suffix}"


class SQLiteResponseStore:
    def __init__(self, path):
        self.path = Path(path)

    def _connect(self):
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(SCHEMA)
            conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        conn.close()

    def add(self, rating, comment=None, submitted=None):
        """Insert one response and return it as a dict.

        `submitted` is only for seeding demo data; real submissions use now.
        """
        submitted = submitted or now_myt()
        conn = self._connect()
        try:
            for _ in range(5):  # retry on the (very unlikely) ID collision
                response_id = new_response_id(submitted)
                try:
                    with conn:
                        conn.execute(
                            "INSERT INTO responses (response_id, rating, comment, submitted_at)"
                            " VALUES (?, ?, ?, ?)",
                            (response_id, rating, comment, submitted.isoformat()),
                        )
                    return {
                        "response_id": response_id,
                        "rating": rating,
                        "comment": comment,
                        "submitted_at": submitted.isoformat(),
                    }
                except sqlite3.IntegrityError as exc:
                    if "response_id" not in str(exc):
                        raise
            raise RuntimeError("could not generate a unique response_id")
        finally:
            conn.close()

    def get(self, response_id):
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT response_id, rating, comment, submitted_at FROM responses"
                " WHERE response_id = ?",
                (response_id,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def list_all(self):
        """All responses, oldest first."""
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT response_id, rating, comment, submitted_at FROM responses ORDER BY id"
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def search(self, rating=None, date_from=None, date_to=None, id_contains=None,
               limit=20, offset=0):
        """Filtered page of responses, newest first. Returns (rows, total).

        Dates are 'YYYY-MM-DD' strings compared against the Malaysia-time date
        part of submitted_at; both ends are inclusive.
        """
        where, params = [], []
        if rating:
            where.append("rating = ?")
            params.append(rating)
        if date_from:
            where.append("substr(submitted_at, 1, 10) >= ?")
            params.append(date_from)
        if date_to:
            where.append("substr(submitted_at, 1, 10) <= ?")
            params.append(date_to)
        if id_contains:
            escaped = id_contains.upper().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            where.append("response_id LIKE ? ESCAPE '\\'")
            params.append(f"%{escaped}%")
        clause = (" WHERE " + " AND ".join(where)) if where else ""

        conn = self._connect()
        try:
            total = conn.execute(f"SELECT COUNT(*) FROM responses{clause}", params).fetchone()[0]
            rows = conn.execute(
                "SELECT response_id, rating, comment, submitted_at FROM responses"
                f"{clause} ORDER BY submitted_at DESC, id DESC LIMIT ? OFFSET ?",
                [*params, limit, offset],
            ).fetchall()
            return [dict(r) for r in rows], total
        finally:
            conn.close()

    def rating_counts(self, date_from=None, date_to=None):
        """{'Good': n, 'OK': n, 'Poor': n} for an optional inclusive date range."""
        where, params = [], []
        if date_from:
            where.append("substr(submitted_at, 1, 10) >= ?")
            params.append(date_from)
        if date_to:
            where.append("substr(submitted_at, 1, 10) <= ?")
            params.append(date_to)
        clause = (" WHERE " + " AND ".join(where)) if where else ""
        conn = self._connect()
        try:
            rows = conn.execute(
                f"SELECT rating, COUNT(*) AS n FROM responses{clause} GROUP BY rating", params
            ).fetchall()
        finally:
            conn.close()
        counts = {r: 0 for r in RATINGS}
        counts.update({row["rating"]: row["n"] for row in rows})
        return counts

    def daily_counts(self, date_from, date_to):
        """One entry per day in [date_from, date_to] (dates), zero-filled."""
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT substr(submitted_at, 1, 10) AS day, rating, COUNT(*) AS n FROM responses"
                " WHERE substr(submitted_at, 1, 10) BETWEEN ? AND ?"
                " GROUP BY day, rating",
                (date_from.isoformat(), date_to.isoformat()),
            ).fetchall()
        finally:
            conn.close()
        found = {}
        for row in rows:
            found.setdefault(row["day"], {})[row["rating"]] = row["n"]
        days = []
        day = date_from
        while day <= date_to:
            key = day.isoformat()
            entry = {"day": key, **{r: found.get(key, {}).get(r, 0) for r in RATINGS}}
            entry["total"] = sum(entry[r] for r in RATINGS)
            days.append(entry)
            day += timedelta(days=1)
        return days

    def count(self):
        conn = self._connect()
        try:
            return conn.execute("SELECT COUNT(*) FROM responses").fetchone()[0]
        finally:
            conn.close()

    def ping(self):
        conn = self._connect()
        try:
            conn.execute("SELECT 1").fetchone()
        finally:
            conn.close()


def make_store(config):
    backend = config["STORAGE_BACKEND"]
    if backend == "sqlite":
        return SQLiteResponseStore(config["DATABASE_PATH"])
    raise ValueError(f"Unsupported STORAGE_BACKEND: {backend!r} (only 'sqlite' is implemented)")
