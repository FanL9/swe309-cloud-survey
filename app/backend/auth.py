"""Staff authentication: one staff account configured by environment variables.

- STAFF_USERNAME and STAFF_PASSWORD_HASH (a Werkzeug hash, never the plain
  password) enable the staff area. Generate the hash with hash_password.py.
- In development only, if both are unset, a demo account is used so the
  prototype can be tried locally (see app/README.md). In production the staff
  area stays disabled until both variables are set.
- Five failed logins for a username lock it for 15 minutes (per instance).
- Forms in the staff area carry a CSRF token tied to the session.
"""

import functools
import hmac
import logging
import secrets
import threading
import time

from flask import abort, current_app, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .logging_setup import LOGGER_NAME

log = logging.getLogger(LOGGER_NAME)

DEV_USERNAME = "staff"
DEV_PASSWORD = "survey-demo"

MAX_FAILURES = 5
LOCK_SECONDS = 15 * 60


class LoginThrottle:
    def __init__(self):
        self._lock = threading.Lock()
        self._failures = {}  # username -> (count, first_failure_time)

    def locked(self, username):
        with self._lock:
            count, since = self._failures.get(username, (0, 0.0))
            if count >= MAX_FAILURES and time.monotonic() - since < LOCK_SECONDS:
                return True
            if time.monotonic() - since >= LOCK_SECONDS:
                self._failures.pop(username, None)
            return False

    def fail(self, username):
        with self._lock:
            count, since = self._failures.get(username, (0, time.monotonic()))
            self._failures[username] = (count + 1, since)

    def reset(self, username):
        with self._lock:
            self._failures.pop(username, None)


def resolve_staff_account(config):
    """Return (username, password_hash) or (None, None) if the staff area is disabled."""
    username, password_hash = config["STAFF_USERNAME"], config["STAFF_PASSWORD_HASH"]
    if username and password_hash:
        return username, password_hash
    if config["APP_ENV"] == "development" and not username and not password_hash:
        return DEV_USERNAME, generate_password_hash(DEV_PASSWORD)
    return None, None


def check_login(username, password):
    """Return True if the credentials match the configured staff account."""
    expected_user = current_app.config["STAFF_ACCOUNT_USERNAME"]
    expected_hash = current_app.config["STAFF_ACCOUNT_HASH"]
    if not expected_user:
        return False
    user_ok = hmac.compare_digest(username.encode(), expected_user.encode())
    # Always run the hash check so timing does not reveal whether the user exists.
    pass_ok = check_password_hash(expected_hash, password)
    return user_ok and pass_ok


def current_staff():
    return session.get("staff_user")


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not current_staff():
            return redirect(url_for("staff.login", next=request.full_path.rstrip("?")))
        return view(*args, **kwargs)
    return wrapped


def csrf_token():
    token = session.get("csrf_token")
    if not token:
        token = session["csrf_token"] = secrets.token_urlsafe(32)
    return token


def verify_csrf():
    sent = request.form.get("csrf_token", "")
    expected = session.get("csrf_token", "")
    if not expected or not hmac.compare_digest(sent, expected):
        log.warning("request rejected reason=csrf path=%s", request.path)
        abort(400)


def safe_next(target):
    """Only allow redirects back into the staff area (no open redirects)."""
    if target and target.startswith("/staff") and not target.startswith("//"):
        return target
    return url_for("staff.responses")
