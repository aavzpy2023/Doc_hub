from app.api import documents, login, project_docs, users
from app.core.config import settings
from app.db import models

# Application imports
from app.db.database import engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- 1. Database Table Creation ---
# SQLAlchemy uses the imported models to create tables if they do not exist.
# It is crucial to import 'models' so that Base.metadata becomes aware of them.
models.Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost",
    "http://localhost:8080",  # The port of frontend
    # "https://your-domine.com",
]

# --- 2. FastAPI Application Instance Creation ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
