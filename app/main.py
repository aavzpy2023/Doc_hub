# /app/main.py
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse
import os
import subprocess # Para ejecutar comandos del sistema

# --- Configuración ---
# Ahora los documentos estarán en una carpeta montada
DOCS_DIRECTORY = "/docs_source" 

# --- Aplicación FastAPI ---
app = FastAPI()

# No necesitamos servir estáticos desde FastAPI, Nginx lo hará.
# Pero dejamos el endpoint que sirve el HTML del editor.

@app.get("/", response_class=HTMLResponse)
async def get_editor_page():
    # El HTML se mantiene igual, pero lo separamos para claridad
    # En un proyecto real, esto estaría en un archivo /app/static/editor.html
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>DocuHub - Editor</title>
        <link rel="stylesheet" href="https://unpkg.com/easymde/dist/easymde.min.css">
        <script src="https://unpkg.com/easymde/dist/easymde.min.js"></script>
        <style>/* Estilos CSS aquí o en un archivo externo */</style>
    </head>
    <body>
        <h1>DocuHub Editor</h1>
        <div id="file-list"></div>
        <textarea id="markdown-editor"></textarea>
        <button id="save-button">Guardar</button>
        <button id="publish-button">Publicar Sitio</button>
        <div id="status"></div>
        <script>
            // Lógica JS aquí o en un archivo externo
            // El JS deberá ser actualizado para listar archivos y tener el botón de publicar
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/documents")
async def list_documents():
    """API para listar los archivos .md disponibles."""
    try:
        files = [f for f in os.listdir(DOCS_DIRECTORY) if f.endswith('.md')]
        return {"documents": files}
    except FileNotFoundError:
        return {"documents": []}

@app.get("/api/documents/{filename}")
async def get_document(filename: str):
    """API para leer el contenido de un archivo .md."""
    filepath = os.path.join(DOCS_DIRECTORY, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    with open(filepath, "r", encoding="utf-8") as f:
        return {"content": f.read()}

@app.post("/api/documents/{filename}")
async def save_document(filename: str, payload: dict = Body(...)):
    """API para guardar contenido en un archivo .md."""
    content = payload.get("content", "")
    filepath = os.path.join(DOCS_DIRECTORY, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return {"message": "Documento guardado."}

# --- NUEVO ENDPOINT ---
@app.post("/api/publish")
async def publish_site():
    """
    Ejecuta el comando 'mkdocs build' para generar el sitio estático.
    """
    try:
        # Creamos un archivo de configuración básico para MkDocs al vuelo
        mkdocs_config = f"""
        site_name: Documentación de Proyectos
        theme:
          name: material
        nav:
        """
        # Añadir archivos a la navegación
        files = sorted([f for f in os.listdir(DOCS_DIRECTORY) if f.endswith('.md')])
        for f in files:
            mkdocs_config += f"  - '{f.replace('_', ' ').replace('.md', '')}': '{f}'\n"
        
        with open(os.path.join(DOCS_DIRECTORY, "mkdocs.yml"), "w") as f:
            f.write(mkdocs_config)

        # Ejecutamos el comando de build
        # MkDocs generará el sitio en la carpeta /docs_build/site
        result = subprocess.run(
            ["mkdocs", "build", "-f", "mkdocs.yml", "-d", "/docs_build/site"],
            cwd=DOCS_DIRECTORY,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Error en MkDocs: {result.stderr}")
        
        return {"message": "Sitio publicado con éxito."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
