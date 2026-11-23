import re

import pytest
from werkzeug.security import generate_password_hash

from backend import create_app
from backend.auth import DEV_PASSWORD, DEV_USERNAME, MAX_FAILURES


def _csrf(client, path="/staff/login"):
    html = client.get(path).get_data(as_text=True)
    return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)


def _login(client, username=DEV_USERNAME, password=DEV_PASSWORD, next_url=""):
    token = _csrf(client)
    return client.post("/staff/login", data={
        "csrf_token": token, "username": username, "password": password, "next": next_url,
    })


@pytest.fixture
def staff(client):
    assert _login(client).status_code == 302
    return client


def _add(app, *ratings):
    store = app.extensions["response_store"]
    return [store.add(r, f"comment {i}")["response_id"] for i, r in enumerate(ratings)]


# --- access control -------------------------------------------------------------

@pytest.mark.parametrize("path", ["/staff/", "/staff/responses", "/staff/export.csv",
                                  "/staff/lookup?id=X", "/staff/responses/R20261123-AAAAAA"])
def test_staff_pages_require_login(client, path):
    resp = client.get(path)
    assert resp.status_code == 302
    assert "/staff/login" in resp.headers["Location"]


def test_login_success_and_redirect_to_next(client):
    resp = _login(client, next_url="/staff/responses?rating=Good")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/staff/responses?rating=Good")
    assert client.get("/staff/responses").status_code == 200


def test_login_rejects_open_redirect(client):
    resp = _login(client, next_url="https://evil.example/")
    assert resp.headers["Location"].endswith("/staff/")


def test_wrong_password_rejected(client):
    resp = _login(client, password="wrong-password")
    assert resp.status_code == 401
    assert "Incorrect username or password" in resp.get_data(as_text=True)
    assert client.get("/staff/responses").status_code == 302


def test_login_without_csrf_rejected(client):
    resp = client.post("/staff/login", data={"username": DEV_USERNAME, "password": DEV_PASSWORD})
    assert resp.status_code == 400


def test_lockout_after_repeated_failures(client):
    for _ in range(MAX_FAILURES):
        _login(client, password="nope")
    resp = _login(client)  # correct password, but locked
    assert resp.status_code == 401
    assert "Too many failed attempts" in resp.get_data(as_text=True)


def test_logout(staff):
    token = _csrf(staff, "/staff/responses")
    resp = staff.post("/staff/logout", data={"csrf_token": token})
    assert resp.status_code == 302
    assert staff.get("/staff/responses").status_code == 302


def test_configured_account_replaces_demo(tmp_path):
    app = create_app({
        "DATABASE_PATH": str(tmp_path / "s.db"), "LOG_FILE": "",
        "STAFF_USERNAME": "alice", "STAFF_PASSWORD_HASH": generate_password_hash("correct horse"),
    })
    client = app.test_client()
    assert _login(client).status_code == 401  # demo account no longer works
    assert _login(client, "alice", "correct horse").status_code == 302


def test_production_without_account_disables_staff_area(tmp_path):
    app = create_app({"DATABASE_PATH": str(tmp_path / "s.db"), "LOG_FILE": "", "APP_ENV": "production"})
    client = app.test_client()
    page = client.get("/staff/login").get_data(as_text=True)
    assert "not configured" in page
    # The form is hidden, and posting directly still fails.
    with client.session_transaction() as s:
        s["csrf_token"] = "t"
    resp = client.post("/staff/login", data={"csrf_token": "t", "username": DEV_USERNAME,
                                             "password": DEV_PASSWORD})
    assert resp.status_code == 401


# --- list, filters, lookup, export ----------------------------------------------

def test_list_shows_newest_first(staff, app):
    ids = _add(app, "Good", "OK", "Poor")
    html = staff.get("/staff/responses").get_data(as_text=True)
    positions = [html.index(i) for i in ids]
    assert positions == sorted(positions, reverse=True)
    assert "3 responses" in html


def test_filter_by_rating(staff, app):
    good, ok, poor = _add(app, "Good", "OK", "Poor")
    html = staff.get("/staff/responses?rating=OK").get_data(as_text=True)
    assert ok in html and good not in html and poor not in html


def test_filter_by_id_fragment_and_dates(staff, app):
    good, ok = _add(app, "Good", "OK")
    html = staff.get(f"/staff/responses?q={ok[-6:].lower()}").get_data(as_text=True)
    assert ok in html and good not in html

    today = ok[1:5] + "-" + ok[5:7] + "-" + ok[7:9]
    assert ok in staff.get(f"/staff/responses?from={today}&to={today}").get_data(as_text=True)
    html = staff.get("/staff/responses?from=2000-01-01&to=2000-01-02").get_data(as_text=True)
    assert "No responses found" in html


def test_invalid_filters_reported_not_crashing(staff):
    html = staff.get("/staff/responses?rating=Great&from=yesterday&page=abc").get_data(as_text=True)
    assert "Rating filter must be" in html
    assert "From must be a date" in html


def test_pagination(staff, app):
    _add(app, *(["Good"] * 25))
    first = staff.get("/staff/responses").get_data(as_text=True)
    assert "Page 1 of 2" in first
    second = staff.get("/staff/responses?page=2").get_data(as_text=True)
    assert second.count("badge-rating badge-good") == 5


def test_lookup_by_exact_id(staff, app):
    (rid,) = _add(app, "Poor")
    resp = staff.get(f"/staff/lookup?id={rid.lower()}")
    assert resp.status_code == 302
    detail = staff.get(resp.headers["Location"]).get_data(as_text=True)
    assert rid in detail and "comment 0" in detail


def test_lookup_unknown_id(staff):
    resp = staff.get("/staff/lookup?id=R20000101-ZZZZZZ", follow_redirects=True)
    assert "No response found" in resp.get_data(as_text=True)
    assert staff.get("/staff/responses/R20000101-ZZZZZZ").status_code == 404


def test_staff_export_download(staff, app):
    _add(app, "Good", "OK")
    resp = staff.get("/staff/export.csv")
    assert resp.status_code == 200
    assert resp.mimetype == "text/csv"
    assert "attachment" in resp.headers["Content-Disposition"]
    lines = resp.get_data(as_text=True).strip().split("\n")
    assert lines[0] == "response_id,rating,submitted_at"
    assert len(lines) == 3
    assert "comment" not in resp.get_data(as_text=True)


def test_staff_access_is_logged(staff, app, tmp_path):
    (rid,) = _add(app, "Good")
    staff.get(f"/staff/responses/{rid}")
    staff.get("/staff/export.csv")
    log_text = (tmp_path / "app.log").read_text(encoding="utf-8")
    assert f"staff login success user={DEV_USERNAME}" in log_text
    assert f"staff viewed response user={DEV_USERNAME} response_id={rid}" in log_text
    assert f"staff export user={DEV_USERNAME} rows=1" in log_text
    assert DEV_PASSWORD not in log_text
