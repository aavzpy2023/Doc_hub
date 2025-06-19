# /app/db/schemas.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# ==============================================================================
# Esquemas para la gestión de USUARIOS (Users)
# ==============================================================================

# --- Atributos base compartidos por todos los esquemas de usuario ---
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario único")
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    is_active: bool = True

# --- Esquema para la CREACIÓN de un usuario (recibido por la API) ---
# Hereda de UserBase y añade el campo de la contraseña.
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Contraseña del usuario")

# --- Esquema para la ACTUALIZACIÓN de un usuario (recibido por la API) ---
# Todos los campos son opcionales.
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)

# --- Esquema para representar un usuario que se DEVUELVE desde la API ---
# Hereda de UserBase y añade el 'id'. NUNCA debe devolver la contraseña.
class User(UserBase):
    id: int

    class Config:
        # Permite a Pydantic mapear automáticamente los datos desde un
        # objeto de SQLAlchemy a este schema.
        from_attributes = True


# ==============================================================================
# Esquemas para la gestión de COMENTARIOS (Comments)
# ==============================================================================

# --- Atributos base para un comentario ---
class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, description="Contenido del comentario")

# --- Esquema para la CREACIÓN de un comentario ---
class CommentCreate(CommentBase):
    document_path: str = Field(..., description="Ruta del documento al que pertenece el comentario")

# --- Esquema para representar un comentario que se DEVUELVE desde la API ---
# Incluye información del comentario y del usuario que lo creó.
class Comment(CommentBase):
    id: int
    document_path: str
    created_at: datetime
    owner_id: int
    owner: User  # Anida el schema 'User' para devolver los datos del propietario

    class Config:
        orm_mode = True


# ==============================================================================
# Esquemas para la gestión de DOCUMENTOS y su bloqueo
# ==============================================================================

# --- Esquema para los datos de un documento (enviados y recibidos) ---
class Document(BaseModel):
    path: str
    content: str

# --- Esquema para representar el estado de un bloqueo ---
class DocumentLock(BaseModel):
    document_path: str
    locked_at: datetime
    locked_by: User # Anida el schema 'User' para mostrar quién tiene el bloqueo

    class Config:
        orm_mode = True


# ==============================================================================
# Esquemas para la AUTENTICACIÓN (Login)
# ==============================================================================

# --- Esquema para la respuesta del token de acceso ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- Esquema para los datos contenidos dentro del token JWT ---
class TokenData(BaseModel):
    username: Optional[str] = None
