#!/usr/bin/env python3
"""
Simple LaVague test to verify web automation is working.
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.append('jarvis')

def test_lavague_basic():
    """Test basic LaVague functionality."""
    print("🌐 Testing LaVague Basic Functionality")
    print("=" * 50)
    
    try:
        # Test import
        from jarvis.tools.plugins.lavague_web_automation import LAVAGUE_AVAILABLE

        print(f"LaVague Available: {LAVAGUE_AVAILABLE}")
        if not LAVAGUE_AVAILABLE:
            print("LaVague is not available - missing dependencies")
            return False
        
        # Test basic selenium functionality
        from lavague.drivers.selenium import SeleniumDriver
        from selenium.webdriver.chrome.options import Options
        
        print("🔧 Setting up Chrome with webdriver-manager...")
        
        # Use webdriver-manager to handle chromedriver automatically
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium import webdriver
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Let webdriver-manager handle the driver
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver installed at: {driver_path}")
        
        # Test basic web navigation
        print("🌐 Testing basic web navigation...")
        driver = webdriver.Chrome(service=webdriver.chrome.service.Service(driver_path), options=chrome_options)
        
        try:
            driver.get("https://example.com")
            title = driver.title
            print(f"✅ Successfully loaded page: '{title}'")
            
            # Test LaVague integration
            print("🤖 Testing LaVague integration...")
            selenium_driver = SeleniumDriver(headless=True)
            selenium_driver.get("https://example.com")
            lavague_title = selenium_driver.driver.title
            selenium_driver.driver.quit()
            
            print(f"✅ LaVague successfully loaded page: '{lavague_title}'")
            
            return True
            
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"❌ LaVague test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_jarvis_integration():
    """Test LaVague integration with Jarvis."""
    print("\n🤖 Testing Jarvis Integration")
    print("=" * 50)
    
    try:
        from jarvis.tools.plugins.lavague_web_automation import check_lavague_status
        
        print("🔍 Testing LaVague status check...")
        result = check_lavague_status.invoke({})
        
        print("📝 Status Result:")
        print("-" * 30)
        print(result[:300])
        if len(result) > 300:
            print("...")
        print("-" * 30)
        
        if "✅ LaVague web automation is working correctly!" in result:
            print("🎉 SUCCESS: LaVague is fully integrated with Jarvis!")
            return True
        else:
            print("⚠️ LaVague integration has issues")
            return False
            
    except Exception as e:
        print(f"❌ Jarvis integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 LaVague Web Automation Test Suite")
    print("=" * 60)
    
    tests = [
        ("Basic LaVague", test_lavague_basic),
        ("Jarvis Integration", test_jarvis_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🎯 Running: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} | {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"Total: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! LaVague is ready for voice commands!")
        print("\n🎤 Try these voice commands with Jarvis:")
        print("• 'Check LaVague status'")
        print("• 'Navigate to google.com and search for Python'")
        print("• 'Extract the title from example.com'")
        print("• 'Fill out the form on [website]'")
    else:
        print(f"\n⚠️ {len(tests) - passed} tests failed. LaVague needs fixes.")

if __name__ == "__main__":
    main()
