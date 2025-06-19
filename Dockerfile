# /Dockerfile (Versión Verificada)

FROM python:3.11-slim-bookworm

# ... (instalación de pandoc, etc.) ...
RUN apt-get update && apt-get install -y --no-install-recommends \
    pandoc texlive-latex-base texlive-fonts-recommended texlive-xetex git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 1. Establecer el directorio de trabajo
WORKDIR /code

# 2. Copiar el archivo de requerimientos desde la carpeta 'app' del host
#    al directorio de trabajo '/code' en el contenedor.
COPY ./app/requirements.txt /code/

# 3. Ejecutar pip install. Se usará el archivo /code/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar todo el código de la aplicación
COPY ./app /code/app

# 5. Comando de ejecución
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]