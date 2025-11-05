# 1️⃣ Usa una imagen oficial de Python
FROM python:3.11-slim

# 2️⃣ Establece el directorio de trabajo
WORKDIR /app

# 3️⃣ Copia los archivos
COPY . /app

# 4️⃣ Instala dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 5️⃣ Copia variables de entorno
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=skinly_core.settings
ENV DEBUG=False
ENV ALLOWED_HOSTS="*"

# 6️⃣ Expone el puerto
EXPOSE 8000

# 7️⃣ Ejecuta migraciones y lanza el servidor
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn skinly_core.wsgi:application --bind 0.0.0.0:$PORT"]
