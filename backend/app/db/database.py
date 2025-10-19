# /app/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Cambia la importación a una ruta relativa explícita desde la raíz del paquete 'app'
from ..core.config import settings # <-- CAMBIO CLAVE AQUÍ

# El resto del archivo se mantiene igual
engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()