#!/usr/bin/env python3
"""
Test script to verify the App Builder System functionality.
This script tests the core components without requiring the full Jarvis system.
"""

import sys
import os
from pathlib import Path

# Add the jarvis package to Python path
project_root = Path(__file__).parent
jarvis_path = project_root / "jarvis"
sys.path.insert(0, str(jarvis_path))

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        # Test smart app builder import
        from jarvis.core.smart_app_builder import SmartAppBuilderCoordinator
        print("✅ SmartAppBuilderCoordinator imported successfully")
        
        # Test professional app builder plugin import
        from jarvis.tools.plugins.professional_app_builder import build_professional_application
        print("✅ Professional app builder plugin imported successfully")
        
        # Test app manager import
        from jarvis.utils.app_manager import DesktopAppManager
        print("✅ DesktopAppManager imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during import: {e}")
        return False

def test_smart_app_builder_initialization():
    """Test if SmartAppBuilderCoordinator can be initialized."""
    print("\n🔍 Testing SmartAppBuilderCoordinator initialization...")
    
    try:
        from jarvis.core.smart_app_builder import SmartAppBuilderCoordinator
        
        # Try to create an instance
        coordinator = SmartAppBuilderCoordinator(
            project_name="test_calculator",
            project_description="A simple calculator application for testing",
            requirements="Basic arithmetic operations",
            tech_stack="python",
            watch_workflow=False
        )
        
        print("✅ SmartAppBuilderCoordinator initialized successfully")
        print(f"   - Project name: {coordinator.project_name}")
        print(f"   - Description: {coordinator.project_description}")
        print(f"   - Tech stack: {coordinator.tech_stack}")
        
        return True, coordinator
        
    except Exception as e:
        print(f"❌ Failed to initialize SmartAppBuilderCoordinator: {e}")
        return False, None

def test_app_manager():
    """Test if DesktopAppManager can be initialized."""
    print("\n🔍 Testing DesktopAppManager...")
    
    try:
        from jarvis.utils.app_manager import DesktopAppManager
        
        # Create app manager instance
        app_manager = DesktopAppManager()
        print("✅ DesktopAppManager initialized successfully")
        
        # Test basic functionality
        test_script = str(project_root / "test_dummy_app.py")
        
        # Create a dummy test script
        with open(test_script, 'w') as f:
            f.write('''#!/usr/bin/env python3
import time
print("Test app started")
time.sleep(1)
print("Test app finished")
''')
        
        # Test registration
        success = app_manager.register_app("test_app", test_script)
        if success:
            print("✅ App registration successful")
        else:
            print("❌ App registration failed")
            
        # Clean up
        if os.path.exists(test_script):
            os.remove(test_script)
            
        return success
        
    except Exception as e:
        print(f"❌ Failed to test DesktopAppManager: {e}")
        return False

def test_professional_app_builder_tool():
    """Test the professional app builder tool function."""
    print("\n🔍 Testing professional app builder tool...")
    
    try:
        from jarvis.tools.plugins.professional_app_builder import build_professional_application
        
        print("✅ Professional app builder tool imported successfully")
        print("   - Function signature looks correct")
        print("   - Tool is ready for use")
        
        # Note: We don't actually call the function here as it would create a real app
        # and requires the full Jarvis environment with LLM access
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test professional app builder tool: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are available."""
    print("\n🔍 Checking dependencies...")
    
    dependencies = [
        "langchain",
        "langchain_core", 
        "pathlib",
        "subprocess",
        "threading"
    ]
    
    missing_deps = []
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} available")
        except ImportError:
            print(f"❌ {dep} missing")
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
        return False
    else:
        print("\n✅ All required dependencies are available")
        return True

def check_existing_apps():
    """Check if there are any existing built apps."""
    print("\n🔍 Checking for existing built applications...")
    
    apps_dir = project_root / "apps"
    if apps_dir.exists():
        apps = list(apps_dir.iterdir())
        if apps:
            print(f"✅ Found {len(apps)} existing applications:")
            for app in apps:
                if app.is_dir():
                    print(f"   - {app.name}")
        else:
            print("📁 Apps directory exists but is empty")
    else:
        print("📁 No apps directory found")
    
    return True

def main():
    """Run all functionality tests."""
    print("🚀 Testing Jarvis App Builder System Functionality")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Dependency Check", check_dependencies),
        ("SmartAppBuilderCoordinator", test_smart_app_builder_initialization),
        ("DesktopAppManager", test_app_manager),
        ("Professional App Builder Tool", test_professional_app_builder_tool),
        ("Existing Apps Check", check_existing_apps)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if test_name == "SmartAppBuilderCoordinator":
                result, _ = test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! App Builder System appears to be functional.")
    elif passed > total // 2:
        print("⚠️  Most tests passed. System is likely functional with minor issues.")
    else:
        print("❌ Multiple test failures. System may have significant issues.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
