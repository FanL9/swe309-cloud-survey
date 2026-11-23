"""WSGI entry point for production servers, e.g. `gunicorn wsgi:app`."""

from backend import create_app

app = create_app()
