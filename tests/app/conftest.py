import sys
from pathlib import Path

import pytest

APP_DIR = Path(__file__).resolve().parents[2] / "app"
sys.path.insert(0, str(APP_DIR))

from backend import create_app  # noqa: E402


@pytest.fixture
def make_app(tmp_path):
    """Build an app on a throwaway database; call again to simulate a restart."""
    def _make():
        return create_app({
            "DATABASE_PATH": str(tmp_path / "survey.db"),
            "LOG_FILE": str(tmp_path / "app.log"),
            "EXPORT_DIR": str(tmp_path / "exports"),
        })
    return _make


@pytest.fixture
def app(make_app):
    return make_app()


@pytest.fixture
def client(app):
    return app.test_client()
