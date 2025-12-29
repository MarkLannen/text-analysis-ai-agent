"""
Ebook App Configurations
Settings for different ebook reader applications.
"""

EBOOK_APPS = {
    "kindle": {
        "name": "Amazon Kindle",
        "page_turn_key": "right",
        "tips": "Open Kindle app, maximize window, and hide toolbar if possible. Use single-page view for best results.",
        "window_title_pattern": "Kindle",
        "supported_platforms": ["macos", "windows"]
    },
    "apple_books": {
        "name": "Apple Books",
        "page_turn_key": "right",
        "tips": "Open Apple Books, enter full-screen mode (Cmd+Ctrl+F), and use single-page layout.",
        "window_title_pattern": "Books",
        "supported_platforms": ["macos"]
    },
    "kobo": {
        "name": "Kobo Desktop",
        "page_turn_key": "right",
        "tips": "Open Kobo app and maximize the reading window. Use single-page view.",
        "window_title_pattern": "Kobo",
        "supported_platforms": ["macos", "windows"]
    },
    "google_play": {
        "name": "Google Play Books",
        "page_turn_key": "right",
        "tips": "Open Google Play Books in Chrome. Use full-screen mode (F11) and single-page view.",
        "window_title_pattern": "Google Play Books",
        "is_web": True,
        "supported_platforms": ["macos", "windows", "linux"]
    },
    "nook": {
        "name": "Barnes & Noble Nook",
        "page_turn_key": "right",
        "tips": "Open Nook app and maximize window. Best results in single-page mode.",
        "window_title_pattern": "NOOK",
        "supported_platforms": ["windows"]
    },
    "calibre": {
        "name": "Calibre E-book Viewer",
        "page_turn_key": "space",
        "tips": "Open book in Calibre viewer. Use View > Single Page mode for best OCR results.",
        "window_title_pattern": "Calibre",
        "supported_platforms": ["macos", "windows", "linux"]
    },
    "adobe_digital": {
        "name": "Adobe Digital Editions",
        "page_turn_key": "right",
        "tips": "Open Adobe Digital Editions and maximize reading view.",
        "window_title_pattern": "Adobe Digital Editions",
        "supported_platforms": ["macos", "windows"]
    },
    "generic": {
        "name": "Generic / Other",
        "page_turn_key": "right",
        "tips": "Position your ebook reader window and make sure text is clearly visible. You may need to manually turn pages.",
        "window_title_pattern": None,
        "supported_platforms": ["macos", "windows", "linux"]
    }
}


def get_app_config(app_key: str) -> dict:
    """
    Get configuration for an ebook app.

    Args:
        app_key: App key from EBOOK_APPS

    Returns:
        App configuration dict
    """
    return EBOOK_APPS.get(app_key, EBOOK_APPS["generic"])


def get_supported_apps(platform: str = None) -> dict:
    """
    Get ebook apps supported on a platform.

    Args:
        platform: Platform name ("macos", "windows", "linux")

    Returns:
        Filtered dict of supported apps
    """
    if platform is None:
        return EBOOK_APPS

    return {
        key: config for key, config in EBOOK_APPS.items()
        if platform in config.get("supported_platforms", [])
    }
