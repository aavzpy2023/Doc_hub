# /Dockerfile

# ==============================================================================
# Etapa 1: Imagen Base
# ==============================================================================
# Usamos una imagen oficial de Python basada en Debian 'Bookworm' (la versión estable más reciente).
# La etiqueta 'slim' asegura que la imagen sea lo más pequeña posible sin sacrificar
# la funcionalidad del gestor de paquetes 'apt'.
FROM python:3.11-slim-bookworm

# ==============================================================================
# Etapa 2: Instalación de Dependencias del Sistema Operativo
# ==============================================================================
# Aquí instalamos todas las herramientas a nivel de sistema que nuestra aplicación necesita.
# Es crucial para la generación de PDFs y otras funcionalidades.

# Actualizamos los repositorios e instalamos Pandoc y una distribución de LaTeX.
# Usamos --no-install-recommends para evitar paquetes innecesarios y mantener la imagen pequeña.
# Al final, limpiamos la caché de apt para optimizar el tamaño final de la imagen.
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Herramienta principal para la conversión de documentos
    pandoc \
    # Motor de composición tipográfica LaTeX, esencial para PDFs de alta calidad
    texlive-latex-base \
    # Paquete de fuentes comunes para LaTeX
    texlive-fonts-recommended \
    # Motor XeTeX, que maneja muy bien las fuentes del sistema (como Calibri)
    texlive-xetex \
    # Dependencias de Git, en caso de que necesitemos interactuar con el repositorio
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ==============================================================================
# Etapa 3: Configuración del Entorno de Trabajo y Dependencias de Python
# ==============================================================================
# Establecemos el directorio de trabajo principal dentro del contenedor.
WORKDIR /code

# Copiamos primero el archivo de requerimientos de Python.
# Docker guardará esta capa en caché. Si no cambias tus dependencias,
# no se volverán a instalar cada vez que construyas la imagen, acelerando el proceso.
COPY ./app/requirements.txt /code/

# Instalamos las dependencias de Python especificadas en requirements.txt.
# --no-cache-dir reduce el tamaño de la imagen al no guardar la caché de pip.
RUN pip install --no-cache-dir -r requirements.txt

# ==============================================================================
# Etapa 4: Copia del Código de la Aplicación
# ==============================================================================
# Copiamos todo el contenido de nuestra carpeta 'app' (que contiene el código fuente)
# al subdirectorio 'app' dentro del contenedor.
# La estructura final dentro del contenedor será /code/app/...
COPY ./app /code/app

# ==============================================================================
# Etapa 5: Comando de Ejecución
# ==============================================================================
# Este es el comando que se ejecutará cuando el contenedor se inicie.
# - WORKDIR es /code, por lo que Uvicorn se ejecuta desde fuera del paquete 'app'.
# - 'app.main:app': Uvicorn buscará un paquete llamado 'app', dentro de él un
#   módulo llamado 'main.py', y dentro de él una instancia de FastAPI llamada 'app'.
#   Esto resuelve el 'ImportError: attempted relative import with no known parent package'.
# - '--host 0.0.0.0': Hace que la aplicación sea accesible desde fuera del contenedor.
# - '--port 8000': El puerto en el que la aplicación escuchará dentro del contenedor.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]