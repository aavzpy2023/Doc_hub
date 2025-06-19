# /app/services/user_service.py

from sqlalchemy.orm import Session
from typing import List, Optional

from app.core import security
from app.db import models, schemas

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Obtiene un usuario por su ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Obtiene un usuario por su correo electrónico."""
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Obtiene un usuario por su nombre de usuario."""
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Obtiene una lista de usuarios con paginación."""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    """
    Crea un nuevo usuario en la base de datos.
    Hashea la contraseña antes de guardarla.
    """
    hashed_password = security.get_password_hash(user_in.password)
    db_user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
        is_active=user_in.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """
    Autentica a un usuario. Retorna el usuario si la autenticación es exitosa,
    de lo contrario retorna None.
    """
    user = get_user_by_username(db, username=username)
    if not user:
        return None
    if not security.verify_password(password, user.hashed_password):
        return None
    return user