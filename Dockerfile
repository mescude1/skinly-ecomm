# Usa una imagen ligera de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto
COPY . /app

# Instala dependencias del sistema y Python
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install -r requirements.txt gunicorn

# Expone el puerto 8080 (Cloud Run usa este puerto)
EXPOSE 8080

# Ejecuta migraciones, recopila estáticos y arranca con Gunicorn
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn skinly_core.wsgi:application --bind 0.0.0.0:${PORT:-8080}"]
