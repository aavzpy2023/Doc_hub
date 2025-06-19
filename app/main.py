# /main.py
from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

# --- Configuración ---
MANUAL_FILE = "manual.md"

# --- Aplicación FastAPI ---
app = FastAPI()

# Montar el directorio 'static' para servir CSS y JS
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def get_editor_page():
    """Sirve la página principal del editor (index.html)."""
    # Para este proyecto simple, vamos a construir el HTML aquí mismo.
    # En un proyecto más grande, esto estaría en un archivo /static/index.html
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Editor de Manual</title>
        <link rel="stylesheet" href="/static/style.css">
        <!-- Importar marked.js desde un CDN para simplicidad -->
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    </head>
    <body>
        <header>
            <h1>Editor de Manual</h1>
            <div>
                <span id="status-message"></span>
                <button id="save-button">Guardar Cambios</button>
            </div>
        </header>
        <div class="editor-container">
            <textarea id="editor" spellcheck="false"></textarea>
            <div id="preview"></div>
        </div>
        <script src="/static/script.js"></script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/manual")
async def get_manual():
    """API para leer el contenido del archivo manual.md."""
    try:
        with open(MANUAL_FILE, "r", encoding="utf-8") as f:
            return {"content": f.read()}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="El archivo del manual no se encontró.")

@app.post("/api/manual")
async def save_manual(payload: dict = Body(...)):
    """API para guardar el nuevo contenido en manual.md."""
    content = payload.get("content", "")
    try:
        with open(MANUAL_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        return {"message": "Manual guardado con éxito."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar el archivo: {e}")
