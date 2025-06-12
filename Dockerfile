# Usamos la version slim ya que es mas liviana
FROM python:3.12-slim

# Establecer el directorio de trabajo
WORKDIR /app

# --- Capa 1: copiamos sólo requirements para aprovechar caché ---
COPY requirements.txt ./

# ---Capa 2: Instalar dependencias del sistema en un solo Run
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev build-essential \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove gcc libpq-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto por defecto de Django
EXPOSE 8000

# Comando por defecto para correr el servidor de desarrollo
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn eventhub.wsgi:application --bind 0.0.0.0:8000 --workers 3"]
