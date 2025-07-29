#!/usr/bin/env python3
"""
Simple LaVague test script to verify web automation is working.
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent))

def test_lavague_import():
    """Test if LaVague can be imported."""
    try:
        from lavague.core import WorldModel, ActionEngine
        from lavague.drivers.selenium import SeleniumDriver
        print("✅ LaVague imports successfully")
        return True
    except ImportError as e:
        print(f"❌ LaVague import failed: {e}")
        return False

def test_selenium_basic():
    """Test basic Selenium functionality."""
    try:
        from lavague.drivers.selenium import SeleniumDriver
        
        print("🌐 Testing basic Selenium functionality...")
        driver = SeleniumDriver(headless=True)
        driver.get("https://httpbin.org/html")  # Simple test page
        title = driver.driver.title
        driver.driver.quit()
        
        print(f"✅ Selenium test successful - Page title: '{title}'")
        return True
        
    except Exception as e:
        print(f"❌ Selenium test failed: {e}")
        return False

def test_lavague_plugin():
    """Test the LaVague plugin."""
    try:
        from jarvis.tools.plugins.lavague_web_automation import LAVAGUE_AVAILABLE
        
        if LAVAGUE_AVAILABLE:
            print("✅ LaVague plugin reports availability")
            return True
        else:
            print("❌ LaVague plugin reports unavailable")
            return False
            
    except Exception as e:
        print(f"❌ LaVague plugin test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing LaVague Web Automation Integration\n")
    
    tests = [
        ("LaVague Import", test_lavague_import),
        ("Selenium Basic", test_selenium_basic),
        ("LaVague Plugin", test_lavague_plugin),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        result = test_func()
        results.append((test_name, result))
        print()
    
    print("📊 Test Results:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:20} | {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"Total: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! LaVague is ready for voice commands.")
        print("\n🎤 Try these voice commands with Jarvis:")
        print("• 'Check LaVague status'")
        print("• 'Navigate to google.com and search for Python'")
        print("• 'Extract the title from example.com'")
    else:
        print(f"\n⚠️  {len(tests) - passed} tests failed. LaVague may not work correctly.")

if __name__ == "__main__":
    main()
