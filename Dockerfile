# Usa una imagen ligera de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto
COPY . /app

# Instala dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expone el puerto 8080 (el que usa Cloud Run)
EXPOSE 8000

# Ejecuta las migraciones, recopila estáticos y arranca con Gunicorn
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn skinly.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
