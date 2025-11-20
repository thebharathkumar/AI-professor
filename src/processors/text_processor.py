"""
Text processing utilities for cleaning and normalizing text
"""
import re
import logging
from typing import List

logger = logging.getLogger(__name__)


class TextProcessor:
    """Utilities for text cleaning and normalization"""

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:\-\'"()\[\]]', '', text)

        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")

        return text.strip()

    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        """
        Split text into sentences

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        # Simple sentence splitting (can be improved with NLTK or spaCy)
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace in text"""
        # Replace tabs with spaces
        text = text.replace('\t', ' ')

        # Remove multiple newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)

        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)

        return text.strip()

    @staticmethod
    def remove_urls(text: str) -> str:
        """Remove URLs from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.sub(url_pattern, '', text)

    @staticmethod
    def remove_email(text: str) -> str:
        """Remove email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.sub(email_pattern, '', text)
