"""Language detection module for Writer tool."""

from typing import Optional
from app.logger import logger


class LanguageDetector:
    """Detect language from text and user requests."""
    
    SUPPORTED_LANGUAGES = {
        'fr': 'French',
        'en': 'English'
    }
    
    def __init__(self, default_language: str = 'fr'):
        self.default_language = default_language
    
    def detect_from_text(self, text: str) -> str:
        """Detect language from text content."""
        try:
            from langdetect import detect
            detected = detect(text)
            return detected if detected in self.SUPPORTED_LANGUAGES else self.default_language
        except Exception as e:
            logger.warning(f"Language detection failed: {e}, using default")
            return self.default_language
    
    def detect_from_request(self, request: str) -> str:
        """Detect language from user request text."""
        french_keywords = ['écris', 'rapport', 'français', 'générer', 'cherche', 'résumé', 'explique', 'décris']
        english_keywords = ['write', 'report', 'english', 'generate', 'search', 'summary', 'explain', 'describe']
        
        request_lower = request.lower()
        
        french_score = sum(1 for kw in french_keywords if kw in request_lower)
        english_score = sum(1 for kw in english_keywords if kw in request_lower)
        
        if french_score > english_score:
            return 'fr'
        elif english_score > french_score:
            return 'en'
        else:
            return self.default_language
    
    def confirm_language(self, detected: str) -> str:
        """Confirm detected language with user."""
        logger.info(f"Detected language: {self.SUPPORTED_LANGUAGES.get(detected, detected)}")
        return detected
