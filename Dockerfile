FROM python:3.11-slim

WORKDIR /app

# System deps
RUN echo "Installing system dependencies..." && \
    apt-get update && apt-get install -y \
        gcc \
        libpq-dev \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN echo "Installing Python dependencies..." && \
    pip install --no-cache-dir -r requirements.txt && \
    echo "Verifying gunicorn installation..." && \
    gunicorn --version

# Copy code
COPY . .

ENV PYTHONUNBUFFERED=1
ENV PORT=8000
EXPOSE 8000

# IMPORTANT: run gunicorn directly, no extra shell
# If your Flask app is at src/diabetes_tracker/app.py with `app = Flask(...)`:
CMD ["sh", "-c", "echo 'Starting gunicorn on port ${PORT:-8000}...' && gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 --access-logfile - --error-logfile - --log-level info 'src.diabetes_tracker.app:app'"]
