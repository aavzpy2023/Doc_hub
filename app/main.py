# /app/main.py
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse
from pathlib import Path # Usaremos pathlib para un manejo de rutas más seguro y moderno
import os
import subprocess
import yaml # Necesitaremos PyYAML para generar el mkdocs.yml

# --- Configuración ---
DOCS_DIRECTORY = Path("/docs_source")

# --- Aplicación FastAPI ---
app = FastAPI()

# ... (El endpoint para servir el HTML del editor se mantiene igual) ...

# --- NUEVA LÓGICA DE API ---

@app.get("/api/documents/tree")
async def get_documents_tree():
    """API para listar la estructura de archivos y carpetas de forma recursiva."""
    def build_tree(current_path: Path):
        tree = []
        for item in sorted(current_path.iterdir()):
            # Omitir archivos y carpetas ocultos como .git
            if item.name.startswith('.'):
                continue
            
            relative_path = item.relative_to(DOCS_DIRECTORY).as_posix()
            if item.is_dir():
                tree.append({
                    "name": item.name,
                    "type": "directory",
                    "path": relative_path,
                    "children": build_tree(item)
                })
            elif item.is_file() and item.suffix == '.md':
                tree.append({
                    "name": item.name,
                    "type": "file",
                    "path": relative_path
                })
        return tree

    if not DOCS_DIRECTORY.exists():
        return []
    return build_tree(DOCS_DIRECTORY)


@app.get("/api/document/{file_path:path}")
async def get_document(file_path: str):
    """API para leer el contenido de un archivo, usando una ruta completa."""
    full_path = DOCS_DIRECTORY / file_path
    # Medida de seguridad para evitar Path Traversal
    if not full_path.resolve().is_relative_to(DOCS_DIRECTORY.resolve()):
         raise HTTPException(status_code=400, detail="Acceso a ruta no permitido.")
    
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
    return {"content": full_path.read_text(encoding="utf-8")}


@app.post("/api/document/{file_path:path}")
async def save_document(file_path: str, payload: dict = Body(...)):
    """API para guardar contenido en un archivo, usando una ruta completa."""
    content = payload.get("content", "")
    full_path = DOCS_DIRECTORY / file_path
    
    if not full_path.resolve().is_relative_to(DOCS_DIRECTORY.resolve()):
         raise HTTPException(status_code=400, detail="Acceso a ruta no permitido.")
    
    # Asegurarse de que el directorio padre exista
    full_path.parent.mkdir(parents=True, exist_ok=True)
    
    full_path.write_text(content, encoding="utf-8")
    return {"message": "Documento guardado."}


@app.post("/api/publish")
async def publish_site():
    """
    Ejecuta 'mkdocs build' generando un mkdocs.yml que refleja la jerarquía de carpetas.
    """
    try:
        # --- Generación de navegación jerárquica para mkdocs.yml ---
        def generate_nav(current_path: Path):
            nav_items = []
            for item in sorted(current_path.iterdir()):
                if item.name.startswith('.') or item.name == 'mkdocs.yml':
                    continue
                
                relative_path = item.relative_to(DOCS_DIRECTORY).as_posix()
                
                if item.is_dir():
                    # Para un directorio, creamos una sección y llamamos recursivamente
                    dir_name = item.name.replace('_', ' ').title()
                    children_nav = generate_nav(item)
                    if children_nav: # Solo añadir si tiene contenido
                        nav_items.append({dir_name: children_nav})
                elif item.is_file() and item.suffix == '.md':
                    # Para un archivo, creamos una entrada de navegación
                    file_name = item.stem.replace('_', ' ').title()
                    nav_items.append({file_name: relative_path})
            return nav_items

        nav_structure = generate_nav(DOCS_DIRECTORY)
        
        mkdocs_config = {
            'site_name': 'Documentación de Proyectos DATAZUCAR',
            'theme': {
                'name': 'material',
                'features': [
                    'navigation.tabs',
                    'navigation.sections',
                    'navigation.expand'
                ]
            },
            'nav': nav_structure
        }
        
        # Escribir el mkdocs.yml usando PyYAML para un formato correcto
        with open(DOCS_DIRECTORY / "mkdocs.yml", "w", encoding="utf-8") as f:
            yaml.dump(mkdocs_config, f, allow_unicode=True, default_flow_style=False)

        # Ejecutar el comando de build
        subprocess.run(
            ["mkdocs", "build", "-f", "mkdocs.yml", "-d", "/docs_build/site", "--clean"],
            cwd=DOCS_DIRECTORY.as_posix(),
            check=True # Lanza una excepción si el comando falla
        )
        
        return {"message": "Sitio publicado con éxito."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al publicar: {str(e)}")
