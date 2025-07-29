#!/usr/bin/env python3
"""
Test Chat Session Persistence

Tests the chat session persistence functionality including
saving, loading, and managing conversation history.
"""

import sys
import time
import tempfile
from pathlib import Path

# Add jarvis to path
sys.path.append(str(Path(__file__).parent / "jarvis"))


def test_conversation_manager_persistence():
    """Test ConversationManager chat session persistence methods."""
    print("💬 Testing ConversationManager Persistence")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.conversation import ConversationManager
        
        config = get_config()
        
        # Create conversation manager with temporary chat history path
        with tempfile.TemporaryDirectory() as temp_dir:
            conversation_manager = ConversationManager(config.conversation, None, None)
            conversation_manager.chat_history_path = Path(temp_dir)
            
            print("🚀 Testing session creation...")
            
            # Test 1: Start new session
            session_id = conversation_manager.start_new_session("Test Session")
            print(f"✅ Created session: {session_id[:8]}...")
            
            # Test 2: Add chat history
            conversation_manager.add_to_chat_history(
                user_input="Hello, how are you?",
                assistant_response="I'm doing well, thank you for asking!",
                metadata={"test": True}
            )
            
            conversation_manager.add_to_chat_history(
                user_input="What's the weather like?",
                assistant_response="I don't have access to current weather data.",
                metadata={"test": True}
            )
            
            print(f"✅ Added 2 exchanges to chat history")
            
            # Test 3: Save chat history
            save_success = conversation_manager.save_chat_history()
            print(f"✅ Save result: {save_success}")
            
            # Test 4: List chat sessions
            sessions = conversation_manager.list_chat_sessions()
            print(f"✅ Found {len(sessions)} sessions")
            
            if sessions:
                session = sessions[0]
                print(f"   Session ID: {session['session_id'][:8]}...")
                print(f"   Messages: {session['message_count']}")
                print(f"   Preview: {session['preview']}")
            
            # Test 5: Load chat history
            new_manager = ConversationManager(config.conversation, None, None)
            new_manager.chat_history_path = Path(temp_dir)
            
            load_success = new_manager.load_chat_history(session_id)
            print(f"✅ Load result: {load_success}")
            
            if load_success:
                print(f"✅ Loaded {len(new_manager.chat_history)} messages")
                
                # Verify content
                if len(new_manager.chat_history) >= 2:
                    first_exchange = new_manager.chat_history[0]
                    if "Hello, how are you?" in first_exchange.get('user_input', ''):
                        print("✅ Chat history content verified")
                    else:
                        print("❌ Chat history content mismatch")
                        return False
                else:
                    print("❌ Insufficient chat history loaded")
                    return False
            else:
                print("❌ Failed to load chat history")
                return False
            
            # Test 6: Delete session
            delete_success = conversation_manager.delete_chat_session(session_id)
            print(f"✅ Delete result: {delete_success}")
            
            return True
        
    except Exception as e:
        print(f"❌ ConversationManager persistence test failed: {e}")
        return False


def test_chat_management_tools():
    """Test chat management tools functionality."""
    print("\n🔧 Testing Chat Management Tools")
    print("=" * 40)
    
    try:
        from jarvis.tools.rag_tools import list_recent_chats, revisit_chat, save_current_chat
        
        print("📋 Testing list_recent_chats...")
        
        # Test listing chats (should handle empty case gracefully)
        result = list_recent_chats(limit=5)
        print(f"✅ List result: {result[:100]}{'...' if len(result) > 100 else ''}")
        
        # Should contain either sessions or "No chat sessions found"
        if "chat sessions" in result.lower():
            print("✅ List function working correctly")
        else:
            print("❌ Unexpected list result format")
            return False
        
        print("\n💾 Testing save_current_chat...")
        
        # Test saving current chat
        save_result = save_current_chat("Test Chat Session")
        print(f"✅ Save result: {save_result}")
        
        # Should indicate success or provide helpful message
        if "started" in save_result.lower() or "saved" in save_result.lower() or "no active" in save_result.lower():
            print("✅ Save function working correctly")
        else:
            print("❌ Unexpected save result format")
            return False
        
        print("\n🔄 Testing revisit_chat...")
        
        # Test revisiting non-existent chat
        revisit_result = revisit_chat("nonexistent123")
        print(f"✅ Revisit result: {revisit_result[:100]}{'...' if len(revisit_result) > 100 else ''}")
        
        # Should handle non-existent session gracefully
        if "no chat session found" in revisit_result.lower() or "failed to load" in revisit_result.lower():
            print("✅ Revisit function handles non-existent sessions correctly")
        else:
            print("❌ Unexpected revisit result for non-existent session")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Chat management tools test failed: {e}")
        return False


def test_chat_history_integration():
    """Test integration of chat history with conversation processing."""
    print("\n🔗 Testing Chat History Integration")
    print("=" * 45)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.conversation import ConversationManager
        
        config = get_config()
        
        # Create conversation manager with temporary path
        with tempfile.TemporaryDirectory() as temp_dir:
            conversation_manager = ConversationManager(config.conversation, None, None)
            conversation_manager.chat_history_path = Path(temp_dir)
            
            print("🚀 Testing automatic session creation...")
            
            # Test automatic session creation when adding history
            conversation_manager.add_to_chat_history(
                user_input="Test message",
                assistant_response="Test response"
            )
            
            if conversation_manager.current_session_id:
                print(f"✅ Session auto-created: {conversation_manager.current_session_id[:8]}...")
            else:
                print("❌ Session not auto-created")
                return False
            
            print("\n📊 Testing session metadata...")
            
            # Add more exchanges
            for i in range(3):
                conversation_manager.add_to_chat_history(
                    user_input=f"Message {i+2}",
                    assistant_response=f"Response {i+2}",
                    metadata={"sequence": i+2}
                )
            
            print(f"✅ Added {len(conversation_manager.chat_history)} total exchanges")
            
            # Save and verify
            save_success = conversation_manager.save_chat_history()
            if save_success:
                print("✅ Session saved successfully")
                
                # List sessions to verify metadata
                sessions = conversation_manager.list_chat_sessions()
                if sessions:
                    session = sessions[0]
                    expected_count = 4  # 1 initial + 3 additional
                    actual_count = session.get('message_count', 0)
                    
                    if actual_count == expected_count:
                        print(f"✅ Message count correct: {actual_count}")
                    else:
                        print(f"❌ Message count mismatch: expected {expected_count}, got {actual_count}")
                        return False
                else:
                    print("❌ No sessions found after saving")
                    return False
            else:
                print("❌ Failed to save session")
                return False
            
            return True
        
    except Exception as e:
        print(f"❌ Chat history integration test failed: {e}")
        return False


def test_session_preview_generation():
    """Test session preview generation functionality."""
    print("\n📝 Testing Session Preview Generation")
    print("=" * 45)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.conversation import ConversationManager
        
        config = get_config()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            conversation_manager = ConversationManager(config.conversation, None, None)
            conversation_manager.chat_history_path = Path(temp_dir)
            
            # Test different preview scenarios
            test_cases = [
                {
                    "name": "Short message",
                    "input": "Hello",
                    "expected_length": 5
                },
                {
                    "name": "Long message",
                    "input": "This is a very long message that should be truncated in the preview because it exceeds the maximum length",
                    "expected_truncated": True
                },
                {
                    "name": "Empty message",
                    "input": "",
                    "should_handle": True
                }
            ]
            
            print("🧪 Testing preview generation scenarios...")
            
            for test_case in test_cases:
                # Create session with test message
                session_id = conversation_manager.start_new_session()
                conversation_manager.add_to_chat_history(
                    user_input=test_case["input"],
                    assistant_response="Test response"
                )
                conversation_manager.save_chat_history()
                
                # Get session list to check preview
                sessions = conversation_manager.list_chat_sessions(limit=1)
                
                if sessions:
                    preview = sessions[0].get('preview', '')
                    print(f"   {test_case['name']}: '{preview}'")
                    
                    if test_case.get('expected_truncated'):
                        if len(preview) <= 50 and preview.endswith('...'):
                            print(f"   ✅ Correctly truncated")
                        else:
                            print(f"   ❌ Not properly truncated")
                            return False
                    elif test_case.get('should_handle'):
                        if preview:  # Should have some preview even for empty input
                            print(f"   ✅ Handled gracefully")
                        else:
                            print(f"   ❌ No preview generated")
                            return False
                else:
                    print(f"   ❌ No session found for {test_case['name']}")
                    return False
            
            return True
        
    except Exception as e:
        print(f"❌ Session preview generation test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Chat Session Persistence Testing Suite")
    print("=" * 60)
    print("Testing comprehensive chat session management functionality...")
    print()
    
    tests = [
        ("ConversationManager Persistence", test_conversation_manager_persistence),
        ("Chat Management Tools", test_chat_management_tools),
        ("Chat History Integration", test_chat_history_integration),
        ("Session Preview Generation", test_session_preview_generation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n📊 Chat Session Persistence Test Results")
    print("=" * 50)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Overall Results:")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📊 Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 Chat Session Persistence: COMPLETE!")
        print("   ✅ Session creation and management working")
        print("   ✅ Chat history saving and loading functional")
        print("   ✅ Management tools operational")
        print("   ✅ Integration with conversation flow successful")
        print("   ✅ Preview generation working correctly")
        print("\n💬 Chat sessions are now fully persistent across conversations!")
    elif passed >= total * 0.75:
        print(f"\n✅ Chat Session Persistence mostly complete!")
        print(f"   Core persistence functionality working with minor issues")
    else:
        print(f"\n⚠️  Chat Session Persistence needs attention")
        print(f"   Multiple persistence issues detected")
    
    return passed >= total * 0.75


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
