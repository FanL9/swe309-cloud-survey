"""Application settings, read from environment variables.

Every value that differs between a laptop and the cloud lives here, so the
same code runs unchanged in both places. See coordination/interfaces.md.
"""

import os
import secrets
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent  # .../app


def _env(name, default):
    value = os.environ.get(name)
    return default if value is None else value


def load_config(overrides=None):
    config = {
        "APP_ENV": _env("APP_ENV", "development"),
        "HOST": _env("HOST", "127.0.0.1"),
        "PORT": int(_env("PORT", "8000")),
        "DATABASE_PATH": _env("DATABASE_PATH", str(APP_DIR / "instance" / "survey.db")),
        "LOG_LEVEL": _env("LOG_LEVEL", "INFO").upper(),
        "LOG_FILE": _env("LOG_FILE", str(APP_DIR / "logs" / "app.log")),
        "EXPORT_DIR": _env("EXPORT_DIR", str(APP_DIR / "instance" / "exports")),
        "SECRET_KEY": _env("SECRET_KEY", ""),
        "STORAGE_BACKEND": _env("STORAGE_BACKEND", "sqlite").lower(),
        # Reserved for the staff area (step 4) and report page (step 5).
        "STAFF_USERNAME": _env("STAFF_USERNAME", ""),
        "STAFF_PASSWORD_HASH": _env("STAFF_PASSWORD_HASH", ""),
        "C3_COUNTS_PATH": _env("C3_COUNTS_PATH", ""),
        # Survey form posts are tiny; anything larger is rejected outright.
        "MAX_CONTENT_LENGTH": 16 * 1024,
    }
    if overrides:
        config.update(overrides)
    if not config["SECRET_KEY"]:
        # Fine for local runs; production must set a fixed key so sessions
        # survive restarts and work across instances.
        config["SECRET_KEY"] = secrets.token_hex(32)
        config["SECRET_KEY_GENERATED"] = True
    return config
