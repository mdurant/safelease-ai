# Imagen base para Django y FastAPI (mismo código, distinto comando)
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Dependencias del sistema para psycopg
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Por defecto no arrancar nada (compose define el comando por servicio)
CMD ["python", "-c", "print('Use docker-compose to run django or fastapi')"]
