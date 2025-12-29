"""
OCR Service
Handles text extraction from images using Tesseract.
"""
from pathlib import Path
from typing import Optional, Union

from PIL import Image


class OCRService:
    """Service for extracting text from images using OCR."""

    def __init__(self, language: str = "eng"):
        """
        Initialize OCR service.

        Args:
            language: Tesseract language code (e.g., "eng", "fra", "deu")
        """
        self.language = language
        self._verify_tesseract()

    def _verify_tesseract(self):
        """Verify Tesseract is installed and accessible."""
        try:
            import pytesseract

            # Try to get tesseract version
            pytesseract.get_tesseract_version()

        except ImportError:
            raise RuntimeError(
                "pytesseract not installed. Run: pip install pytesseract"
            )
        except Exception as e:
            if "not installed" in str(e).lower() or "not found" in str(e).lower():
                raise RuntimeError(
                    "Tesseract OCR is not installed. Install it:\n"
                    "  macOS: brew install tesseract\n"
                    "  Ubuntu: sudo apt install tesseract-ocr\n"
                    "  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
                )
            raise

    def extract_text(self, image: Union[Image.Image, Path, str]) -> str:
        """
        Extract text from an image.

        Args:
            image: PIL Image, file path, or path string

        Returns:
            Extracted text
        """
        import pytesseract

        # Load image if path provided
        if isinstance(image, (str, Path)):
            image = Image.open(image)

        # Preprocess image for better OCR
        processed = self._preprocess_image(image)

        # Run OCR
        text = pytesseract.image_to_string(
            processed,
            lang=self.language,
            config='--psm 6'  # Assume uniform block of text
        )

        return self._clean_text(text)

    def extract_with_confidence(self, image: Union[Image.Image, Path, str]) -> dict:
        """
        Extract text with confidence scores.

        Args:
            image: PIL Image or file path

        Returns:
            Dict with text and confidence data
        """
        import pytesseract

        if isinstance(image, (str, Path)):
            image = Image.open(image)

        processed = self._preprocess_image(image)

        # Get detailed data
        data = pytesseract.image_to_data(
            processed,
            lang=self.language,
            output_type=pytesseract.Output.DICT
        )

        # Calculate average confidence for non-empty text
        confidences = [
            int(conf) for conf, text in zip(data['conf'], data['text'])
            if text.strip() and int(conf) > 0
        ]

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        # Get full text
        text = pytesseract.image_to_string(processed, lang=self.language)

        return {
            "text": self._clean_text(text),
            "confidence": avg_confidence,
            "word_count": len([t for t in data['text'] if t.strip()])
        }

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR results.

        Args:
            image: Input image

        Returns:
            Preprocessed image
        """
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Convert to grayscale
        gray = image.convert('L')

        # Increase contrast
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(gray)
        enhanced = enhancer.enhance(1.5)

        # Increase sharpness
        enhancer = ImageEnhance.Sharpness(enhanced)
        sharpened = enhancer.enhance(2.0)

        return sharpened

    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text.

        Args:
            text: Raw OCR text

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            # Strip whitespace
            line = line.strip()

            # Skip empty lines at start
            if not cleaned_lines and not line:
                continue

            cleaned_lines.append(line)

        # Remove trailing empty lines
        while cleaned_lines and not cleaned_lines[-1]:
            cleaned_lines.pop()

        # Join with single newlines
        text = '\n'.join(cleaned_lines)

        # Fix common OCR errors
        text = text.replace('|', 'I')  # Pipe to I
        text = text.replace('0', 'O') if text.isalpha() else text  # Zero to O in words

        return text

    def set_language(self, language: str):
        """
        Set OCR language.

        Args:
            language: Tesseract language code
        """
        self.language = language

    def get_available_languages(self) -> list:
        """
        Get list of available Tesseract languages.

        Returns:
            List of language codes
        """
        try:
            import pytesseract
            return pytesseract.get_languages()
        except Exception:
            return ["eng"]  # Default to English
