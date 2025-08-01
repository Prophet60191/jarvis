#!/usr/bin/env python3
"""
Test script for the new "vault" commands.
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_vault_tool_import():
    """Test if the vault tools can be imported."""
    print("🔧 Testing Vault Tool Import")
    print("=" * 60)
    
    try:
        from jarvis.tools.plugins.rag_ui_tool import open_rag_manager, close_rag_manager, show_rag_status
        
        print("✅ Successfully imported vault tools:")
        print(f"   • open_rag_manager: {open_rag_manager.name}")
        print(f"   • close_rag_manager: {close_rag_manager.name}")
        print(f"   • show_rag_status: {show_rag_status.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Vault tool import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vault_descriptions():
    """Test that the tool descriptions mention 'vault'."""
    print("\n📝 Testing Vault Descriptions")
    print("=" * 60)
    
    try:
        from jarvis.tools.plugins.rag_ui_tool import open_rag_manager, close_rag_manager, show_rag_status
        
        tools = [
            ("open_rag_manager", open_rag_manager),
            ("close_rag_manager", close_rag_manager),
            ("show_rag_status", show_rag_status),
        ]
        
        all_good = True
        
        for tool_name, tool in tools:
            description = tool.description.lower()
            
            if "vault" in description:
                print(f"✅ {tool_name}: Contains 'vault'")
                print(f"   Preview: {tool.description[:80]}...")
            else:
                print(f"❌ {tool_name}: Missing 'vault' reference")
                print(f"   Description: {tool.description[:80]}...")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Description test failed: {e}")
        return False


def test_vault_function_calls():
    """Test calling the vault functions."""
    print("\n🧪 Testing Vault Function Calls")
    print("=" * 60)
    
    try:
        from jarvis.tools.plugins.rag_ui_tool import open_rag_manager, close_rag_manager, show_rag_status
        
        # Test show_rag_status (safest to test)
        print("🔍 Testing show_rag_status...")
        status_result = show_rag_status.func()
        print(f"   Result: {status_result}")
        
        if "vault" in status_result.lower():
            print("✅ Status result mentions 'vault'")
        else:
            print("❌ Status result doesn't mention 'vault'")
            return False
        
        # Test open_rag_manager (just check the return message, don't actually open)
        print("\n🔍 Testing open_rag_manager...")
        open_result = open_rag_manager.func()
        print(f"   Result: {open_result}")
        
        if "vault" in open_result.lower():
            print("✅ Open result mentions 'vault'")
        else:
            print("❌ Open result doesn't mention 'vault'")
            return False
        
        # Test close_rag_manager
        print("\n🔍 Testing close_rag_manager...")
        close_result = close_rag_manager.func()
        print(f"   Result: {close_result}")
        
        if "vault" in close_result.lower():
            print("✅ Close result mentions 'vault'")
        else:
            print("❌ Close result doesn't mention 'vault'")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Function call test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def provide_usage_guide():
    """Provide usage guide for the new vault commands."""
    print("\n🎯 Vault Commands Usage Guide")
    print("=" * 60)
    
    print("🎤 Voice Commands:")
    print("   • 'Hey Jarvis, open vault' - Opens the knowledge vault")
    print("   • 'Hey Jarvis, show vault' - Opens the vault interface")
    print("   • 'Hey Jarvis, close vault' - Closes the vault app")
    print("   • 'Hey Jarvis, show vault status' - Shows vault system status")
    print()
    print("🏛️ What is the Vault?")
    print("   • Your personal knowledge repository")
    print("   • Document upload and management")
    print("   • Intelligent document search")
    print("   • RAG (Retrieval-Augmented Generation) system")
    print("   • Memory and conversation management")
    print()
    print("✨ Benefits of 'Vault' vs 'RAG Manager':")
    print("   • More intuitive and user-friendly")
    print("   • No conflict with memory tools")
    print("   • Conveys secure knowledge storage")
    print("   • Easier to remember and say")


def main():
    """Test the new vault commands."""
    print("🏛️ Vault Commands Test Suite")
    print("=" * 60)
    print("Testing the new 'vault' terminology for RAG management")
    print("=" * 60)
    
    tests = [
        ("Tool Import", test_vault_tool_import),
        ("Descriptions", test_vault_descriptions),
        ("Function Calls", test_vault_function_calls),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("🏛️ VAULT COMMANDS TEST RESULTS")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Vault commands are ready!")
        provide_usage_guide()
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
        provide_usage_guide()


if __name__ == "__main__":
    main()
