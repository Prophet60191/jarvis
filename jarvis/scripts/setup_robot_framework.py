#!/usr/bin/env python3
"""
Setup script for Robot Framework integration with Jarvis Voice Assistant.

This script installs Robot Framework and its dependencies, sets up the
test environment, and validates the installation.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle errors."""
    print(f"Running: {description or ' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False


def install_robot_framework():
    """Install Robot Framework and required libraries."""
    print("🤖 Installing Robot Framework and dependencies...")
    
    packages = [
        "robotframework",
        "robotframework-seleniumlibrary",
        "robotframework-requests",
        "robotframework-sshlibrary",
        "robotframework-appiumlibrary",
        "robotframework-pabot",  # For parallel execution
        "robotframework-lint",   # For test validation
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        if not run_command([sys.executable, "-m", "pip", "install", package]):
            print(f"Failed to install {package}")
            return False
    
    print("✅ Robot Framework installation completed!")
    return True


def setup_test_environment():
    """Set up the test environment structure."""
    print("📁 Setting up test environment...")
    
    script_dir = Path(__file__).parent
    jarvis_root = script_dir.parent
    
    # Create test directories if they don't exist
    test_dirs = [
        jarvis_root / "tests" / "robot" / "keywords",
        jarvis_root / "tests" / "robot" / "suites",
        jarvis_root / "tests" / "robot" / "resources",
        jarvis_root / "tests" / "robot" / "libraries",
        jarvis_root / "tests" / "fixtures",
        jarvis_root / "test_results",
        jarvis_root / "logs",
    ]
    
    for test_dir in test_dirs:
        test_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {test_dir}")
    
    # Create .gitignore for test results
    gitignore_path = jarvis_root / "test_results" / ".gitignore"
    gitignore_content = """# Ignore all test result files
*
!.gitignore
"""
    gitignore_path.write_text(gitignore_content)
    
    print("✅ Test environment setup completed!")
    return True


def validate_installation():
    """Validate that Robot Framework is properly installed."""
    print("🔍 Validating Robot Framework installation...")

    # Check Robot Framework version (ignore exit code as --version returns 251)
    print("Checking Robot Framework version...")
    try:
        result = subprocess.run([sys.executable, "-m", "robot", "--version"],
                              capture_output=True, text=True)
        if "Robot Framework" in result.stdout:
            print(f"✅ {result.stdout.strip()}")
        else:
            print("❌ Robot Framework version check failed")
            return False
    except Exception as e:
        print(f"❌ Failed to check Robot Framework version: {e}")
        return False
    
    # Check if our custom library can be imported
    try:
        script_dir = Path(__file__).parent
        jarvis_root = script_dir.parent
        sys.path.insert(0, str(jarvis_root))
        
        from tests.robot.libraries.JarvisLibrary import JarvisLibrary
        print("✅ JarvisLibrary can be imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import JarvisLibrary: {e}")
        return False
    
    # Test basic Robot Framework functionality
    test_robot_content = """*** Test Cases ***
Basic Test
    Log    Robot Framework is working
"""
    
    script_dir = Path(__file__).parent
    jarvis_root = script_dir.parent
    test_file = jarvis_root / "test_results" / "validation_test.robot"
    test_file.write_text(test_robot_content)
    
    print("Running validation test...")
    if run_command([
        sys.executable, "-m", "robot",
        "--outputdir", str(jarvis_root / "test_results"),
        "--log", "validation_log.html",
        "--report", "validation_report.html",
        str(test_file)
    ], "Running Robot Framework validation test"):
        print("✅ Robot Framework validation test passed!")
        # Clean up test file
        test_file.unlink()
        return True
    else:
        print("❌ Robot Framework validation test failed!")
        return False


def create_test_runner_script():
    """Create a convenient test runner script."""
    print("📝 Creating test runner script...")
    
    script_dir = Path(__file__).parent
    jarvis_root = script_dir.parent
    
    # Make the test runner executable
    test_runner = jarvis_root / "scripts" / "run_robot_tests.py"
    if test_runner.exists():
        os.chmod(test_runner, 0o755)
        print(f"✅ Test runner script is ready: {test_runner}")
        return True
    else:
        print(f"❌ Test runner script not found: {test_runner}")
        return False


def print_usage_instructions():
    """Print usage instructions for Robot Framework testing."""
    print("\n" + "="*60)
    print("🎉 Robot Framework Setup Complete!")
    print("="*60)
    
    print("\n📋 Available Commands:")
    print("  # Run all tests")
    print("  python scripts/run_robot_tests.py")
    
    print("\n  # Run specific test suite")
    print("  python scripts/run_robot_tests.py --suite core_functionality")
    
    print("\n  # Run tests with specific tags")
    print("  python scripts/run_robot_tests.py --tags smoke")
    
    print("\n  # List available test suites")
    print("  python scripts/run_robot_tests.py --list-suites")
    
    print("\n  # Run with debug logging")
    print("  python scripts/run_robot_tests.py --log-level DEBUG")
    
    print("\n📁 Test Structure:")
    print("  tests/robot/suites/          - Test suites")
    print("  tests/robot/keywords/        - Reusable keywords")
    print("  tests/robot/libraries/       - Custom Python libraries")
    print("  tests/robot/resources/       - Test data and configs")
    print("  test_results/                - Test execution results")
    
    print("\n🔧 Next Steps:")
    print("  1. Review test configuration in tests/robot/resources/test_config.yaml")
    print("  2. Run a basic test: python scripts/run_robot_tests.py --tags smoke")
    print("  3. Check results in test_results/ directory")
    print("  4. Add your own test cases to tests/robot/suites/")
    
    print("\n📚 Documentation:")
    print("  - Robot Framework User Guide: https://robotframework.org/robotframework/")
    print("  - Jarvis Robot Integration: docs/ROBOT_FRAMEWORK_INTEGRATION_PLAN.md")


def main():
    """Main setup function."""
    print("🚀 Setting up Robot Framework for Jarvis Voice Assistant")
    print("="*60)
    
    steps = [
        ("Installing Robot Framework", install_robot_framework),
        ("Setting up test environment", setup_test_environment),
        ("Validating installation", validate_installation),
        ("Creating test runner script", create_test_runner_script),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 Step: {step_name}")
        print("-" * 40)
        
        if not step_func():
            print(f"❌ Failed at step: {step_name}")
            print("Setup incomplete. Please check the errors above.")
            return 1
    
    print_usage_instructions()
    return 0


if __name__ == "__main__":
    sys.exit(main())
