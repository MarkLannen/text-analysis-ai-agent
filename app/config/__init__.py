"""
Configuration package
Application settings and ebook app configurations.
"""
from .settings import Settings
from .ebook_apps import EBOOK_APPS, get_app_config, get_supported_apps

__all__ = [
    'Settings',
    'EBOOK_APPS',
    'get_app_config',
    'get_supported_apps'
]
