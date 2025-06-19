#
# /app/core/config.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "DocuHub Interno"
    API_V1_STR: str = "/api/v1"

    # Lee desde las variables de entorno inyectadas por Docker Compose
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # Rutas del sistema de archivos
    DOCS_DIRECTORY: str = "/docs_source"

    class Config:
        case_sensitive = True

# Instancia única que será importada por otros módulos
settings = Settings()