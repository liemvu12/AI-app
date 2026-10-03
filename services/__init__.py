"""
Services package initialization
"""
from .translator import detect_language, translate_text
from .language_helper import process_prompt_for_learning, polish_engineering_english
from .agy_client import AGYClient

__all__ = [
    "detect_language",
    "translate_text",
    "process_prompt_for_learning",
    "polish_engineering_english",
    "AGYClient",
]
