"""
Vector Store Service
Handles ChromaDB operations for document embeddings and retrieval.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings


class VectorStore:
    """Service for managing document embeddings in ChromaDB."""

    def __init__(self, persist_dir: Optional[Path] = None):
        if persist_dir is None:
            persist_dir = Path(__file__).parent.parent.parent / "data" / "chromadb"

        persist_dir = Path(persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB with persistence
        self.client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create the main collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"description": "Document embeddings for text analysis"}
        )

    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Number of overlapping characters between chunks

        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings near the chunk boundary
                for sep in ['. ', '.\n', '!\n', '?\n', '\n\n']:
                    last_sep = text[start:end].rfind(sep)
                    if last_sep > chunk_size // 2:
                        end = start + last_sep + len(sep)
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap

        return chunks

    def add_document(self, doc_id: str, content: str, name: str) -> int:
        """
        Add a document to the vector store.

        Args:
            doc_id: Unique document ID
            content: Document text content
            name: Document name for metadata

        Returns:
            Number of chunks indexed
        """
        # Remove existing chunks for this document
        self.delete_document(doc_id)

        # Chunk the content
        chunks = self._chunk_text(content)

        if not chunks:
            return 0

        # Prepare data for ChromaDB
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "doc_id": doc_id,
                "doc_name": name,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            for i in range(len(chunks))
        ]

        # Add to collection (ChromaDB will handle embeddings)
        self.collection.add(
            ids=ids,
            documents=chunks,
            metadatas=metadatas
        )

        return len(chunks)

    def is_document_indexed(self, doc_id: str) -> bool:
        """
        Check if a document is indexed in the vector store.

        Args:
            doc_id: Document ID

        Returns:
            True if document has indexed chunks
        """
        results = self.collection.get(
            where={"doc_id": doc_id},
            limit=1
        )
        return len(results["ids"]) > 0

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete all chunks for a document.

        Args:
            doc_id: Document ID

        Returns:
            True if any chunks were deleted
        """
        try:
            # Get all chunk IDs for this document
            results = self.collection.get(
                where={"doc_id": doc_id}
            )

            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                return True

        except Exception:
            pass

        return False

    def search(
        self,
        query: str,
        doc_ids: Optional[List[str]] = None,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant chunks.

        Args:
            query: Search query
            doc_ids: Optional list of document IDs to search within
            n_results: Maximum number of results

        Returns:
            List of matching chunks with metadata
        """
        where_filter = None
        if doc_ids:
            if len(doc_ids) == 1:
                where_filter = {"doc_id": doc_ids[0]}
            else:
                where_filter = {"doc_id": {"$in": doc_ids}}

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )

        # Format results
        chunks = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                chunks.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None
                })

        return chunks

    def get_all_chunks(self, doc_id: str) -> List[Dict[str, Any]]:
        """
        Get all chunks for a document in order.

        Args:
            doc_id: Document ID

        Returns:
            List of chunks with metadata, ordered by chunk_index
        """
        results = self.collection.get(
            where={"doc_id": doc_id},
            include=["documents", "metadatas"]
        )

        chunks = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"]):
                chunks.append({
                    "content": doc,
                    "metadata": results["metadatas"][i] if results["metadatas"] else {}
                })

        # Sort by chunk index
        chunks.sort(key=lambda x: x["metadata"].get("chunk_index", 0))

        return chunks
