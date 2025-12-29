"""
Screenshot Service
Handles screen capture and page turn simulation.
"""
from pathlib import Path
from typing import Optional
from datetime import datetime
import io

from PIL import Image


class ScreenshotService:
    """Service for capturing screenshots and simulating page turns."""

    def __init__(self, save_dir: Optional[Path] = None):
        if save_dir is None:
            self.save_dir = Path(__file__).parent.parent.parent / "data" / "screenshots"
        else:
            self.save_dir = Path(save_dir)

        self.save_dir.mkdir(parents=True, exist_ok=True)

    def capture_screen(self, region: Optional[tuple] = None) -> Image.Image:
        """
        Capture a screenshot of the screen.

        Args:
            region: Optional tuple (x, y, width, height) to capture specific region

        Returns:
            PIL Image of the screenshot
        """
        try:
            import pyautogui

            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()

            return screenshot

        except ImportError:
            raise RuntimeError("pyautogui not installed. Run: pip install pyautogui")
        except Exception as e:
            raise RuntimeError(f"Screenshot failed: {str(e)}")

    def capture_and_save(self, region: Optional[tuple] = None) -> Path:
        """
        Capture a screenshot and save it to disk.

        Args:
            region: Optional region to capture

        Returns:
            Path to saved screenshot
        """
        screenshot = self.capture_screen(region)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"screenshot_{timestamp}.png"
        filepath = self.save_dir / filename

        screenshot.save(filepath)
        return filepath

    def simulate_page_turn(self, key: str = "right", delay: float = 0.1):
        """
        Simulate a page turn by pressing a key.

        Args:
            key: Key to press (e.g., "right", "left", "space")
            delay: Delay after key press
        """
        try:
            import pyautogui
            import time

            pyautogui.press(key)
            time.sleep(delay)

        except ImportError:
            raise RuntimeError("pyautogui not installed. Run: pip install pyautogui")
        except Exception as e:
            raise RuntimeError(f"Page turn failed: {str(e)}")

    def get_window_list(self) -> list:
        """
        Get list of visible windows (platform-specific).

        Returns:
            List of window titles
        """
        try:
            import pyautogui

            # pyautogui doesn't have window listing, return empty
            # This would need platform-specific implementation
            return []

        except ImportError:
            return []

    def focus_window(self, window_title: str) -> bool:
        """
        Attempt to focus a window by title.

        Args:
            window_title: Partial window title to match

        Returns:
            True if window was focused
        """
        # Platform-specific implementation would go here
        # For now, return False and let user manually focus
        return False

    def crop_to_content(self, image: Image.Image, padding: int = 10) -> Image.Image:
        """
        Attempt to crop image to just the content area.

        Args:
            image: Input image
            padding: Pixels of padding to keep around content

        Returns:
            Cropped image
        """
        # Convert to grayscale for analysis
        gray = image.convert('L')

        # Get bounding box of non-white content
        bbox = gray.getbbox()

        if bbox:
            # Add padding
            x1, y1, x2, y2 = bbox
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(image.width, x2 + padding)
            y2 = min(image.height, y2 + padding)

            return image.crop((x1, y1, x2, y2))

        return image

    def image_to_bytes(self, image: Image.Image, format: str = "PNG") -> bytes:
        """
        Convert PIL Image to bytes.

        Args:
            image: PIL Image
            format: Output format

        Returns:
            Image as bytes
        """
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        return buffer.getvalue()
