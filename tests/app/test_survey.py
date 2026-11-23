import csv
import re

import pytest

from backend.export import write_export
from backend.validation import ValidationError, validate_submission

ID_PATTERN = re.compile(r"^R\d{8}-[A-Z2-9]{6}$")
TS_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00$")


# --- validation -------------------------------------------------------------

@pytest.mark.parametrize("rating", ["Good", "OK", "Poor"])
def test_valid_ratings_accepted(rating):
    assert validate_submission({"rating": rating}) == (rating, None)


@pytest.mark.parametrize("rating", ["good", "GOOD", " Good", "Good ", "Gd", "Excellent", "ok", 5, ["Good"]])
def test_invalid_ratings_rejected(rating):
    with pytest.raises(ValidationError) as exc:
        validate_submission({"rating": rating})
    assert exc.value.reason == "invalid_rating"


@pytest.mark.parametrize("data", [{}, {"rating": ""}, {"rating": None}])
def test_missing_rating_rejected(data):
    with pytest.raises(ValidationError) as exc:
        validate_submission(data)
    assert exc.value.reason == "missing_rating"


def test_comment_trimmed_and_limited():
    assert validate_submission({"rating": "OK", "comment": "  fine  "}) == ("OK", "fine")
    assert validate_submission({"rating": "OK", "comment": "   "}) == ("OK", None)
    with pytest.raises(ValidationError):
        validate_submission({"rating": "OK", "comment": "x" * 501})


# --- form and API -------------------------------------------------------------

def test_form_submit_saves_and_redirects(client, app):
    resp = client.post("/", data={"rating": "Good", "comment": "Nice"})
    assert resp.status_code == 303
    response_id = resp.headers["Location"].rsplit("/", 1)[-1]
    assert ID_PATTERN.match(response_id)

    saved = app.extensions["response_store"].get(response_id)
    assert saved["rating"] == "Good"
    assert saved["comment"] == "Nice"
    assert TS_PATTERN.match(saved["submitted_at"])

    page = client.get(resp.headers["Location"])
    assert response_id in page.get_data(as_text=True)


def test_form_rejects_invalid_rating(client, app):
    resp = client.post("/", data={"rating": "Excellent"})
    assert resp.status_code == 400
    assert "Rating must be exactly one of" in resp.get_data(as_text=True)
    assert app.extensions["response_store"].count() == 0


def test_api_accepts_valid_rating(client):
    resp = client.post("/api/responses", json={"rating": "Poor"})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["rating"] == "Poor"
    assert ID_PATTERN.match(body["response_id"])


@pytest.mark.parametrize("payload", [{"rating": "Bad"}, {"rating": "good"}, {}, ["Good"]])
def test_api_rejects_invalid_input(client, app, payload):
    resp = client.post("/api/responses", json=payload)
    assert resp.status_code == 400
    assert app.extensions["response_store"].count() == 0


def test_oversized_request_rejected(client):
    resp = client.post("/", data={"rating": "Good", "comment": "x" * 20_000})
    assert resp.status_code == 413


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok", "storage": "ok"}


def test_unknown_page_404(client):
    assert client.get("/nope").status_code == 404


# --- persistence ----------------------------------------------------------------

def test_responses_survive_restart(make_app):
    first = make_app()
    ids = [
        first.test_client().post("/api/responses", json={"rating": r}).get_json()["response_id"]
        for r in ("Good", "OK", "Poor")
    ]

    restarted = make_app()  # new app object, same database file
    store = restarted.extensions["response_store"]
    assert store.count() == 3
    assert [store.get(i)["rating"] for i in ids] == ["Good", "OK", "Poor"]


# --- logging ----------------------------------------------------------------------

def test_logs_record_accept_and_reject_without_comment(client, app, tmp_path):
    client.post("/api/responses", json={"rating": "Good", "comment": "secret-comment-text"})
    client.post("/api/responses", json={"rating": "Excellent"})
    log_text = (tmp_path / "app.log").read_text(encoding="utf-8")
    assert "response accepted channel=api" in log_text
    assert "response rejected channel=api reason=invalid_rating value='Excellent'" in log_text
    assert "status=201" in log_text and "status=400" in log_text
    assert "secret-comment-text" not in log_text


# --- export -----------------------------------------------------------------------

def test_export_matches_c3_format(client, app, tmp_path):
    for r in ("Good", "Good", "OK"):
        client.post("/api/responses", json={"rating": r, "comment": "not exported"})
    out = tmp_path / "export.csv"
    rows = write_export(app.extensions["response_store"], out)
    assert rows == 3

    with out.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        assert reader.fieldnames == ["response_id", "rating", "submitted_at"]
        records = list(reader)
    assert [r["rating"] for r in records] == ["Good", "Good", "OK"]
    assert all(ID_PATTERN.match(r["response_id"]) for r in records)
    assert all(TS_PATTERN.match(r["submitted_at"]) for r in records)
