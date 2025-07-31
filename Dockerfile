FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# We still copy the app/ directory for the initial build,
# but the volume mount will take precedence for development changes.
COPY app/ app/

EXPOSE 8000

# The CMD here will be overridden by the docker-compose.yml,
# but it's good practice to have a sensible default.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]