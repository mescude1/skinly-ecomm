# Usa una imagen oficial de Python
FROM python:3.11-slim

# Evita que Python escriba .pyc y buffer
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define el puerto (Cloud Run lo sobreescribe)
ENV PORT 8080

# Crea el directorio de la app
WORKDIR /app

# Copia el código
COPY . /app

# Instala dependencias del sistema necesarias
RUN apt-get update && apt-get install -y build-essential libpq-dev libjpeg-dev zlib1g-dev && rm -rf /var/lib/apt/lists/*

# Instala dependencias de Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

# Recoge archivos estáticos
RUN python manage.py collectstatic --noinput || true

# Expone el puerto
EXPOSE 8080

# Ejecuta migraciones y arranca el servidor con Gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn skinly_core.wsgi:application --bind 0.0.0.0:${PORT:-8080} --workers 3 --timeout 120"]
