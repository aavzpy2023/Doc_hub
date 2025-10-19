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
from ..services import user_service  # Asumimos que este servicio existe

# This is the URL where the frontend will send the username and password to get a token.
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    """
    FastAPI dependency to get the current user from a JWT token.

    Retrieves the token from the request, decodes it, and fetches the
    corresponding user from the database.

    Raises:
        HTTPException(401): If the token is invalid or credentials cannot be validated.
        HTTPException(404): If the user from the token payload does not exist.

    Returns:
        models.User: The authenticated user object.
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
    FastAPI dependency to get the current user and ensure they are active.
    This is used in most protected endpoints.

    Raises:
        HTTPException(400): If the user is marked as inactive.

    Returns:
        models.User: The active, authenticated user object.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo.")
    return current_user


def get_current_admin_user(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    """
    FastAPI dependency to get the current user and ensure they are an admin.
    Used in endpoints that require administrative privileges.

    Raises:
        HTTPException(403): If the user is not an administrator.

    Returns:
        models.User: The active, authenticated admin user object.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene suficientes privilegios.",
        )
    return current_user
