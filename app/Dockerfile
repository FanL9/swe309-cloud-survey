# Container image for Cloud Run or any container platform.
# Build from the app/ folder:  docker build -t survey .
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    HOST=0.0.0.0 \
    PORT=8080 \
    LOG_FILE= \
    DATABASE_PATH=/tmp/survey.db \
    EXPORT_DIR=/tmp/exports

WORKDIR /srv/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY frontend ./frontend
COPY wsgi.py export_csv.py ./

RUN useradd --create-home appuser
USER appuser

EXPOSE 8080
CMD exec gunicorn --bind 0.0.0.0:${PORT} --workers 2 --threads 4 --access-logfile - wsgi:app
