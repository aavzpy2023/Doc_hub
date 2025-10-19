# /app/db/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # Para obtener la fecha y hora actual de la BD

# Importamos la clase Base desde nuestro archivo de configuración de la BD.
# Todas nuestras tablas heredarán de esta clase.
from .database import Base

class User(Base):
    """
    Modelo de la tabla de Usuarios.
    Almacena la información de inicio de sesión y los roles.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # Relación uno-a-muchos: Un usuario puede tener muchos comentarios.
    comments = relationship("Comment", back_populates="owner")


class Comment(Base):
    """
    Modelo de la tabla de Comentarios.
    Almacena los comentarios asociados a cada documento.
    """
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    document_path = Column(String(512), index=True, nullable=False)
    content = Column(Text, nullable=False)
    
    # func.now() inserta la fecha y hora del servidor de la BD automáticamente.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Clave foránea que enlaza con la tabla de usuarios.
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relación muchos-a-uno: Un comentario pertenece a un solo usuario.
    owner = relationship("User", back_populates="comments")


class DocumentLock(Base):
    """
    Modelo de la tabla de Bloqueo de Documentos.
    Evita la edición simultánea.
    """
    __tablename__ = "document_locks"

    # La ruta del documento es la clave primaria. Solo puede haber un bloqueo por documento.
    document_path = Column(String(512), primary_key=True)
    
    locked_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Clave foránea que indica qué usuario tiene el bloqueo.
    locked_by_user_id = Column(Integer, ForeignKey("users.id"))
