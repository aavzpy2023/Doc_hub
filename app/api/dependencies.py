# /app/api/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from ..core import security
from ..core.config import settings
from ..db import models, schemas
from ..db.database import get_db
from ..services import user_service # Asumimos que este servicio existe

# Esta es la URL donde el frontend enviará el usuario y la contraseña para obtener un token.
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    """
    Dependencia para obtener el usuario actual a partir de un token JWT.
    """
    try:
        payload = security.decode_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo validar las credenciales",
            )
        token_data = schemas.TokenData(username=payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales",
        )
    
    user = user_service.get_user_by_username(db, username=token_data.username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Dependencia para obtener el usuario actual que además esté activo.
    Se usa en la mayoría de los endpoints protegidos.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo.")
    return current_user


def get_current_admin_user(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    """
    Dependencia para obtener el usuario actual, verificando que sea un administrador.
    Se usa en endpoints que requieren privilegios de administrador.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="El usuario no tiene suficientes privilegios."
        )
    return current_user