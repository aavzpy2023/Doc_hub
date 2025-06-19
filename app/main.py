# /app/main.py (Versión Refactorizada)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.db.database import engine, Base
from app.db import models
from app.core.config import settings

# --- API Routers ---
# Importamos los routers que creamos en la carpeta /api
from app.api import login, users, documents

# --------------------------------------------------------------------------
# 1. Creación de las Tablas de la Base de Datos
# --------------------------------------------------------------------------
# Es crucial que los modelos se importen antes de llamar a create_all
# para que SQLAlchemy los conozca.
Base.metadata.create_all(bind=engine)

# --------------------------------------------------------------------------
# 2. Creación de la Instancia Principal de la Aplicación FastAPI
# --------------------------------------------------------------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# --------------------------------------------------------------------------
# 3. Inclusión de los Routers de la API
# --------------------------------------------------------------------------
# Aquí "conectamos" los endpoints definidos en otros archivos.
# Todas las rutas en 'login.router' comenzarán con '/api/v1/login'.
app.include_router(login.router, prefix=f"{settings.API_V1_STR}/login", tags=["Login"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(documents.router, prefix=f"{settings.API_V1_STR}/documents", tags=["Documents"])


# --------------------------------------------------------------------------
# 4. Servir el Frontend (Opcional, pero necesario para el editor)
# --------------------------------------------------------------------------
# Montamos el directorio 'static' para servir CSS/JS
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Un endpoint para servir la página de login
@app.get("/login", response_class=HTMLResponse, tags=["Frontend"])
async def read_login_page():
    with open("app/static/login.html") as f:
        return HTMLResponse(content=f.read())

# Un endpoint para servir la página principal del editor
@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
@app.get("/editor", response_class=HTMLResponse, tags=["Frontend"])
async def read_editor_page():
    with open("app/static/editor.html") as f:
        return HTMLResponse(content=f.read())