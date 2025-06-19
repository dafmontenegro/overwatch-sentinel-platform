FROM python:3.9-slim

WORKDIR /backend

# Instala dependencias del sistema y psql
RUN apt-get update && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY .env .
COPY ./src ./src
COPY wait-for-postgres.sh .

RUN chmod +x wait-for-postgres.sh

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port 8000"]
#./wait-for-postgres.sh db && 