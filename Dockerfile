FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy only application files (not .env)
# .env contains sensitive credentials and should not be in the image
COPY app/ ./app/
COPY tests/ ./tests/
COPY CSV_to_json.py .
COPY products.csv .
COPY products.json .

EXPOSE 8000

# MONGO_URI environment variable must be passed at runtime via -e flag
# This allows different credentials for different environments (dev/staging/prod)
# without changing the Docker image
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]