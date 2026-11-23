"""Staff area: login, response list with filters, lookup by ID, CSV download.

Every staff action that reads personal data (viewing a response, exporting)
is written to the log with the staff username, as an access audit trail.
"""

import logging
import math
from datetime import date, timedelta

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .auth import check_login, current_staff, login_required, safe_next, verify_csrf
from .export import export_text
from .logging_setup import LOGGER_NAME
from .reports import load_c3_batch, percentages, resolve_c3_path
from .storage import now_myt
from .validation import RATINGS

bp = Blueprint("staff", __name__, url_prefix="/staff")
log = logging.getLogger(LOGGER_NAME)

PAGE_SIZE = 20
TREND_DAYS = 14


def _store():
    return current_app.extensions["response_store"]


def _throttle():
    return current_app.extensions["login_throttle"]


def _parse_date(value, label, errors):
    if not value:
        return None
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        errors.append(f"{label} must be a date (YYYY-MM-DD).")
        return None


@bp.route("/login", methods=["GET", "POST"])
def login():
    enabled = bool(current_app.config["STAFF_ACCOUNT_USERNAME"])
    if current_staff():
        return redirect(url_for("staff.dashboard"))
    if request.method == "GET":
        return render_template("staff/login.html", enabled=enabled,
                               next=request.args.get("next", ""))

    verify_csrf()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    next_url = request.form.get("next", "")
    error = None
    if not enabled:
        error = "Staff login is not configured on this server."
    elif _throttle().locked(username):
        log.warning("staff login blocked reason=locked user=%s", username or "-")
        error = "Too many failed attempts. Try again in 15 minutes."
    elif check_login(username, password):
        _throttle().reset(username)
        session.clear()
        session.permanent = True
        session["staff_user"] = username
        log.info("staff login success user=%s", username)
        return redirect(safe_next(next_url))
    else:
        _throttle().fail(username)
        log.warning("staff login failed user=%s", username or "-")
        error = "Incorrect username or password."
    return render_template("staff/login.html", enabled=enabled, error=error,
                           username=username, next=next_url), 401


@bp.post("/logout")
@login_required
def logout():
    verify_csrf()
    log.info("staff logout user=%s", current_staff())
    session.clear()
    flash("You have been signed out.")
    return redirect(url_for("staff.login"))


@bp.get("/")
@login_required
def dashboard():
    store = _store()
    today = now_myt().date()
    yesterday = today - timedelta(days=1)
    all_counts = store.rating_counts()
    total = sum(all_counts.values())
    today_total = sum(store.rating_counts(today.isoformat(), today.isoformat()).values())
    yesterday_total = sum(store.rating_counts(yesterday.isoformat(), yesterday.isoformat()).values())
    days = store.daily_counts(today - timedelta(days=TREND_DAYS - 1), today)
    return render_template(
        "staff/dashboard.html",
        total=total, counts=all_counts, pct=percentages(all_counts),
        today_total=today_total, yesterday_total=yesterday_total,
        days=days, trend_days=TREND_DAYS, ratings=RATINGS,
        chart_data={
            "labels": [d["day"][5:] for d in days],
            "series": {r: [d[r] for d in days] for r in RATINGS},
            "distribution": [all_counts[r] for r in RATINGS],
        },
    )


@bp.get("/report")
@login_required
def report():
    errors = []
    today = now_myt().date()
    day_text = _parse_date(request.args.get("date", ""), "Date", errors) or today.isoformat()
    day = date.fromisoformat(day_text)
    prev = day - timedelta(days=1)
    store = _store()
    counts = store.rating_counts(day_text, day_text)
    prev_counts = store.rating_counts(prev.isoformat(), prev.isoformat())
    week = store.daily_counts(day - timedelta(days=6), day)
    batch = load_c3_batch(resolve_c3_path(current_app.config))
    log.info("staff viewed report user=%s date=%s", current_staff(), day_text)
    return render_template(
        "staff/report.html",
        day=day_text, prev_day=prev.isoformat(), next_day=(day + timedelta(days=1)).isoformat(),
        is_today=day >= today, errors=errors, ratings=RATINGS,
        counts=counts, total=sum(counts.values()), pct=percentages(counts),
        prev_counts=prev_counts, prev_total=sum(prev_counts.values()),
        week=week, batch=batch,
        batch_pct=percentages(batch["counts"]) if "counts" in batch else None,
        generated_at=now_myt(),
    )


@bp.get("/responses")
@login_required
def responses():
    errors = []
    rating = request.args.get("rating", "")
    if rating and rating not in RATINGS:
        errors.append("Rating filter must be Good, OK or Poor.")
        rating = ""
    date_from = _parse_date(request.args.get("from", ""), "From", errors)
    date_to = _parse_date(request.args.get("to", ""), "To", errors)
    if date_from and date_to and date_from > date_to:
        errors.append("'From' must not be after 'To'.")
        date_from = date_to = None
    query = request.args.get("q", "").strip()[:40]
    try:
        page = max(1, int(request.args.get("page", "1")))
    except ValueError:
        page = 1

    rows, total = _store().search(
        rating=rating or None, date_from=date_from, date_to=date_to,
        id_contains=query or None, limit=PAGE_SIZE, offset=(page - 1) * PAGE_SIZE,
    )
    pages = max(1, math.ceil(total / PAGE_SIZE))
    filters = {"rating": rating, "from": date_from or "", "to": date_to or "", "q": query}
    return render_template(
        "staff/responses.html",
        rows=rows, total=total, page=page, pages=pages, filters=filters,
        ratings=RATINGS, errors=errors,
        active_filters=any(filters.values()),
    )


@bp.get("/lookup")
@login_required
def lookup():
    """Support-desk lookup: jump straight to one response by its exact ID."""
    response_id = request.args.get("id", "").strip().upper()
    if response_id and _store().get(response_id):
        return redirect(url_for("staff.response_detail", response_id=response_id))
    log.info("staff lookup not_found user=%s response_id=%s", current_staff(), response_id[:40] or "-")
    flash(f"No response found with ID {response_id[:40]!s}." if response_id else "Enter a response ID.")
    return redirect(url_for("staff.responses"))


@bp.get("/responses/<response_id>")
@login_required
def response_detail(response_id):
    record = _store().get(response_id)
    if record is None:
        log.info("staff lookup not_found user=%s response_id=%s", current_staff(), response_id[:40])
        return render_template("error.html", code=404, message="Response not found."), 404
    log.info("staff viewed response user=%s response_id=%s", current_staff(), response_id)
    return render_template("staff/response_detail.html", r=record)


@bp.get("/export.csv")
@login_required
def export_csv():
    text, rows = export_text(_store())
    filename = f"responses-{now_myt():%Y%m%d-%H%M%S}.csv"
    log.info("staff export user=%s rows=%d", current_staff(), rows)
    return Response(
        text,
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
