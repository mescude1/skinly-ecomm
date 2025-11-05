# 1️⃣ Usa una imagen oficial de Python
FROM python:3.11-slim

# 2️⃣ Establece directorio de trabajo
WORKDIR /app

# 3️⃣ Copia los archivos del proyecto
COPY . /app

# 4️⃣ Instala dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 5️⃣ Expone el puerto que usará Django
EXPOSE 8000

# 6️⃣ Ejecuta migraciones y lanza el servidor
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
