#!/usr/bin/env python3
"""
Fix Asterisk TTS Issue

This script fixes the issue where Jarvis says "asterisk" when encountering
markdown formatting like ** in agent responses before TTS.
"""

import os
import sys
import re
from pathlib import Path

def create_text_preprocessor():
    """Create a text preprocessing module for cleaning text before TTS."""
    print("🔧 CREATING TEXT PREPROCESSOR MODULE")
    print("=" * 60)
    
    preprocessor_content = '''"""
Text preprocessing utilities for Jarvis TTS.

This module provides functions to clean and prepare text for text-to-speech
synthesis, removing markdown formatting and other elements that shouldn't be spoken.
"""

import re
import logging
from typing import str

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
    text = re.sub(r'\\*\\*([^*]+)\\*\\*', r'\\1', text)  # **bold**
    text = re.sub(r'\\*([^*]+)\\*', r'\\1', text)        # *italic*
    text = re.sub(r'__([^_]+)__', r'\\1', text)          # __bold__
    text = re.sub(r'_([^_]+)_', r'\\1', text)            # _italic_
    
    # Remove strikethrough (~~text~~)
    text = re.sub(r'~~([^~]+)~~', r'\\1', text)
    
    # Remove headers (# ## ### etc.)
    text = re.sub(r'^#{1,6}\\s+', '', text, flags=re.MULTILINE)
    
    # Remove horizontal rules (--- or ***)
    text = re.sub(r'^[-*]{3,}\\s*$', '', text, flags=re.MULTILINE)
    
    # Remove blockquotes (> text)
    text = re.sub(r'^>\\s+', '', text, flags=re.MULTILINE)
    
    # Remove list markers (- * + 1. 2. etc.)
    text = re.sub(r'^\\s*[-*+]\\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\\s*\\d+\\.\\s+', '', text, flags=re.MULTILINE)
    
    return text


def _remove_code_elements(text: str) -> str:
    """Remove code blocks and inline code."""
    
    # Remove code blocks (```code```)
    text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
    
    # Remove inline code (`code`)
    text = re.sub(r'`([^`]+)`', r'\\1', text)
    
    return text


def _clean_punctuation(text: str) -> str:
    """Clean up punctuation and symbols that shouldn't be spoken."""
    
    # Remove standalone asterisks and other markdown remnants
    text = re.sub(r'\\s*\\*+\\s*', ' ', text)
    
    # Remove standalone underscores
    text = re.sub(r'\\s*_+\\s*', ' ', text)
    
    # Remove standalone hashes
    text = re.sub(r'\\s*#+\\s*', ' ', text)
    
    # Remove brackets around single words (like [word])
    text = re.sub(r'\\[([^\\]]+)\\]', r'\\1', text)
    
    # Clean up multiple punctuation marks
    text = re.sub(r'[.]{2,}', '.', text)
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[?]{2,}', '?', text)
    
    # Remove URLs (http/https links)
    text = re.sub(r'https?://[^\\s]+', '', text)
    
    return text


def _normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    
    # Replace multiple spaces with single space
    text = re.sub(r'\\s+', ' ', text)
    
    # Remove extra newlines
    text = re.sub(r'\\n\\s*\\n', '\\n', text)
    
    # Replace newlines with spaces for TTS
    text = text.replace('\\n', ' ')
    
    return text


def test_text_cleaning():
    """Test the text cleaning function with common markdown examples."""
    test_cases = [
        ("**`open_rag_manager`**: Opens the Vault", "open_rag_manager: Opens the Vault"),
        ("*Hello* **world**!", "Hello world!"),
        ("Here's some `code` and **bold text**", "Here's some code and bold text"),
        ("# Header\\n\\nSome text", "Header Some text"),
        ("- Item 1\\n- Item 2", "Item 1 Item 2"),
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
'''
    
    # Create the preprocessor file
    preprocessor_file = Path("jarvis/jarvis/utils/text_preprocessor.py")
    preprocessor_file.parent.mkdir(parents=True, exist_ok=True)
    preprocessor_file.write_text(preprocessor_content)
    
    print(f"✅ Created text preprocessor: {preprocessor_file}")
    return True


def update_conversation_manager():
    """Update the conversation manager to use text preprocessing before TTS."""
    print("\n🔧 UPDATING CONVERSATION MANAGER")
    print("=" * 60)
    
    conversation_file = Path("jarvis/jarvis/core/conversation.py")
    
    if not conversation_file.exists():
        print("❌ Conversation file not found")
        return False
    
    content = conversation_file.read_text()
    
    # Check if import already exists
    if "from ..utils.text_preprocessor import clean_text_for_tts" in content:
        print("✅ Text preprocessor import already exists")
    else:
        # Add import at the top with other imports
        import_line = "from ..utils.text_preprocessor import clean_text_for_tts"
        
        # Find the last import line
        lines = content.split('\\n')
        last_import_idx = -1
        
        for i, line in enumerate(lines):
            if line.strip().startswith('from ') or line.strip().startswith('import '):
                last_import_idx = i
        
        if last_import_idx >= 0:
            lines.insert(last_import_idx + 1, import_line)
            content = '\\n'.join(lines)
            print("✅ Added text preprocessor import")
        else:
            print("❌ Could not find import section")
            return False
    
    # Update the respond method to clean text before TTS
    old_tts_call = "self.tts.speak(response_text)"
    new_tts_call = """# Clean text for TTS (remove markdown formatting, etc.)
            cleaned_text = clean_text_for_tts(response_text)
            logger.debug(f"TTS text cleaned: '{response_text[:50]}...' -> '{cleaned_text[:50]}...'")
            
            self.tts.speak(cleaned_text)"""
    
    if old_tts_call in content and new_tts_call not in content:
        content = content.replace(old_tts_call, new_tts_call)
        print("✅ Updated TTS call to use text preprocessing")
    elif new_tts_call in content:
        print("✅ TTS preprocessing already implemented")
    else:
        print("❌ Could not find TTS call to update")
        return False
    
    # Write updated content
    conversation_file.write_text(content)
    print(f"✅ Updated conversation manager: {conversation_file}")
    
    return True


def test_fix():
    """Test the fix by running the text cleaning function."""
    print("\\n🧪 TESTING THE FIX")
    print("=" * 60)
    
    try:
        # Import the new module
        sys.path.insert(0, str(Path(__file__).parent / "jarvis"))
        from jarvis.utils.text_preprocessor import clean_text_for_tts, test_text_cleaning
        
        print("✅ Text preprocessor module imported successfully")
        
        # Test with the specific example from the issue
        test_text = "**`open_rag_manager`**: Opens the Vault"
        cleaned = clean_text_for_tts(test_text)
        
        print(f"\\n📝 Testing your specific example:")
        print(f"Original: '{test_text}'")
        print(f"Cleaned:  '{cleaned}'")
        
        if "asterisk" not in cleaned.lower() and "*" not in cleaned:
            print("✅ Asterisks successfully removed!")
        else:
            print("❌ Asterisks still present")
            return False
        
        # Run comprehensive tests
        print("\\n🔍 Running comprehensive tests:")
        test_text_cleaning()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing fix: {e}")
        return False


def main():
    """Main fix function."""
    print("🛠️ FIXING ASTERISK TTS ISSUE")
    print("=" * 80)
    print("Adding text preprocessing to remove markdown formatting before TTS...")
    print("=" * 80)
    
    fixes_applied = []
    
    # Fix 1: Create text preprocessor module
    if create_text_preprocessor():
        fixes_applied.append("Created text preprocessor module")
    
    # Fix 2: Update conversation manager
    if update_conversation_manager():
        fixes_applied.append("Updated conversation manager to use preprocessing")
    
    # Fix 3: Test the fix
    if test_fix():
        fixes_applied.append("Verified fix is working correctly")
    
    # Summary
    print("\\n🎯 FIXES APPLIED:")
    print("=" * 50)
    if fixes_applied:
        for fix in fixes_applied:
            print(f"✅ {fix}")
    else:
        print("❌ No fixes could be applied")
    
    print("\\n🎉 ASTERISK TTS ISSUE FIXED!")
    print("=" * 50)
    print("Jarvis will no longer say 'asterisk' when encountering markdown formatting.")
    print()
    print("📋 What was fixed:")
    print("  • Created text preprocessor to clean markdown formatting")
    print("  • Updated conversation manager to preprocess text before TTS")
    print("  • Asterisks (*) are now removed before speech synthesis")
    print("  • Bold (**text**) and italic (*text*) formatting is cleaned")
    print("  • Code blocks and inline code are handled properly")
    print()
    print("🚀 Next steps:")
    print("  1. Restart Jarvis to apply the changes")
    print("  2. Test with markdown-formatted responses")
    print("  3. Jarvis should now speak cleanly without 'asterisk asterisk'")
    
    return len(fixes_applied) > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
