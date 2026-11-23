import json
from datetime import timedelta

import pytest

from backend import create_app
from backend.reports import load_c3_batch, percentages
from backend.storage import now_myt
from test_staff import _login


def _store(app):
    return app.extensions["response_store"]


def _at(days_ago, hour=12):
    return (now_myt() - timedelta(days=days_ago)).replace(hour=hour, minute=0, second=0)


# --- storage aggregates --------------------------------------------------------------

def test_rating_counts_all_and_by_day(app):
    s = _store(app)
    for r, d in [("Good", 0), ("Good", 0), ("Poor", 0), ("OK", 1), ("Good", 3)]:
        s.add(r, submitted=_at(d))
    assert s.rating_counts() == {"Good": 3, "OK": 1, "Poor": 1}
    today = _at(0).date().isoformat()
    assert s.rating_counts(today, today) == {"Good": 2, "OK": 0, "Poor": 1}


def test_daily_counts_zero_fills_missing_days(app):
    s = _store(app)
    s.add("Good", submitted=_at(0))
    s.add("Poor", submitted=_at(2))
    days = s.daily_counts(_at(3).date(), _at(0).date())
    assert [d["day"] for d in days] == [_at(n).date().isoformat() for n in (3, 2, 1, 0)]
    assert [d["total"] for d in days] == [0, 1, 0, 1]
    assert days[1]["Poor"] == 1 and days[3]["Good"] == 1


def test_percentages():
    assert percentages({"Good": 1, "OK": 1, "Poor": 2}) == {"Good": 25.0, "OK": 25.0, "Poor": 50.0}
    assert percentages({"Good": 0, "OK": 0, "Poor": 0}) == {"Good": 0.0, "OK": 0.0, "Poor": 0.0}


# --- C3 batch reader -------------------------------------------------------------------

def test_load_c3_batch_with_summary(tmp_path):
    (tmp_path / "counts.csv").write_text("rating,count\nGood,12\nOK,10\nPoor,8\n", encoding="utf-8")
    (tmp_path / "summary.json").write_text(json.dumps({
        "input_rows": 40, "accepted": 30, "duplicate": 5, "invalid_rating": 5, "invalid_id": 0,
        "generated_at_utc": "2026-11-22T07:35:53+00:00",
    }), encoding="utf-8")
    batch = load_c3_batch(tmp_path / "counts.csv")
    assert batch["counts"] == {"Good": 12, "OK": 10, "Poor": 8}
    assert batch["total"] == 30
    assert batch["cleaning"]["duplicate"] == 5
    assert batch["generated_at"].strftime("%Y-%m-%d %H:%M") == "2026-11-22 15:35"  # MYT


@pytest.mark.parametrize("content, message", [
    (None, "not found"),
    ("a,b\n1,2\n", "rating,count"),
    ("rating,count\nGood,many\n", "could not be read"),
])
def test_load_c3_batch_errors(tmp_path, content, message):
    path = tmp_path / "counts.csv"
    if content is not None:
        path.write_text(content, encoding="utf-8")
    assert message in load_c3_batch(path)["error"]


def test_load_c3_batch_unset():
    assert "not set" in load_c3_batch(None)["error"]


def test_repository_c3_output_is_readable():
    from backend.reports import REPO_C3_COUNTS
    batch = load_c3_batch(REPO_C3_COUNTS)
    assert batch["counts"] == {"Good": 12, "OK": 10, "Poor": 8}


# --- pages ---------------------------------------------------------------------------------

@pytest.mark.parametrize("path", ["/staff/", "/staff/report"])
def test_pages_require_login(client, path):
    assert client.get(path).status_code == 302


def test_login_lands_on_dashboard(client):
    resp = _login(client)
    assert resp.headers["Location"].endswith("/staff/")


def test_dashboard_numbers(client, app):
    s = _store(app)
    for r, d in [("Good", 0), ("Good", 0), ("Poor", 0), ("OK", 1), ("Good", 20)]:
        s.add(r, submitted=_at(d))
    _login(client)
    html = client.get("/staff/").get_data(as_text=True)
    assert "Total responses" in html
    assert "60.0%" in html  # Good 3 of 5
    assert "+2 vs yesterday (1)" in html  # today 3, yesterday 1

    data = json.loads(html.split('id="chart-data">')[1].split("</script>")[0])
    assert len(data["labels"]) == 14
    assert data["distribution"] == [3, 1, 1]
    assert data["series"]["Good"][-1] == 2  # today
    assert sum(data["series"]["Good"]) == 2  # the 20-day-old one is outside the window


def test_report_for_specific_day(client, app):
    s = _store(app)
    s.add("Good", submitted=_at(1))
    s.add("Poor", submitted=_at(1))
    s.add("OK", submitted=_at(2))
    _login(client)
    day = _at(1).date().isoformat()
    html = client.get(f"/staff/report?date={day}").get_data(as_text=True)
    assert f"For management · {day}" in html
    assert "50.0%" in html
    assert "+1 vs" in html  # 2 responses vs 1 the day before
    assert "Batch result (C3, PySpark)" in html


def test_report_shows_c3_batch(tmp_path):
    (tmp_path / "counts.csv").write_text("rating,count\nGood,7\nOK,2\nPoor,1\n", encoding="utf-8")
    app = create_app({"DATABASE_PATH": str(tmp_path / "s.db"), "LOG_FILE": "",
                      "C3_COUNTS_PATH": str(tmp_path / "counts.csv")})
    client = app.test_client()
    _login(client)
    html = client.get("/staff/report").get_data(as_text=True)
    assert "70.0%" in html and "counts.csv" in html


def test_report_rejects_bad_date(client):
    _login(client)
    html = client.get("/staff/report?date=tomorrow").get_data(as_text=True)
    assert "Date must be a date" in html
