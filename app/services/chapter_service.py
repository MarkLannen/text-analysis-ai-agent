"""
Chapter Service
Detects chapter boundaries in documents and provides chapter-level text access.
"""
import re
from typing import List, Dict, Optional
from pathlib import Path

from services.document_service import DocumentService


class ChapterService:
    """Service for detecting and managing chapter boundaries in documents."""

    def __init__(self, document_service: Optional[DocumentService] = None):
        self.document_service = document_service or DocumentService()

    def _clean_text_artifacts(self, text: str) -> str:
        """Remove common OCR/ebook artifacts that interfere with chapter detection."""
        # Remove Kindle progress markers like "42%"
        text = re.sub(r'^\d+%\s*$', '', text, flags=re.MULTILINE)
        # Remove "X minutes left in chapter" lines
        text = re.sub(r'^\d+ minutes? left in chapter.*$', '', text, flags=re.MULTILINE)
        return text

    def detect_chapters(self, doc_id: str) -> List[Dict]:
        """
        Detect chapter boundaries in a document.

        Args:
            doc_id: Document ID

        Returns:
            List of chapter dicts with index, number, title, start_char, end_char, char_count
        """
        doc = self.document_service.get_document(doc_id)
        if not doc:
            return []

        text = doc["content"]
        cleaned = self._clean_text_artifacts(text)
        lines = cleaned.split('\n')

        chapters = []
        chapter_starts = []  # (line_index, title, number)

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue

            # Pattern 1: Book-specific header (e.g. "GAUTAMA BUDDHA") followed by
            # a chapter number or section name on the next non-empty line
            if re.match(r'^[A-Z][A-Z\s]{3,}$', stripped) and len(stripped) > 5:
                next_line = self._get_next_nonempty_line(lines, i)
                if next_line is not None:
                    next_stripped = next_line.strip()
                    # Chapter number (digit), OCR artifact "s" for "5", or section names
                    if re.match(r'^\d+$', next_stripped):
                        chapter_starts.append((i, stripped, next_stripped))
                        continue
                    if next_stripped.lower() == 's':
                        # OCR artifact for "5"
                        chapter_starts.append((i, stripped, '5'))
                        continue
                    if re.match(r'^(INTRODUCTION|APPENDIX|PREFACE|PROLOGUE|EPILOGUE|CONCLUSION|FOREWORD|AFTERWORD)', next_stripped, re.IGNORECASE):
                        chapter_starts.append((i, next_stripped, next_stripped))
                        continue

            # Pattern 2: Generic "Chapter X" or "CHAPTER X" patterns
            match = re.match(r'^(?:CHAPTER|Chapter)\s+(\d+)', stripped)
            if match:
                chapter_num = match.group(1)
                # Look for a title on the next line
                next_line = self._get_next_nonempty_line(lines, i)
                title = next_line.strip() if next_line else f"Chapter {chapter_num}"
                chapter_starts.append((i, title, chapter_num))
                continue

            # Pattern 3: Standalone front/back matter keywords at line start
            if re.match(r'^(INTRODUCTION|APPENDIX|PREFACE|PROLOGUE|EPILOGUE|CONCLUSION|FOREWORD|AFTERWORD)\s*$', stripped, re.IGNORECASE):
                # Only if not already captured by Pattern 1
                already_captured = any(cs[0] == i for cs in chapter_starts)
                if not already_captured:
                    chapter_starts.append((i, stripped, stripped))

        if not chapter_starts:
            return []

        # Convert line indices to character offsets and build chapter list
        # Build cumulative char offset map for each line
        char_offsets = []
        offset = 0
        for line in lines:
            char_offsets.append(offset)
            offset += len(line) + 1  # +1 for newline

        for idx, (line_idx, title, number) in enumerate(chapter_starts):
            start_char = char_offsets[line_idx]

            if idx + 1 < len(chapter_starts):
                end_char = char_offsets[chapter_starts[idx + 1][0]]
            else:
                end_char = len(cleaned)

            chapters.append({
                "index": idx,
                "number": str(number),
                "title": title,
                "start_char": start_char,
                "end_char": end_char,
                "char_count": end_char - start_char
            })

        return chapters

    def _get_next_nonempty_line(self, lines: List[str], current_idx: int) -> Optional[str]:
        """Get the next non-empty line after current_idx, within 3 lines."""
        for j in range(current_idx + 1, min(current_idx + 4, len(lines))):
            if lines[j].strip():
                return lines[j]
        return None

    def get_chapter_text(self, doc_id: str, chapter_index: int) -> Optional[str]:
        """
        Get the full text of a specific chapter.

        Args:
            doc_id: Document ID
            chapter_index: Chapter index from detect_chapters

        Returns:
            Full chapter text, or None if not found
        """
        doc = self.document_service.get_document(doc_id)
        if not doc:
            return None

        chapters = self.get_chapters(doc_id)
        if not chapters:
            # Detect on the fly if not cached
            chapters = self.detect_chapters(doc_id)

        if chapter_index < 0 or chapter_index >= len(chapters):
            return None

        chapter = chapters[chapter_index]
        text = self._clean_text_artifacts(doc["content"])
        return text[chapter["start_char"]:chapter["end_char"]]

    def get_chapters(self, doc_id: str) -> List[Dict]:
        """Retrieve cached chapter metadata from document index."""
        return self.document_service.get_chapter_metadata(doc_id)

    def save_chapters(self, doc_id: str, chapters: List[Dict]):
        """Persist chapter metadata to document index."""
        self.document_service.save_chapter_metadata(doc_id, chapters)
