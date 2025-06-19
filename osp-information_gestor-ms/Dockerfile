FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar primero requirements.txt para aprovechar cache de Docker
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el contenido (incluyendo .env)
COPY . .

# Puerto expuesto
EXPOSE 8001

# Comando para ejecutar la aplicación (usará el .env copiado)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]