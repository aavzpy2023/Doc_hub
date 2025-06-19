# /app/api/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api import dependencies
from app.db import models, schemas
from app.db.database import get_db
from app.services import user_service # Asumimos que este servicio existe

router = APIRouter()

@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_admin_user: models.User = Depends(dependencies.get_current_admin_user)
):
    """
    Crea un nuevo usuario en el sistema.
    Solo accesible para administradores.
    """
    user = user_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un usuario con este correo electrónico.",
        )
    return user_service.create_user(db, user_in=user_in)


@router.get("/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin_user: models.User = Depends(dependencies.get_current_admin_user)
):
    """
    Obtiene una lista de usuarios.
    Solo accesible para administradores.
    """
    users = user_service.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin_user: models.User = Depends(dependencies.get_current_admin_user)
):
    """
    Obtiene un usuario específico por su ID.
    Solo accesible para administradores.
    """
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user