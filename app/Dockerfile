# /app/Dockerfile

# Usamos una imagen base de Debian que facilita la instalación de paquetes
FROM python:3.11-slim-bookworm

# --- INSTALACIÓN DE DEPENDENCIAS DEL SISTEMA ---
# Actualizamos los repositorios e instalamos Pandoc y una distribución de LaTeX
# texlive-latex-base: El motor de LaTeX
# texlive-fonts-recommended: Paquete de fuentes comunes
# texlive-xetex: El motor específico que maneja bien las fuentes del sistema como Calibri
# pandoc: La herramienta de conversión
RUN apt-get update && apt-get install -y --no-install-recommends \
    pandoc \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-xetex \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# --- Etapa 5: Comando de ejecución ---
# Este es el comando que se ejecutará cuando el contenedor inicie.
# Le dice a Uvicorn que sirva la aplicación 'app' desde el archivo 'main.py'.
# --host 0.0.0.0 es crucial para que la app sea accesible desde fuera del contenedor.
# --port 8000 es el puerto que la aplicación escuchará dentro del contenedor.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
