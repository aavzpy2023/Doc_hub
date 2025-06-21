
import os
import aiofiles # Para operaciones de archivo asíncronas
from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.api.dependencies import get_current_active_user # Asumiendo que quieres proteger estos endpoints
from app.db.models import User # Para el tipado de current_user

router = APIRouter()

# Directorio base donde están los documentos del proyecto dentro del contenedor
# Montado desde ./docs en el host a /docs_source en el contenedor app
DOCS_SOURCE_DIR = "/docs_source"

class FileNode(BaseModel):
    name: str
    path: str # Ruta relativa al DOCS_SOURCE_DIR
    type: str # 'file' o 'directory'
    children: Optional[List['FileNode']] = None

FileNode.model_rebuild() # Para la referencia recursiva de 'FileNode' en 'children'

class DocumentContent(BaseModel):
    content: str

def get_project_file_tree_recursive(root_dir: str, current_path: str = "") -> List[FileNode]:
    """
    Construye recursivamente el árbol de archivos y directorios,
    filtrando por archivos .md y listando directorios.
    """
    tree_nodes: List[FileNode] = []
    try:
        full_current_path = os.path.join(root_dir, current_path)
        if not os.path.exists(full_current_path) or not os.path.isdir(full_current_path):
            return []

        for item in sorted(os.listdir(full_current_path)):
            item_path_abs = os.path.join(full_current_path, item)
            item_path_rel = os.path.join(current_path, item) # Ruta relativa a DOCS_SOURCE_DIR

            if os.path.isdir(item_path_abs):
                children = get_project_file_tree_recursive(root_dir, item_path_rel)
                # Solo incluir directorios si tienen archivos .md o subdirectorios con .md (opcional, para no mostrar vacíos)
                # if children: # Descomentar si no quieres directorios vacíos (sin .md dentro)
                tree_nodes.append(FileNode(name=item, path=item_path_rel, type="directory", children=children))
            elif os.path.isfile(item_path_abs) and item.lower().endswith(".md"):
                tree_nodes.append(FileNode(name=item, path=item_path_rel, type="file"))
    except Exception as e:
        # Loggear el error sería bueno aquí
        print(f"Error traversing directory {full_current_path}: {e}")
        return [] # Retornar lista vacía en caso de error de permisos u otros
    return tree_nodes

def secure_join(base: str, user_path: str) -> str:
    """
    Une de forma segura la ruta base con la ruta proporcionada por el usuario,
    previniendo path traversal.
    """
    # Normalizar la ruta del usuario para resolver '..' etc.
    normalized_user_path = os.path.normpath(user_path)

    # Si la ruta normalizada comienza con '..' o es absoluta, es sospechosa
    if normalized_user_path.startswith("..") or os.path.isabs(normalized_user_path):
        raise HTTPException(status_code=400, detail="Ruta inválida o maliciosa.")

    # Construir la ruta completa
    full_path = os.path.normpath(os.path.join(base, normalized_user_path))

    # Verificar que la ruta resultante esté dentro del directorio base
    if not full_path.startswith(os.path.normpath(base) + os.sep) and full_path != os.path.normpath(base):
         # La segunda condición (full_path != os.path.normpath(base)) es para permitir el acceso al directorio base mismo si es necesario.
         # En este caso, user_path sería vacío o '.', lo cual es seguro.
        raise HTTPException(status_code=403, detail="Acceso prohibido a la ruta especificada.")

    return full_path


@router.get("/tree", response_model=List[FileNode], summary="Listar archivos y directorios de /docs_source")
async def list_project_docs(current_user: User = Depends(get_current_active_user)):
    if not os.path.exists(DOCS_SOURCE_DIR) or not os.path.isdir(DOCS_SOURCE_DIR):
        raise HTTPException(status_code=404, detail=f"Directorio fuente '{DOCS_SOURCE_DIR}' no encontrado en el servidor.")

    tree = get_project_file_tree_recursive(DOCS_SOURCE_DIR)
    return tree

@router.get("/content/{file_path:path}", response_model=DocumentContent, summary="Obtener contenido de un archivo de /docs_source")
async def get_project_doc_content(file_path: str, current_user: User = Depends(get_current_active_user)):
    try:
        abs_file_path = secure_join(DOCS_SOURCE_DIR, file_path)
        if not os.path.isfile(abs_file_path) or not abs_file_path.lower().endswith(".md"):
            raise HTTPException(status_code=404, detail="Archivo no encontrado o no es un archivo Markdown.")

        async with aiofiles.open(abs_file_path, mode="r", encoding="utf-8") as f:
            content = await f.read()
        return DocumentContent(content=content)
    except HTTPException: # Re-lanzar HTTPExceptions de secure_join o de aquí
        raise
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
    except Exception as e:
        # Loggear el error
        print(f"Error leyendo archivo {file_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al leer el archivo: {str(e)}")

@router.post("/content/{file_path:path}", summary="Guardar contenido de un archivo en /docs_source")
async def save_project_doc_content(
    file_path: str,
    payload: DocumentContent = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    try:
        abs_file_path = secure_join(DOCS_SOURCE_DIR, file_path)

        # Asegurarse que el directorio padre existe, si no, crearlo (opcional, depende del caso de uso)
        # dir_name = os.path.dirname(abs_file_path)
        # if not os.path.exists(dir_name):
        #     os.makedirs(dir_name, exist_ok=True)

        if not abs_file_path.lower().endswith(".md"):
             raise HTTPException(status_code=400, detail="Solo se pueden guardar archivos Markdown (.md).")

        async with aiofiles.open(abs_file_path, mode="w", encoding="utf-8") as f:
            await f.write(payload.content)
        return JSONResponse(status_code=200, content={"message": "Archivo guardado exitosamente."})
    except HTTPException:
        raise
    except Exception as e:
        # Loggear el error
        print(f"Error guardando archivo {file_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al guardar el archivo: {str(e)}")
