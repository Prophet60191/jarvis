#!/usr/bin/env python3
"""
Demonstrate the asterisk TTS fix with before/after examples.
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def demonstrate_fix():
    """Demonstrate the fix with clear before/after examples."""
    print("🎯 ASTERISK TTS FIX DEMONSTRATION")
    print("=" * 80)
    
    try:
        from jarvis.utils.text_preprocessor import clean_text_for_tts
        
        # Examples of text that would cause Jarvis to say "asterisk"
        problematic_texts = [
            "**`open_rag_manager`**: Opens the Vault",
            "Use the **bold** command to *emphasize* text",
            "Here's some `code` and **important** information",
            "# Main Menu\n- **Option 1**: First choice\n- **Option 2**: Second choice",
            "Visit ***our website*** for more details",
            "The `get_time()` function returns **current time**",
        ]
        
        print("🔍 BEFORE FIX (what Jarvis would say):")
        print("-" * 60)
        for i, text in enumerate(problematic_texts, 1):
            # Simulate what TTS would receive before the fix
            spoken_before = text.replace("*", "asterisk ").replace("`", "backtick ")
            print(f"{i}. Original: {text}")
            print(f"   Would say: {spoken_before}")
            print()
        
        print("✅ AFTER FIX (what Jarvis will say now):")
        print("-" * 60)
        for i, text in enumerate(problematic_texts, 1):
            cleaned = clean_text_for_tts(text)
            print(f"{i}. Original: {text}")
            print(f"   Will say: {cleaned}")
            print()
        
        print("🎉 SUMMARY OF IMPROVEMENTS:")
        print("=" * 60)
        print("✅ No more 'asterisk asterisk' when encountering **bold** text")
        print("✅ No more 'backtick' when encountering `code` text")
        print("✅ Clean speech for markdown-formatted responses")
        print("✅ Headers, lists, and formatting are properly cleaned")
        print("✅ URLs are cleaned (no long web addresses spoken)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error demonstrating fix: {e}")
        return False


def show_specific_example():
    """Show the specific example from the user's issue."""
    print("\n🎯 YOUR SPECIFIC EXAMPLE")
    print("=" * 60)
    
    try:
        from jarvis.utils.text_preprocessor import clean_text_for_tts
        
        # The exact text from your issue
        original_text = "**`open_rag_manager`**: Opens the Vault"
        cleaned_text = clean_text_for_tts(original_text)
        
        print("📝 The text that was causing the problem:")
        print(f"   {original_text}")
        print()
        print("🔊 What Jarvis was saying BEFORE the fix:")
        print("   'asterisk asterisk backtick open underscore rag underscore manager backtick asterisk asterisk colon Opens the Vault'")
        print()
        print("✅ What Jarvis will say AFTER the fix:")
        print(f"   '{cleaned_text}'")
        print()
        print("🎉 Much better! Clean and natural speech.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error showing specific example: {e}")
        return False


def main():
    """Main demonstration function."""
    print("🎤 JARVIS ASTERISK TTS FIX - DEMONSTRATION")
    print("=" * 80)
    print("This demonstrates how the fix resolves the 'asterisk asterisk' issue")
    print("=" * 80)
    
    success = True
    
    if not demonstrate_fix():
        success = False
    
    if not show_specific_example():
        success = False
    
    if success:
        print("\n🚀 READY TO TEST!")
        print("=" * 60)
        print("1. Restart Jarvis to apply the changes")
        print("2. Ask Jarvis something that would generate markdown in the response")
        print("3. Listen for clean speech without 'asterisk asterisk'")
        print()
        print("Example test questions:")
        print("• 'What tools are available?' (might show **tool names**)")
        print("• 'How do I use the vault?' (might show `commands`)")
        print("• 'Show me the help menu' (might show formatted lists)")
    
    return success


if __name__ == "__main__":
    main()
