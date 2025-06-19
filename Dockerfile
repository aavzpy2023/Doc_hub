# /Dockerfile

# --- Etapa 1: Imagen base ---
# Usamos una imagen oficial de Python. La versión 'slim' es más ligera.
FROM python:3.11-slim

# --- Etapa 2: Configuración del entorno de trabajo ---
# Establecemos el directorio de trabajo dentro del contenedor.
# Todas las operaciones siguientes se harán relativas a esta ruta.
WORKDIR /app

# --- Etapa 3: Copiar archivos de requerimientos e instalar dependencias ---
# Copiamos solo el requirements.txt primero. Docker cacheará esta capa,
# así que no reinstalará todo cada vez que cambies tu código, solo si
# cambian las dependencias. Es una buena práctica de optimización.
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# --- Etapa 4: Copiar el resto del código de la aplicación ---
# Ahora copiamos todos los archivos de tu proyecto al directorio de trabajo /app.
COPY . .

# --- Etapa 5: Comando de ejecución ---
# Este es el comando que se ejecutará cuando el contenedor inicie.
# Le dice a Uvicorn que sirva la aplicación 'app' desde el archivo 'main.py'.
# --host 0.0.0.0 es crucial para que la app sea accesible desde fuera del contenedor.
# --port 8000 es el puerto que la aplicación escuchará dentro del contenedor.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
