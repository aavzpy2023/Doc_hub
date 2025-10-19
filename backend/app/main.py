from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api import documents, login, project_docs, users
from app.core.config import settings
from app.db import models

# Application imports
from app.db.database import engine

# --- 1. Database Table Creation ---
# SQLAlchemy uses the imported models to create tables if they do not exist.
# It is crucial to import 'models' so that Base.metadata becomes aware of them.
models.Base.metadata.create_all(bind=engine)

# --- 2. FastAPI Application Instance Creation ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# --- 3. API Router Inclusion ---
# The API is modularized by including routers from different files.
# This keeps the code organized and scalable.
app.include_router(login.router, prefix=f"{settings.API_V1_STR}/login", tags=["Login"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(
    documents.router, prefix=f"{settings.API_V1_STR}/documents", tags=["Documents"]
)
app.include_router(
    project_docs.router,
    prefix=f"{settings.API_V1_STR}/project-docs",
    tags=["Project Docs Editor"],
)

# --- 4. Serve Basic Frontend ---
# Mounts static files (CSS, JS) for the frontend.
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/login", response_class=HTMLResponse, tags=["Frontend"])
async def read_login_page():
    """Serves the login page."""
    with open("app/static/login.html") as f:
        return HTMLResponse(content=f.read())


@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
@app.get("/editor", response_class=HTMLResponse, tags=["Frontend"])
async def read_editor_page():
    """Serves the main Markdown editor page."""
    with open("app/static/editor.html") as f:
        return HTMLResponse(content=f.read())
