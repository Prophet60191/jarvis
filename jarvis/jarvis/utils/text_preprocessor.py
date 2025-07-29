"""
Text preprocessing utilities for Jarvis TTS.

This module provides functions to clean and prepare text for text-to-speech
synthesis, removing markdown formatting and other elements that shouldn't be spoken.
"""

import re
import logging

logger = logging.getLogger(__name__)


def clean_text_for_tts(text: str) -> str:
    """
    Clean text for text-to-speech by removing markdown formatting and other
    elements that shouldn't be spoken aloud.
    
    Args:
        text: Raw text that may contain markdown formatting
        
    Returns:
        Cleaned text suitable for TTS
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Store original for logging
    original_text = text
    
    # Remove markdown formatting
    text = _remove_markdown_formatting(text)
    
    # Remove code blocks and inline code
    text = _remove_code_elements(text)
    
    # Clean up punctuation and symbols
    text = _clean_punctuation(text)
    
    # Normalize whitespace
    text = _normalize_whitespace(text)
    
    # Log if significant changes were made
    if len(original_text) - len(text) > 10:
        logger.debug(f"TTS text cleaned: {len(original_text)} -> {len(text)} chars")
    
    return text.strip()


def _remove_markdown_formatting(text: str) -> str:
    """Remove markdown formatting elements."""
    
    # Remove bold/italic markers (**text**, *text*, __text__, _text_)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold**
    text = re.sub(r'\*([^*]+)\*', r'\1', text)        # *italic*
    text = re.sub(r'__([^_]+)__', r'\1', text)          # __bold__
    text = re.sub(r'_([^_]+)_', r'\1', text)            # _italic_
    
    # Remove strikethrough (~~text~~)
    text = re.sub(r'~~([^~]+)~~', r'\1', text)
    
    # Remove headers (# ## ### etc.)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove horizontal rules (--- or ***)
    text = re.sub(r'^[-*]{3,}\s*$', '', text, flags=re.MULTILINE)
    
    # Remove blockquotes (> text)
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    
    # Remove list markers (- * + 1. 2. etc.)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    return text


def _remove_code_elements(text: str) -> str:
    """Remove code blocks and inline code."""
    
    # Remove code blocks (```code```)
    text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
    
    # Remove inline code (`code`)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    return text


def _clean_punctuation(text: str) -> str:
    """Clean up punctuation and symbols that shouldn't be spoken."""
    
    # Remove standalone asterisks and other markdown remnants
    text = re.sub(r'\s*\*+\s*', ' ', text)
    
    # Remove standalone underscores
    text = re.sub(r'\s*_+\s*', ' ', text)
    
    # Remove standalone hashes
    text = re.sub(r'\s*#+\s*', ' ', text)
    
    # Remove brackets around single words (like [word])
    text = re.sub(r'\[([^\]]+)\]', r'\1', text)
    
    # Clean up multiple punctuation marks
    text = re.sub(r'[.]{2,}', '.', text)
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[?]{2,}', '?', text)
    
    # Remove URLs (http/https links)
    text = re.sub(r'https?://[^\s]+', '', text)
    
    return text


def _normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove extra newlines
    text = re.sub(r'\n\s*\n', '\n', text)
    
    # Replace newlines with spaces for TTS
    text = text.replace('\n', ' ')
    
    return text


def test_text_cleaning():
    """Test the text cleaning function with common markdown examples."""
    test_cases = [
        ("**`open_rag_manager`**: Opens the Vault", "open_rag_manager: Opens the Vault"),
        ("*Hello* **world**!", "Hello world!"),
        ("Here's some `code` and **bold text**", "Here's some code and bold text"),
        ("# Header\n\nSome text", "Header Some text"),
        ("- Item 1\n- Item 2", "Item 1 Item 2"),
        ("Visit https://example.com for more", "Visit  for more"),
        ("Text with *** multiple *** asterisks", "Text with  multiple  asterisks"),
    ]
    
    print("🧪 Testing text cleaning function:")
    print("-" * 50)
    
    for original, expected in test_cases:
        cleaned = clean_text_for_tts(original)
        status = "✅" if cleaned.strip() == expected.strip() else "❌"
        print(f"{status} '{original}' -> '{cleaned}'")
        if cleaned.strip() != expected.strip():
            print(f"   Expected: '{expected}'")
    
    return True


if __name__ == "__main__":
    test_text_cleaning()
