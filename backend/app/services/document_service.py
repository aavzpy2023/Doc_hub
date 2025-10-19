import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import git

from app.core.config import settings


class DocumentService:
    """
    Business layer service to handle document-related logic.
    Encapsulates all interaction with the filesystem and the Git repository,
    keeping the API controllers clean and focused on HTTP concerns.
    """

    def __init__(self, docs_path: str = settings.DOCS_DIRECTORY):
        """
        Initializes the service, ensuring the documents directory
        and the Git repository exist. If the repo doesn't exist, it's initialized.

        Args:
            docs_path (str): The root path for the documents directory.
        """
        self.docs_path = Path(docs_path)
        if not self.docs_path.exists():
            self.docs_path.mkdir(parents=True)

        try:
            self.repo = git.Repo(self.docs_path)
        except git.InvalidGitRepositoryError:
            self.repo = git.Repo.init(self.docs_path)

    def _get_full_path(self, relative_path: str) -> Path:
        """
        Builds and validates a full, secure path for a file.
        Prevents path traversal attacks by ensuring the resolved path
        is within the configured documents directory.

        Args:
            relative_path (str): The user-provided relative path.

        Raises:
            ValueError: If the path is determined to be outside the allowed directory.

        Returns:
            Path: A resolved, secure Path object.
        """
        full_path = (self.docs_path / relative_path).resolve()
        if not full_path.is_relative_to(self.docs_path.resolve()):
            raise ValueError("Path traversal attempt detected.")
        return full_path

    def list_documents(self) -> List[Dict[str, Any]]:
        """
        Lists all documents and directories recursively to build a file tree.

        Returns:
            List[Dict[str, Any]]: A hierarchical list of dictionaries
                                  representing the file and directory structure.
        """

        def build_tree(current_path: Path):
            tree = []
            for item in sorted(current_path.iterdir()):
                if item.name.startswith(".") or item.name == "mkdocs.yml":
                    continue

                relative_path = item.relative_to(self.docs_path).as_posix()
                if item.is_dir():
                    tree.append(
                        {
                            "name": item.name,
                            "type": "directory",
                            "path": relative_path,
                            "children": build_tree(item),
                        }
                    )
                elif item.is_file() and item.suffix == ".md":
                    tree.append(
                        {"name": item.name, "type": "file", "path": relative_path}
                    )
            return tree

        return build_tree(self.docs_path)

    def get_document_content(self, relative_path: str) -> Optional[str]:
        """
        Reads the content of a specific Markdown file.

        Args:
            relative_path (str): The relative path of the file to read.

        Returns:
            Optional[str]: The content of the file as a string, or None if not found.
        """
        try:
            full_path = self._get_full_path(relative_path)
            return full_path.read_text(encoding="utf-8")
        except (FileNotFoundError, ValueError):
            return None

    def save_document_content(
        self, relative_path: str, content: str, author_name: str
    ) -> bool:
        """
        Saves a document's content and creates a Git commit.
        This is an atomic operation: it writes and then versions.

        Args:
            relative_path (str): The file path relative to the documents directory.
            content (str): The new content of the file.
            author_name (str): The user making the change, for the commit message.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        try:
            full_path = self._get_full_path(relative_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")

            self.repo.git.add(str(full_path))
            if self.repo.is_dirty(path=str(full_path)):
                self.repo.git.commit(
                    "-m", f"Doc '{relative_path}' updated by {author_name}"
                )
            return True
        except Exception as e:
            print(f"Error saving document {relative_path}: {e}")
            # Simple rollback logic on failure
            try:
                self.repo.git.reset("--hard", "HEAD")
            except git.GitCommandError:
                pass
            return False

    def generate_mkdocs_nav(self) -> List[Dict[str, Any]]:
        """
        Generates the hierarchical navigation structure for the mkdocs.yml file.
        This allows MkDocs to build a site with a nested menu that mirrors
        the directory structure.

        Returns:
            List[Dict[str, Any]]: A list formatted for the 'nav' key in mkdocs.yml.
        """

        def build_nav(current_path: Path):
            nav_items = []
            for item in sorted(current_path.iterdir()):
                if item.name.startswith(".") or item.name == "mkdocs.yml":
                    continue

                relative_path = item.relative_to(self.docs_path).as_posix()

                if item.is_dir():
                    dir_name = item.name.replace("_", " ").title()
                    children_nav = build_nav(item)
                    if children_nav:
                        nav_items.append({dir_name: children_nav})
                elif item.is_file() and item.suffix == ".md":
                    file_name = item.stem.replace("_", " ").title()
                    nav_items.append({file_name: relative_path})
            return nav_items

        return build_nav(self.docs_path)


# A single instance is created (Singleton pattern) to be easily imported and used by other modules.
document_service = DocumentService()
