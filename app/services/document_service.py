"""
Document Service
Handles document storage, retrieval, and management.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from PyPDF2 import PdfReader


class DocumentService:
    """Service for managing documents."""

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            # Default to data/documents relative to app
            self.data_dir = Path(__file__).parent.parent.parent / "data" / "documents"
        else:
            self.data_dir = Path(data_dir)

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.data_dir / "index.json"
        self._load_index()

    def _load_index(self):
        """Load the document index from disk."""
        if self.index_file.exists():
            with open(self.index_file, "r") as f:
                self.index = json.load(f)
        else:
            self.index = {"documents": {}}

    def _save_index(self):
        """Save the document index to disk."""
        with open(self.index_file, "w") as f:
            json.dump(self.index, f, indent=2, default=str)

    def _extract_text(self, content: bytes, mime_type: str) -> str:
        """Extract text content from various file formats."""
        if mime_type == "text/plain" or mime_type == "text/markdown":
            return content.decode("utf-8")

        elif mime_type == "application/pdf":
            # Save temporarily and read with PyPDF2
            import io
            pdf_reader = PdfReader(io.BytesIO(content))
            text_parts = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return "\n\n".join(text_parts)

        else:
            # Try to decode as text
            try:
                return content.decode("utf-8")
            except UnicodeDecodeError:
                raise ValueError(f"Unsupported file type: {mime_type}")

    def save_document(self, name: str, content: bytes, mime_type: str) -> str:
        """
        Save a document and return its ID.

        Args:
            name: Original filename
            content: File content as bytes
            mime_type: MIME type of the file

        Returns:
            Document ID
        """
        doc_id = str(uuid.uuid4())

        # Extract text content
        text_content = self._extract_text(content, mime_type)

        # Save the text content
        doc_path = self.data_dir / f"{doc_id}.txt"
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(text_content)

        # Update index
        self.index["documents"][doc_id] = {
            "id": doc_id,
            "name": name,
            "original_type": mime_type,
            "size": self._format_size(len(content)),
            "text_length": len(text_content),
            "created_at": datetime.now().isoformat(),
            "path": str(doc_path)
        }
        self._save_index()

        return doc_id

    def _format_size(self, size_bytes: int) -> str:
        """Format file size for display."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.

        Args:
            doc_id: Document ID

        Returns:
            Document dict with content, or None if not found
        """
        if doc_id not in self.index["documents"]:
            return None

        doc_meta = self.index["documents"][doc_id]
        doc_path = Path(doc_meta["path"])

        if not doc_path.exists():
            return None

        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()

        return {
            **doc_meta,
            "content": content
        }

    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents (metadata only).

        Returns:
            List of document metadata dicts
        """
        return list(self.index["documents"].values())

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document.

        Args:
            doc_id: Document ID

        Returns:
            True if deleted, False if not found
        """
        if doc_id not in self.index["documents"]:
            return False

        doc_meta = self.index["documents"][doc_id]
        doc_path = Path(doc_meta["path"])

        # Delete file
        if doc_path.exists():
            doc_path.unlink()

        # Remove from index
        del self.index["documents"][doc_id]
        self._save_index()

        return True

    def save_chapter_metadata(self, doc_id: str, chapters: List[Dict]) -> bool:
        """
        Save chapter metadata for a document.

        Args:
            doc_id: Document ID
            chapters: List of chapter dicts from ChapterService.detect_chapters

        Returns:
            True if saved, False if document not found
        """
        if doc_id not in self.index["documents"]:
            return False

        self.index["documents"][doc_id]["chapters"] = chapters
        self._save_index()
        return True

    def get_chapter_metadata(self, doc_id: str) -> List[Dict]:
        """
        Get cached chapter metadata for a document.

        Args:
            doc_id: Document ID

        Returns:
            List of chapter dicts, or empty list if none cached
        """
        if doc_id not in self.index["documents"]:
            return []

        return self.index["documents"][doc_id].get("chapters", [])

    def rename_document(self, doc_id: str, new_name: str) -> bool:
        """
        Rename a document.

        Args:
            doc_id: Document ID
            new_name: New display name

        Returns:
            True if renamed, False if not found
        """
        if doc_id not in self.index["documents"]:
            return False

        self.index["documents"][doc_id]["name"] = new_name
        self._save_index()
        return True
