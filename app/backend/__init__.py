"""Company A survey service (SWE309 C1 prototype)."""

import time

from flask import Flask, g, jsonify, render_template, request

from . import staff
from .auth import DEV_USERNAME, LoginThrottle, csrf_token, current_staff, resolve_staff_account
from .config import APP_DIR, load_config
from .logging_setup import setup_logging
from .routes import bp
from .storage import make_store

FRONTEND_DIR = APP_DIR / "frontend"


def create_app(overrides=None):
    config = load_config(overrides)
    app = Flask(
        __name__,
        template_folder=str(FRONTEND_DIR / "templates"),
        static_folder=str(FRONTEND_DIR / "static"),
    )
    app.config.update(config)

    log = setup_logging(config)
    store = make_store(config)
    store.init_schema()
    app.extensions["response_store"] = store
    app.extensions["login_throttle"] = LoginThrottle()
    app.register_blueprint(bp)
    app.register_blueprint(staff.bp)

    staff_user, staff_hash = resolve_staff_account(config)
    app.config["STAFF_ACCOUNT_USERNAME"] = staff_user
    app.config["STAFF_ACCOUNT_HASH"] = staff_hash
    if staff_user is None:
        log.warning("staff area disabled: set STAFF_USERNAME and STAFF_PASSWORD_HASH")
    elif staff_user == DEV_USERNAME and not config["STAFF_USERNAME"]:
        log.warning("using the development demo staff account (never in production)")

    if config.get("SECRET_KEY_GENERATED") and config["APP_ENV"] == "production":
        log.warning("SECRET_KEY is not set; using a random key (set it before enabling staff login)")

    app.jinja_env.globals.update(csrf_token=csrf_token, current_staff=current_staff)

    @app.before_request
    def _start_timer():
        g.started = time.perf_counter()

    @app.after_request
    def _log_request(response):
        if not request.path.startswith("/static/"):
            elapsed_ms = (time.perf_counter() - g.get("started", time.perf_counter())) * 1000
            log.info(
                "request method=%s path=%s status=%s duration_ms=%.1f",
                request.method, request.path, response.status_code, elapsed_ms,
            )
        return response

    def _wants_json():
        return request.path.startswith("/api/") or request.path == "/health"

    @app.errorhandler(400)
    def _bad_request(_err):
        if _wants_json():
            return jsonify(error="bad_request"), 400
        return render_template("error.html", code=400,
                               message="The form expired or was invalid. Please try again."), 400

    @app.errorhandler(404)
    def _not_found(_err):
        if _wants_json():
            return jsonify(error="not_found"), 404
        return render_template("error.html", code=404, message="Page not found."), 404

    @app.errorhandler(413)
    def _too_large(_err):
        log.warning("request rejected reason=too_large path=%s", request.path)
        if _wants_json():
            return jsonify(error="too_large"), 413
        return render_template("error.html", code=413, message="Submission too large."), 413

    @app.errorhandler(500)
    def _server_error(_err):
        log.exception("unhandled error path=%s", request.path)
        if _wants_json():
            return jsonify(error="server_error"), 500
        return render_template("error.html", code=500, message="Something went wrong."), 500

    log.info(
        "app started env=%s storage=%s database=%s responses=%d",
        config["APP_ENV"], config["STORAGE_BACKEND"], config["DATABASE_PATH"], store.count(),
    )
    return app
