# /app/api/documents.py

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List

from app.api import dependencies
from app.db import models
from app.services import document_service

router = APIRouter()

@router.get("/tree")
def list_document_tree(
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    """Lista la estructura jerárquica de todos los documentos."""
    return document_service.list_documents()


@router.get("/{file_path:path}")
def read_document(
    file_path: str,
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    """Obtiene el contenido de un archivo Markdown específico."""
    content = document_service.get_document_content(file_path)
    if content is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return {"path": file_path, "content": content}


@router.post("/{file_path:path}")
def save_document(
    file_path: str,
    payload: dict = Body(...),
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    """Guarda el contenido de un archivo y crea un commit."""
    content = payload.get("content", "")
    success = document_service.save_document_content(
        relative_path=file_path, content=content, author_name=current_user.username
    )
    if not success:
        raise HTTPException(status_code=500, detail="Error al guardar el documento.")
    return {"message": "Documento guardado con éxito."}
    
# ... Aquí irían los endpoints para generar PDF y publicar el sitio con MkDocs ...