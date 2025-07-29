#!/usr/bin/env python3
"""
Test the asterisk TTS fix.
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_text_cleaning():
    """Test the text cleaning function."""
    print("🧪 TESTING ASTERISK TTS FIX")
    print("=" * 60)
    
    try:
        from jarvis.utils.text_preprocessor import clean_text_for_tts
        print("✅ Text preprocessor imported successfully")
        
        # Test the specific example from the issue
        test_text = "**`open_rag_manager`**: Opens the Vault"
        cleaned = clean_text_for_tts(test_text)
        
        print(f"\n📝 Your specific example:")
        print(f"Original: '{test_text}'")
        print(f"Cleaned:  '{cleaned}'")
        
        if "*" not in cleaned:
            print("✅ SUCCESS: Asterisks removed!")
        else:
            print("❌ FAILED: Asterisks still present")
            return False
        
        # Test other markdown examples
        test_cases = [
            ("**bold text**", "bold text"),
            ("*italic text*", "italic text"),
            ("Here is `code` and **bold**", "Here is code and bold"),
            ("# Header text", "Header text"),
            ("- List item", "List item"),
            ("Visit https://example.com for info", "Visit  for info"),
            ("Text with *** multiple *** asterisks", "Text with  multiple  asterisks"),
        ]
        
        print("\n🔍 Additional test cases:")
        print("-" * 40)
        all_passed = True
        
        for original, expected in test_cases:
            result = clean_text_for_tts(original)
            # Normalize whitespace for comparison
            result_normalized = " ".join(result.split())
            expected_normalized = " ".join(expected.split())
            
            status = "✅" if result_normalized == expected_normalized else "❌"
            print(f"{status} '{original}' -> '{result}'")
            
            if result_normalized != expected_normalized:
                print(f"   Expected: '{expected}'")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error testing text cleaning: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conversation_integration():
    """Test that the conversation manager has been updated."""
    print("\n🔧 TESTING CONVERSATION MANAGER INTEGRATION")
    print("=" * 60)
    
    try:
        conversation_file = Path("jarvis/jarvis/core/conversation.py")
        
        if not conversation_file.exists():
            print("❌ Conversation file not found")
            return False
        
        content = conversation_file.read_text()
        
        # Check for import
        if "from ..utils.text_preprocessor import clean_text_for_tts" in content:
            print("✅ Text preprocessor import found")
        else:
            print("❌ Text preprocessor import missing")
            return False
        
        # Check for usage
        if "clean_text_for_tts(response_text)" in content:
            print("✅ Text preprocessing usage found")
        else:
            print("❌ Text preprocessing usage missing")
            return False
        
        print("✅ Conversation manager integration complete")
        return True
        
    except Exception as e:
        print(f"❌ Error checking conversation integration: {e}")
        return False


def main():
    """Main test function."""
    print("🔧 ASTERISK TTS FIX VERIFICATION")
    print("=" * 80)
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Text cleaning function
    if test_text_cleaning():
        tests_passed += 1
        print("✅ Test 1 PASSED: Text cleaning function")
    else:
        print("❌ Test 1 FAILED: Text cleaning function")
    
    # Test 2: Conversation manager integration
    if test_conversation_integration():
        tests_passed += 1
        print("✅ Test 2 PASSED: Conversation manager integration")
    else:
        print("❌ Test 2 FAILED: Conversation manager integration")
    
    # Summary
    print(f"\n🎯 TEST RESULTS: {tests_passed}/{total_tests} PASSED")
    print("=" * 80)
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Asterisk TTS issue has been fixed")
        print("✅ Markdown formatting will be cleaned before TTS")
        print("✅ Jarvis will no longer say 'asterisk asterisk'")
        
        print("\n📋 What was fixed:")
        print("  • Created text preprocessor to remove markdown formatting")
        print("  • Updated conversation manager to clean text before TTS")
        print("  • **bold** and *italic* formatting is now removed")
        print("  • `code` blocks are cleaned properly")
        print("  • Headers, lists, and other markdown elements are handled")
        
        print("\n🚀 Next steps:")
        print("  1. Restart Jarvis to apply the changes")
        print("  2. Test with responses containing markdown formatting")
        print("  3. Jarvis should now speak cleanly without saying 'asterisk'")
        
    elif tests_passed > 0:
        print("⚠️ SOME TESTS PASSED")
        print("The fix is partially working but needs attention")
    else:
        print("❌ ALL TESTS FAILED")
        print("The fix needs to be investigated and corrected")
    
    return tests_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
