FROM python:3.9-slim

WORKDIR /app

# Instala dependencias del sistema y psql
RUN apt-get update && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY .env .
COPY ./app ./app
COPY wait-for-postgres.sh .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["sh", "-c", "./wait-for-postgres.sh db && uvicorn app.main:app --host 0.0.0.0 --port 8000"]