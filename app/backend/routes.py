"""HTTP routes: survey page, JSON API and health check."""

import logging

from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from .logging_setup import LOGGER_NAME
from .validation import RATINGS, ValidationError, validate_submission

bp = Blueprint("survey", __name__)
log = logging.getLogger(LOGGER_NAME)


def _store():
    return current_app.extensions["response_store"]


def _short(value, limit=40):
    text = repr(value)
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _save(data, channel):
    """Validate and store one submission. Raises ValidationError."""
    try:
        rating, comment = validate_submission(data)
    except ValidationError as err:
        log.warning(
            "response rejected channel=%s reason=%s value=%s",
            channel, err.reason, _short(err.value),
        )
        raise
    record = _store().add(rating, comment)
    log.info(
        "response accepted channel=%s response_id=%s rating=%s",
        channel, record["response_id"], record["rating"],
    )
    return record


@bp.get("/")
def survey_form():
    return render_template("survey.html", ratings=RATINGS)


@bp.post("/")
def survey_submit():
    try:
        record = _save(request.form, channel="form")
    except ValidationError as err:
        return (
            render_template(
                "survey.html",
                ratings=RATINGS,
                error=err.message,
                comment=request.form.get("comment", ""),
            ),
            400,
        )
    # Post/Redirect/Get: refreshing the thank-you page does not resubmit.
    return redirect(url_for("survey.thanks", response_id=record["response_id"]), code=303)


@bp.get("/thanks/<response_id>")
def thanks(response_id):
    # Only echoes the ID back; it does not look anything up, so the page
    # cannot be used to read other people's responses.
    return render_template("thanks.html", response_id=response_id)


@bp.post("/api/responses")
def api_create_response():
    if request.is_json:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            log.warning("response rejected channel=api reason=bad_json")
            return jsonify(error="bad_json", message="Body must be a JSON object."), 400
    else:
        data = request.form
    try:
        record = _save(data, channel="api")
    except ValidationError as err:
        return jsonify(error=err.reason, message=err.message, allowed=list(RATINGS)), 400
    return jsonify(
        response_id=record["response_id"],
        rating=record["rating"],
        submitted_at=record["submitted_at"],
    ), 201


@bp.get("/health")
def health():
    try:
        _store().ping()
    except Exception:  # noqa: BLE001 - any storage failure means unhealthy
        log.exception("health check failed")
        return jsonify(status="error", storage="unavailable"), 503
    return jsonify(status="ok", storage="ok")
