# /app/services/document_service.py

import os
import git
from pathlib import Path
from typing import List, Optional, Dict, Any

from app.core.config import settings

class DocumentService:
    """
    Servicio para manejar la lógica de negocio relacionada con los documentos,
    incluyendo la interacción con el sistema de archivos y Git.
    """
    def __init__(self, docs_path: str = settings.DOCS_DIRECTORY):
        self.docs_path = Path(docs_path)
        if not self.docs_path.exists():
            self.docs_path.mkdir(parents=True)
        
        try:
            self.repo = git.Repo(self.docs_path)
        except git.InvalidGitRepositoryError:
            self.repo = git.Repo.init(self.docs_path)

    def _get_full_path(self, relative_path: str) -> Path:
        """Construye y valida la ruta completa y segura de un archivo."""
        full_path = (self.docs_path / relative_path).resolve()
        if not full_path.is_relative_to(self.docs_path.resolve()):
            raise ValueError("Acceso a ruta no permitido (Path Traversal).")
        return full_path

    def list_documents(self) -> List[Dict[str, Any]]:
        """Lista todos los documentos y directorios de forma jerárquica."""
        def build_tree(current_path: Path):
            tree = []
            for item in sorted(current_path.iterdir()):
                if item.name.startswith('.') or item.name == 'mkdocs.yml':
                    continue
                
                relative_path = item.relative_to(self.docs_path).as_posix()
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
        return build_tree(self.docs_path)

    def get_document_content(self, relative_path: str) -> Optional[str]:
        """Lee el contenido de un archivo Markdown."""
        try:
            full_path = self._get_full_path(relative_path)
            return full_path.read_text(encoding='utf-8')
        except (FileNotFoundError, ValueError):
            return None
        
    def save_document_content(self, relative_path: str, content: str, author_name: str) -> bool:
        """Guarda el contenido de un documento y realiza un commit en Git."""
        try:
            full_path = self._get_full_path(relative_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')

            self.repo.git.add(str(full_path))
            if self.repo.is_dirty(path=str(full_path)):
                self.repo.git.commit('-m', f"Doc '{relative_path}' actualizado por {author_name}")
            return True
        except Exception as e:
            print(f"Error al guardar documento {relative_path}: {e}")
            # Considerar un rollback de Git si el commit falla
            try:
                self.repo.git.reset('--hard', 'HEAD')
            except git.GitCommandError:
                pass # Puede fallar si no había nada que resetear
            return False
    
    def generate_mkdocs_nav(self) -> List[Dict[str, Any]]:
        """
        Genera la estructura de navegación jerárquica para el archivo mkdocs.yml.
        """
        def build_nav(current_path: Path):
            nav_items = []
            for item in sorted(current_path.iterdir()):
                if item.name.startswith('.') or item.name == 'mkdocs.yml':
                    continue
                
                relative_path = item.relative_to(self.docs_path).as_posix()
                
                if item.is_dir():
                    dir_name = item.name.replace('_', ' ').title()
                    children_nav = build_nav(item)
                    if children_nav:
                        nav_items.append({dir_name: children_nav})
                elif item.is_file() and item.suffix == '.md':
                    file_name = item.stem.replace('_', ' ').title()
                    nav_items.append({file_name: relative_path})
            return nav_items
        return build_nav(self.docs_path)

# Creamos una instancia única del servicio para que sea fácil de importar y usar
document_service = DocumentService()