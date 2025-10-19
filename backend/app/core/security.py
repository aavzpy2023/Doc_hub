# /app/core/security.py

from datetime import datetime, timedelta
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# 1. Contexto de Passlib para el Hashing de Contraseñas
#    Usamos bcrypt, que es el estándar recomendado para contraseñas.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 2. Funciones de Contraseña


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if a plain text password matches its hashed version.

    Args:
        plain_password (str): The password in plain text.
        hashed_password (str): The hashed password from the database.

    Returns:
        bool: True if passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generates a hash for a plain text password.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


# 3. Funciones de Token JWT (JSON Web Token)


def create_access_token(subject: Any, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a new JWT access token.

    Args:
        subject (Any): The subject of the token (typically the user ID or username).
        expires_delta (Optional[timedelta]): The lifespan of the token. If not provided,
                                             the default from settings is used.

    Returns:
        str: The encoded JWT token.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # The token 'payload' contains the data we want to store within it.
    # 'exp' (expiration) and 'sub' (subject) are standard JWT claims.
    to_encode = {"exp": expire, "sub": str(subject)}

    encoded_jwt = jwt.encode(
        claims=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[str]:
    """
    Decodes a JWT token to retrieve its 'subject'.

    Args:
        token (str): The JWT token to decode.

    Returns:
        Optional[str]: The subject of the token if it's valid, otherwise None.
    """
    try:
        payload = jwt.decode(
            token=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # Extract the 'subject' from payload
        return payload.get("sub")
    except JWTError:
        # If the token has expired, has an invalid signature, etc., jose will raise an error.
        # In that case, we return None.
        return None
