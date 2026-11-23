"""Local start: `python run.py` (works on Windows). Cloud uses gunicorn + wsgi.py."""

from backend import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=False)
