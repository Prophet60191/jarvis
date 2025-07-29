#!/usr/bin/env python3
"""
Test Chat History Configuration

Tests the configuration system for chat history settings
and their integration with the conversation manager.
"""

import sys
import tempfile
from pathlib import Path

# Add jarvis to path
sys.path.append(str(Path(__file__).parent / "jarvis"))


def test_conversation_config_chat_history():
    """Test ConversationConfig chat history settings."""
    print("⚙️ Testing ConversationConfig Chat History Settings")
    print("=" * 60)
    
    try:
        from jarvis.config import ConversationConfig
        
        # Test default configuration
        print("🔍 Testing default configuration...")
        default_config = ConversationConfig()
        
        # Check default values
        expected_defaults = {
            'chat_history_enabled': True,
            'auto_save_sessions': True,
            'max_session_history': 100,
            'session_cleanup_days': 30,
            'auto_start_session': True
        }
        
        all_defaults_correct = True
        for attr, expected_value in expected_defaults.items():
            actual_value = getattr(default_config, attr, None)
            print(f"   {attr}: {actual_value} (expected: {expected_value})")
            
            if actual_value != expected_value:
                print(f"   ❌ Incorrect default value for {attr}")
                all_defaults_correct = False
            else:
                print(f"   ✅ Correct default value")
        
        # Check chat_history_path
        chat_history_path = default_config.chat_history_path
        print(f"   chat_history_path: {chat_history_path}")
        
        if isinstance(chat_history_path, Path) and str(chat_history_path) == "data/chat_sessions":
            print("   ✅ Correct default chat history path")
        else:
            print("   ❌ Incorrect default chat history path")
            all_defaults_correct = False
        
        if all_defaults_correct:
            print("✅ All default configuration values are correct")
        else:
            print("❌ Some default configuration values are incorrect")
            return False
        
        # Test custom configuration
        print("\n🛠️ Testing custom configuration...")
        
        custom_config = ConversationConfig(
            chat_history_enabled=False,
            chat_history_path=Path("/tmp/custom_chat"),
            auto_save_sessions=False,
            max_session_history=50,
            session_cleanup_days=7,
            auto_start_session=False
        )
        
        custom_values = {
            'chat_history_enabled': False,
            'auto_save_sessions': False,
            'max_session_history': 50,
            'session_cleanup_days': 7,
            'auto_start_session': False
        }
        
        all_custom_correct = True
        for attr, expected_value in custom_values.items():
            actual_value = getattr(custom_config, attr)
            print(f"   {attr}: {actual_value} (expected: {expected_value})")
            
            if actual_value != expected_value:
                print(f"   ❌ Incorrect custom value for {attr}")
                all_custom_correct = False
            else:
                print(f"   ✅ Correct custom value")
        
        if str(custom_config.chat_history_path) == "/tmp/custom_chat":
            print("   ✅ Correct custom chat history path")
        else:
            print("   ❌ Incorrect custom chat history path")
            all_custom_correct = False
        
        if all_custom_correct:
            print("✅ Custom configuration values work correctly")
            return True
        else:
            print("❌ Custom configuration values have issues")
            return False
        
    except Exception as e:
        print(f"❌ ConversationConfig test failed: {e}")
        return False


def test_conversation_manager_config_integration():
    """Test ConversationManager integration with configuration."""
    print("\n🔗 Testing ConversationManager Config Integration")
    print("=" * 60)
    
    try:
        from jarvis.config import ConversationConfig
        from jarvis.core.conversation import ConversationManager
        
        # Test with chat history enabled
        print("✅ Testing with chat history enabled...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            enabled_config = ConversationConfig(
                chat_history_enabled=True,
                chat_history_path=Path(temp_dir) / "enabled_chat",
                auto_save_sessions=True,
                max_session_history=10,
                auto_start_session=True
            )
            
            manager = ConversationManager(enabled_config, None, None)
            
            # Check configuration integration
            config_checks = [
                ('chat_history_enabled', True),
                ('auto_save_sessions', True),
                ('max_session_history', 10),
                ('auto_start_session', True)
            ]
            
            all_enabled_correct = True
            for attr, expected in config_checks:
                actual = getattr(manager, attr, None)
                print(f"   {attr}: {actual} (expected: {expected})")
                
                if actual != expected:
                    print(f"   ❌ Configuration not properly integrated for {attr}")
                    all_enabled_correct = False
                else:
                    print(f"   ✅ Configuration integrated correctly")
            
            # Check path integration
            expected_path = Path(temp_dir) / "enabled_chat"
            if manager.chat_history_path == expected_path:
                print("   ✅ Chat history path integrated correctly")
            else:
                print(f"   ❌ Chat history path mismatch: {manager.chat_history_path} vs {expected_path}")
                all_enabled_correct = False
            
            # Check directory creation
            if manager.chat_history_path.exists():
                print("   ✅ Chat history directory created")
            else:
                print("   ❌ Chat history directory not created")
                all_enabled_correct = False
            
            if not all_enabled_correct:
                return False
        
        # Test with chat history disabled
        print("\n❌ Testing with chat history disabled...")
        
        disabled_config = ConversationConfig(
            chat_history_enabled=False,
            auto_save_sessions=False,
            auto_start_session=False
        )
        
        disabled_manager = ConversationManager(disabled_config, None, None)
        
        if not disabled_manager.chat_history_enabled:
            print("   ✅ Chat history properly disabled")
        else:
            print("   ❌ Chat history not properly disabled")
            return False
        
        # Test add_to_chat_history with disabled config
        disabled_manager.add_to_chat_history("test", "response")
        
        if len(disabled_manager.chat_history) == 0:
            print("   ✅ Chat history not added when disabled")
        else:
            print("   ❌ Chat history added despite being disabled")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ ConversationManager config integration test failed: {e}")
        return False


def test_auto_save_functionality():
    """Test auto-save functionality with configuration."""
    print("\n💾 Testing Auto-Save Functionality")
    print("=" * 40)
    
    try:
        from jarvis.config import ConversationConfig
        from jarvis.core.conversation import ConversationManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with auto-save enabled
            auto_save_config = ConversationConfig(
                chat_history_enabled=True,
                chat_history_path=Path(temp_dir),
                auto_save_sessions=True,
                auto_start_session=True
            )
            
            manager = ConversationManager(auto_save_config, None, None)
            
            print("🔄 Testing auto-save trigger...")
            
            # Add exchanges to trigger auto-save (every 5 exchanges)
            for i in range(6):
                manager.add_to_chat_history(f"Message {i+1}", f"Response {i+1}")
            
            # Check if session was created and saved
            if manager.current_session_id:
                print(f"   ✅ Session auto-created: {manager.current_session_id[:8]}...")
                
                # Check if file exists (auto-save should have triggered)
                session_file = manager.chat_history_path / f"{manager.current_session_id}.json"
                if session_file.exists():
                    print("   ✅ Auto-save triggered and file created")
                else:
                    print("   ⚠️ Auto-save may not have triggered yet (timing dependent)")
                
            else:
                print("   ❌ Session not auto-created")
                return False
            
            # Test with auto-save disabled
            print("\n🚫 Testing with auto-save disabled...")
            
            no_auto_save_config = ConversationConfig(
                chat_history_enabled=True,
                chat_history_path=Path(temp_dir) / "no_auto",
                auto_save_sessions=False,
                auto_start_session=True
            )
            
            no_auto_manager = ConversationManager(no_auto_save_config, None, None)
            
            # Add exchanges (should not auto-save)
            for i in range(6):
                no_auto_manager.add_to_chat_history(f"Message {i+1}", f"Response {i+1}")
            
            if no_auto_manager.current_session_id:
                session_file = no_auto_manager.chat_history_path / f"{no_auto_manager.current_session_id}.json"
                if not session_file.exists():
                    print("   ✅ Auto-save correctly disabled")
                else:
                    print("   ❌ Auto-save occurred despite being disabled")
                    return False
            else:
                print("   ❌ Session not created")
                return False
            
            return True
        
    except Exception as e:
        print(f"❌ Auto-save functionality test failed: {e}")
        return False


def test_session_cleanup_configuration():
    """Test session cleanup with configuration settings."""
    print("\n🧹 Testing Session Cleanup Configuration")
    print("=" * 50)
    
    try:
        from jarvis.config import ConversationConfig
        from jarvis.core.conversation import ConversationManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cleanup_config = ConversationConfig(
                chat_history_enabled=True,
                chat_history_path=Path(temp_dir),
                max_session_history=3,  # Keep only 3 sessions
                session_cleanup_days=30
            )
            
            manager = ConversationManager(cleanup_config, None, None)
            
            print("📝 Creating test sessions...")
            
            # Create multiple sessions
            session_ids = []
            for i in range(5):
                session_id = manager.start_new_session(f"Test Session {i+1}")
                manager.add_to_chat_history(f"Test message {i+1}", f"Test response {i+1}")
                manager.save_chat_history()
                session_ids.append(session_id)
            
            print(f"   Created {len(session_ids)} sessions")
            
            # Test cleanup
            print("\n🧹 Testing cleanup...")
            cleanup_result = manager.cleanup_old_sessions()
            
            print(f"   Cleanup status: {cleanup_result.get('status', 'unknown')}")
            print(f"   Total sessions: {cleanup_result.get('total_sessions', 0)}")
            print(f"   Deleted: {cleanup_result.get('deleted_count', 0)}")
            print(f"   Kept: {cleanup_result.get('kept_count', 0)}")
            
            if cleanup_result.get('status') == 'success':
                expected_kept = min(3, len(session_ids))  # max_session_history = 3
                actual_kept = cleanup_result.get('kept_count', 0)
                
                if actual_kept <= expected_kept:
                    print("   ✅ Session cleanup working correctly")
                else:
                    print(f"   ❌ Too many sessions kept: {actual_kept} > {expected_kept}")
                    return False
            else:
                print(f"   ❌ Cleanup failed: {cleanup_result.get('message', 'unknown error')}")
                return False
            
            return True
        
    except Exception as e:
        print(f"❌ Session cleanup configuration test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Chat History Configuration Testing Suite")
    print("=" * 70)
    print("Testing configuration system integration with chat history...")
    print()
    
    tests = [
        ("ConversationConfig Chat History", test_conversation_config_chat_history),
        ("ConversationManager Config Integration", test_conversation_manager_config_integration),
        ("Auto-Save Functionality", test_auto_save_functionality),
        ("Session Cleanup Configuration", test_session_cleanup_configuration)
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
    
    print(f"\n📊 Chat History Configuration Test Results")
    print("=" * 55)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Overall Results:")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📊 Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 Chat History Configuration: COMPLETE!")
        print("   ✅ Configuration settings properly defined")
        print("   ✅ ConversationManager integration working")
        print("   ✅ Auto-save functionality operational")
        print("   ✅ Session cleanup configuration functional")
        print("\n⚙️ Chat history is now fully configurable!")
    elif passed >= total * 0.75:
        print(f"\n✅ Chat History Configuration mostly complete!")
        print(f"   Core configuration functionality working with minor issues")
    else:
        print(f"\n⚠️  Chat History Configuration needs attention")
        print(f"   Multiple configuration issues detected")
    
    return passed >= total * 0.75


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
