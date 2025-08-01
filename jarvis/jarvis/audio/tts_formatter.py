#!/usr/bin/env python3
"""
TTS Formatter - Cleans up text for natural speech synthesis.

SEPARATION OF CONCERNS:
- This module ONLY handles text formatting for TTS
- It does NOT handle audio processing or speech synthesis
- It provides clean text output optimized for natural speech

SINGLE RESPONSIBILITY: Format text to sound natural when spoken by TTS
"""

import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class TTSFormatter:
    """
    Formats text for natural TTS speech synthesis.
    
    SINGLE RESPONSIBILITY: Text formatting for speech only.
    
    Handles:
    - Markdown formatting removal (* ** *** etc.)
    - Special character pronunciation
    - Number and abbreviation expansion
    - Punctuation optimization for speech
    """
    
    def __init__(self):
        """Initialize TTS formatter."""
        # Markdown patterns to clean
        self.markdown_patterns = [
            # Bold and italic patterns
            (r'\*\*\*(.*?)\*\*\*', r'\1'),  # ***bold italic*** -> text
            (r'\*\*(.*?)\*\*', r'\1'),      # **bold** -> text
            (r'\*(.*?)\*', r'\1'),          # *italic* -> text
            (r'__(.*?)__', r'\1'),          # __bold__ -> text
            (r'_(.*?)_', r'\1'),            # _italic_ -> text
            
            # Headers
            (r'^#{1,6}\s+(.+)$', r'\1'),    # # Header -> Header
            
            # Lists (handle both single line and multiline)
            (r'^\s*[-*+]\s+(.+)$', r'\1'),  # - item -> item
            (r'^\s*\d+\.\s+(.+)$', r'\1'),  # 1. item -> item
            (r'\s+-\s+', ' '),              # Remove - between items
            
            # Code blocks and inline code
            (r'```.*?```', ''),             # Remove code blocks
            (r'`([^`]+)`', r'\1'),          # `code` -> code
            
            # Links
            (r'\[([^\]]+)\]\([^)]+\)', r'\1'),  # [text](url) -> text
            (r'<([^>]+)>', r'\1'),          # <url> -> url
            
            # Strikethrough
            (r'~~(.*?)~~', r'\1'),          # ~~text~~ -> text
        ]
        
        # Special character replacements for speech
        self.speech_replacements = {
            # Mathematical symbols
            '+': ' plus ',
            '-': ' minus ',
            '=': ' equals ',
            '<': ' less than ',
            '>': ' greater than ',
            '<=': ' less than or equal to ',
            '>=': ' greater than or equal to ',
            '!=': ' not equal to ',
            
            # Programming symbols
            '&': ' and ',
            '|': ' or ',
            '&&': ' and ',
            '||': ' or ',
            '->': ' arrow ',
            '=>': ' arrow ',
            '::': ' double colon ',
            
            # Common abbreviations
            'e.g.': 'for example',
            'i.e.': 'that is',
            'etc.': 'and so on',
            'vs.': 'versus',
            'vs': 'versus',
            
            # Units (common ones)
            'ms': 'milliseconds',
            'sec': 'seconds',
            'min': 'minutes',
            'hr': 'hours',
            'km': 'kilometers',
            'mb': 'megabytes',
            'gb': 'gigabytes',
        }
        
        # Patterns that should be removed entirely
        self.remove_patterns = [
            r'\s*\n\s*',  # Multiple newlines -> single space
            r'\s{2,}',    # Multiple spaces -> single space
        ]
        
        logger.info("TTSFormatter initialized")
    
    def format_for_speech(self, text: str) -> str:
        """
        Format text for natural speech synthesis.
        
        Args:
            text: Raw text that may contain markdown and special characters
            
        Returns:
            Cleaned text optimized for TTS
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Start with the original text
        formatted_text = text
        
        # Step 1: Clean markdown formatting
        formatted_text = self._clean_markdown(formatted_text)
        
        # Step 2: Replace special characters for speech
        formatted_text = self._replace_special_characters(formatted_text)
        
        # Step 3: Clean up whitespace and formatting
        formatted_text = self._clean_whitespace(formatted_text)
        
        # Step 4: Handle numbers and abbreviations
        formatted_text = self._expand_abbreviations(formatted_text)
        
        # Step 5: Final cleanup
        formatted_text = self._final_cleanup(formatted_text)
        
        logger.debug(f"TTS formatting: '{text[:50]}...' -> '{formatted_text[:50]}...'")
        
        return formatted_text.strip()
    
    def _clean_markdown(self, text: str) -> str:
        """Remove markdown formatting."""
        for pattern, replacement in self.markdown_patterns:
            text = re.sub(pattern, replacement, text, flags=re.MULTILINE | re.DOTALL)
        return text
    
    def _replace_special_characters(self, text: str) -> str:
        """Replace special characters with speech-friendly versions."""
        for symbol, replacement in self.speech_replacements.items():
            # Handle different types of symbols differently
            if symbol in ['<=', '>=', '!=', '->', '=>', '::']:
                # Multi-character operators - replace directly
                text = text.replace(symbol, replacement)
            elif symbol in ['&', '+', '=', '<', '>']:
                # Single character operators - use spaces around them
                pattern = r'\s*' + re.escape(symbol) + r'\s*'
                text = re.sub(pattern, replacement, text)
            elif symbol in ['-']:
                # Dash - only replace when used as minus (with spaces)
                pattern = r'\s+' + re.escape(symbol) + r'\s+'
                text = re.sub(pattern, replacement, text)
            elif symbol in ['e.g.', 'i.e.', 'etc.', 'vs.', 'vs']:
                # Abbreviations - replace directly
                text = text.replace(symbol, replacement)
            else:
                # Other symbols - replace directly
                text = text.replace(symbol, replacement)
        return text
    
    def _clean_whitespace(self, text: str) -> str:
        """Clean up whitespace and formatting."""
        for pattern in self.remove_patterns:
            text = re.sub(pattern, ' ', text)
        return text
    
    def _expand_abbreviations(self, text: str) -> str:
        """Expand common abbreviations for better speech."""
        # Handle common programming terms
        programming_terms = {
            'API': 'A P I',
            'URL': 'U R L',
            'HTML': 'H T M L',
            'CSS': 'C S S',
            'JS': 'JavaScript',
            'SQL': 'S Q L',
            'JSON': 'Jason',  # More natural pronunciation
            'XML': 'X M L',
            'HTTP': 'H T T P',
            'HTTPS': 'H T T P S',
        }
        
        for abbrev, expansion in programming_terms.items():
            # Replace whole words only (including plural forms)
            pattern = r'\b' + re.escape(abbrev) + r's?\b'  # Handle plurals like "APIs"
            text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)
        
        return text
    
    def _final_cleanup(self, text: str) -> str:
        """Final cleanup and optimization."""
        # Remove any remaining problematic characters
        text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
        
        # Ensure proper spacing around punctuation
        text = re.sub(r'\s*([.,!?;:])\s*', r'\1 ', text)
        
        # Clean up multiple spaces again
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def preview_formatting(self, text: str) -> Dict[str, str]:
        """
        Preview how text will be formatted (for debugging).
        
        Args:
            text: Original text
            
        Returns:
            Dictionary with original and formatted versions
        """
        formatted = self.format_for_speech(text)
        
        return {
            "original": text,
            "formatted": formatted,
            "changes_made": text != formatted,
            "length_change": len(formatted) - len(text)
        }


# Singleton instance for global access
_tts_formatter = None


def get_tts_formatter() -> TTSFormatter:
    """
    Get singleton TTS formatter instance.
    
    Returns:
        TTSFormatter instance
    """
    global _tts_formatter
    if _tts_formatter is None:
        _tts_formatter = TTSFormatter()
    return _tts_formatter


def format_text_for_speech(text: str) -> str:
    """
    Convenience function to format text for speech.
    
    Args:
        text: Text to format
        
    Returns:
        Speech-optimized text
    """
    formatter = get_tts_formatter()
    return formatter.format_for_speech(text)
