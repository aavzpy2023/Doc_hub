# /app/api/documents.py

from fastapi import APIRouter, Depends, HTTPException, Body, status
from fastapi.responses import FileResponse
from typing import List, Dict, Any
import tempfile
import os
import subprocess
import yaml
from pathlib import Path

# Importaciones de nuestra aplicación
from ..api import dependencies
from ..db import models
from ..core.config import settings
from ..services import document_service # Usaremos el servicio para la lógica de Git

# Creamos un nuevo router. Todos los endpoints definidos aquí
# serán añadidos a la aplicación principal.
router = APIRouter()


@router.get("/tree", response_model=List[Dict[str, Any]])
def list_document_tree(
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    """
    Endpoint para listar la estructura jerárquica de todos los documentos.
    Devuelve una estructura de árbol para que el frontend la renderice.
    """
    try:
        return document_service.list_documents()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar los documentos: {e}"
        )


@router.get("/content/{file_path:path}", response_model=Dict[str, str])
def read_document_content(
    file_path: str,
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    """
    Endpoint para obtener el contenido de un archivo Markdown específico.
    """
    content = document_service.get_document_content(file_path)
    if content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")
    
    return {"path": file_path, "content": content}


@router.post("/content/{file_path:path}")
def save_document_content(
    file_path: str,
    payload: dict = Body(...),
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    """
    Endpoint para guardar el contenido de un archivo y crear un commit en Git.
    Utiliza el document_service para encapsular la lógica.
    """
    content = payload.get("content", "")
    success = document_service.save_document_content(
        relative_path=file_path, content=content, author_name=current_user.username
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al guardar el documento.")
    
    return {"message": "Documento guardado y versionado con éxito."}


# /app/api/documents.py (Fragmento del endpoint /publish)

@router.post("/publish")
def publish_site(
    current_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Ejecuta 'mkdocs build' para generar el sitio estático.
    """
    try:
        # 1. Obtenemos la estructura de navegación desde el servicio
        nav_structure = document_service.generate_mkdocs_nav()
        
        # 2. Creamos el diccionario de configuración
        mkdocs_config = {
            'site_name': 'Documentación de Proyectos DATAZUCAR',
            'theme': {
                'name': 'material',
                'features': ['navigation.tabs', 'navigation.sections', 'navigation.expand']
            },
            'nav': nav_structure
        }
        
        # 3. Escribimos el archivo de configuración
        docs_path = Path(settings.DOCS_DIRECTORY)
        with open(docs_path / "mkdocs.yml", "w", encoding="utf-8") as f:
            yaml.dump(mkdocs_config, f, allow_unicode=True, default_flow_style=False)

        # 4. Ejecutamos el comando de build
        subprocess.run(
            ["mkdocs", "build", "-f", "mkdocs.yml", "-d", "/docs_build/site", "--clean"],
            cwd=docs_path.as_posix(),
            check=True
        )
        
        return {"message": "Sitio publicado con éxito."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al publicar el sitio: {str(e)}")


@router.get("/pdf/{file_path:path}")
def generate_pdf_from_document(
    file_path: str,
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    """
    Genera un PDF a partir de un archivo Markdown usando Pandoc.
    """
    source_path = Path(settings.DOCS_DIRECTORY) / file_path
    if not source_path.exists() or not source_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo Markdown no encontrado")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
        output_pdf_path = tmp_pdf.name
    
    try:
        # Comando Pandoc para generar el PDF
        pandoc_command = [
            "pandoc", str(source_path),
            "--pdf-engine=xelatex",
            "-o", output_pdf_path,
            "-V", "documentclass=article",
            "-V", "mainfont=Calibri",
            "-V", "fontsize=11pt",
            "-V", "geometry:margin=2.5cm",
            "-V", r"header-includes=\usepackage{fancyhdr}\pagestyle{fancy}\fancyhf{}\rhead{" + source_path.parent.name.replace('_', ' ') + r"}\cfoot{\thepage}"
        ]

        subprocess.run(pandoc_command, check=True, capture_output=True, text=True)

        return FileResponse(
            path=output_pdf_path,
            media_type='application/pdf',
            filename=f"{source_path.stem}.pdf"
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al generar el PDF: {e.stderr}")
    finally:
        if os.path.exists(output_pdf_path):
            os.remove(output_pdf_path)