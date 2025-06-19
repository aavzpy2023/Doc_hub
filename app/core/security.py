# /app/core/security.py

from datetime import datetime, timedelta
from typing import Optional, Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# 1. Contexto de Passlib para el Hashing de Contraseñas
#    Usamos bcrypt, que es el estándar recomendado para contraseñas.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 2. Funciones de Contraseña

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su versión hasheada.

    Args:
        plain_password (str): La contraseña sin hashear.
        hashed_password (str): La contraseña hasheada desde la base de datos.

    Returns:
        bool: True si las contraseñas coinciden, False en caso contrario.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Genera el hash de una contraseña en texto plano.

    Args:
        password (str): La contraseña a hashear.

    Returns:
        str: La contraseña hasheada.
    """
    return pwd_context.hash(password)


# 3. Funciones de Token JWT (JSON Web Token)

def create_access_token(
    subject: Any, expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un nuevo token de acceso JWT.

    Args:
        subject (Any): El sujeto del token (generalmente el ID o username del usuario).
        expires_delta (Optional[timedelta]): Tiempo de vida del token. Si no se provee,
                                             se usa el valor de la configuración.

    Returns:
        str: El token JWT codificado.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # El 'payload' del token contiene los datos que queremos guardar en él.
    # 'exp' (expiration) y 'sub' (subject) son claims estándar de JWT.
    to_encode = {"exp": expire, "sub": str(subject)}
    
    encoded_jwt = jwt.encode(
        claims=to_encode, 
        key=settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[str]:
    """
    Decodifica un token JWT para obtener el 'subject' (ID/username del usuario).

    Args:
        token (str): El token JWT a decodificar.

    Returns:
        Optional[str]: El 'subject' del token si es válido, None en caso contrario.
    """
    try:
        payload = jwt.decode(
            token=token, 
            key=settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        # Extraemos el 'subject' del payload
        return payload.get("sub")
    except JWTError:
        # Si el token ha expirado, tiene una firma inválida, etc., jose lanzará un error.
        # En ese caso, devolvemos None.
        return None