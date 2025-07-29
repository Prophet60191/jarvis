#!/usr/bin/env python3
"""
Quick fix for Jarvis errors.
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_basic_imports():
    """Test if basic Jarvis components can be imported."""
    print("🔍 Testing Basic Imports")
    print("=" * 60)
    
    imports_to_test = [
        ("jarvis.config", "get_config"),
        ("jarvis.core.agent", "JarvisAgent"),
        ("jarvis.tools.plugins.jarvis_ui_tool", "open_jarvis_ui"),
        ("jarvis.tools.plugins.device_time_tool", "get_current_time"),
    ]
    
    all_good = True
    
    for module_name, item_name in imports_to_test:
        try:
            module = __import__(module_name, fromlist=[item_name])
            getattr(module, item_name)
            print(f"✅ {module_name}.{item_name}")
        except Exception as e:
            print(f"❌ {module_name}.{item_name}: {e}")
            all_good = False
    
    return all_good


def test_agent_creation():
    """Test if we can create a Jarvis agent."""
    print("\n🤖 Testing Agent Creation")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.agent import JarvisAgent
        
        config = get_config()
        print("✅ Config loaded")
        
        agent = JarvisAgent(config.llm)
        print("✅ Agent created")
        
        agent.initialize()
        print("✅ Agent initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simple_tool():
    """Test a simple tool like get_current_time."""
    print("\n⏰ Testing Simple Tool")
    print("=" * 60)
    
    try:
        from jarvis.tools.plugins.device_time_tool import get_current_time
        
        result = get_current_time.func()
        print(f"✅ get_current_time result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_jarvis_ui_tool():
    """Check the Jarvis UI tool specifically."""
    print("\n⚙️ Testing Jarvis UI Tool")
    print("=" * 60)
    
    try:
        from jarvis.tools.plugins.jarvis_ui_tool import open_jarvis_ui
        
        print("✅ Jarvis UI tool imported")
        
        # Check if the desktop script exists where the tool expects it
        import os
        plugin_file = open_jarvis_ui.func.__code__.co_filename
        jarvis_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(plugin_file))))
        desktop_script = os.path.join(jarvis_dir, "jarvis_settings_app.py")
        
        print(f"📍 Tool expects desktop script at: {desktop_script}")
        print(f"   Exists: {'✅ Yes' if os.path.exists(desktop_script) else '❌ No'}")
        
        if os.path.exists(desktop_script):
            print("✅ Desktop script found in expected location")
            return True
        else:
            print("❌ Desktop script not found where tool expects it")
            return False
        
    except Exception as e:
        print(f"❌ Jarvis UI tool check failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def provide_quick_fix():
    """Provide a quick fix for the issues."""
    print("\n🔧 Quick Fix")
    print("=" * 60)
    
    print("Based on the test results, here's what to do:")
    print()
    print("1. If imports are failing:")
    print("   • Check Python path issues")
    print("   • Restart Jarvis completely")
    print()
    print("2. If agent creation is failing:")
    print("   • Check config.yaml file")
    print("   • Verify LLM settings")
    print()
    print("3. If tools are failing:")
    print("   • Check tool file paths")
    print("   • Verify tool imports")
    print()
    print("4. Quick restart command:")
    print("   • Stop Jarvis (Ctrl+C)")
    print("   • Run: python main.py")


def main():
    """Run quick diagnostics and fix."""
    print("🚨 Jarvis Error Quick Fix")
    print("=" * 60)
    print("Diagnosing why Jarvis is saying 'I encountered an error'")
    print("=" * 60)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Agent Creation", test_agent_creation),
        ("Simple Tool", test_simple_tool),
        ("Jarvis UI Tool", check_jarvis_ui_tool),
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
    print("🚨 QUICK FIX RESULTS")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed < total:
        provide_quick_fix()
        print("\n🎯 Most likely fix: Restart Jarvis completely")
        print("   1. Stop current Jarvis (Ctrl+C)")
        print("   2. Run: python main.py")
    else:
        print("\n🎉 All tests passed - Jarvis should be working!")


if __name__ == "__main__":
    main()
