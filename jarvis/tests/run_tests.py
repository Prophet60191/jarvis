#!/usr/bin/env python3
"""
Test runner for Jarvis Voice Assistant.

This script provides a convenient way to run all tests with proper
configuration and reporting.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd or project_root,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_dependencies():
    """Check if required test dependencies are installed."""
    print("🔍 Checking test dependencies...")
    
    required_packages = [
        'pytest',
        'pytest-cov',
        'pytest-mock',
        'pytest-asyncio'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        success, _, _ = run_command(f"python -c 'import {package.replace('-', '_')}'")
        if not success:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All test dependencies are installed")
    return True


def run_unit_tests(verbose=False, coverage=False):
    """Run unit tests."""
    print("\n🧪 Running unit tests...")
    
    cmd = "python -m pytest tests/unit/"
    
    if verbose:
        cmd += " -v"
    
    if coverage:
        cmd += " --cov=jarvis --cov-report=term-missing --cov-report=html"
    
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✅ Unit tests passed")
        if stdout:
            print(stdout)
    else:
        print("❌ Unit tests failed")
        if stderr:
            print(stderr)
        if stdout:
            print(stdout)
    
    return success


def run_integration_tests(verbose=False):
    """Run integration tests."""
    print("\n🔗 Running integration tests...")
    
    cmd = "python -m pytest tests/integration/"
    
    if verbose:
        cmd += " -v"
    
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✅ Integration tests passed")
        if stdout:
            print(stdout)
    else:
        print("❌ Integration tests failed")
        if stderr:
            print(stderr)
        if stdout:
            print(stdout)
    
    return success


def run_all_tests(verbose=False, coverage=False):
    """Run all tests."""
    print("\n🚀 Running all tests...")
    
    cmd = "python -m pytest tests/"
    
    if verbose:
        cmd += " -v"
    
    if coverage:
        cmd += " --cov=jarvis --cov-report=term-missing --cov-report=html"
    
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✅ All tests passed")
        if stdout:
            print(stdout)
    else:
        print("❌ Some tests failed")
        if stderr:
            print(stderr)
        if stdout:
            print(stdout)
    
    return success


def run_linting():
    """Run code linting."""
    print("\n🔍 Running code linting...")
    
    # Check if flake8 is available
    success, _, _ = run_command("python -c 'import flake8'")
    if not success:
        print("⚠️  flake8 not installed, skipping linting")
        return True
    
    cmd = "python -m flake8 jarvis/ tests/ --max-line-length=120 --ignore=E203,W503"
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✅ Code linting passed")
    else:
        print("❌ Code linting failed")
        if stdout:
            print(stdout)
        if stderr:
            print(stderr)
    
    return success


def run_type_checking():
    """Run type checking with mypy."""
    print("\n🔍 Running type checking...")
    
    # Check if mypy is available
    success, _, _ = run_command("python -c 'import mypy'")
    if not success:
        print("⚠️  mypy not installed, skipping type checking")
        return True
    
    cmd = "python -m mypy jarvis/ --ignore-missing-imports --no-strict-optional"
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✅ Type checking passed")
    else:
        print("❌ Type checking failed")
        if stdout:
            print(stdout)
        if stderr:
            print(stderr)
    
    return success


def generate_test_report():
    """Generate a comprehensive test report."""
    print("\n📊 Generating test report...")
    
    cmd = ("python -m pytest tests/ --cov=jarvis --cov-report=html --cov-report=xml "
           "--junit-xml=test-results.xml -v")
    
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✅ Test report generated")
        print("📁 HTML coverage report: htmlcov/index.html")
        print("📁 XML coverage report: coverage.xml")
        print("📁 JUnit test results: test-results.xml")
    else:
        print("❌ Test report generation failed")
        if stderr:
            print(stderr)
    
    return success


def clean_test_artifacts():
    """Clean up test artifacts."""
    print("\n🧹 Cleaning test artifacts...")
    
    artifacts = [
        "htmlcov/",
        "coverage.xml",
        "test-results.xml",
        ".coverage",
        ".pytest_cache/",
        "__pycache__/",
        "*.pyc"
    ]
    
    for artifact in artifacts:
        if "*" in artifact:
            success, _, _ = run_command(f"find . -name '{artifact}' -delete")
        else:
            artifact_path = project_root / artifact
            if artifact_path.exists():
                if artifact_path.is_dir():
                    success, _, _ = run_command(f"rm -rf {artifact_path}")
                else:
                    success, _, _ = run_command(f"rm -f {artifact_path}")
    
    print("✅ Test artifacts cleaned")


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Jarvis Voice Assistant Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--lint", action="store_true", help="Run code linting")
    parser.add_argument("--type-check", action="store_true", help="Run type checking")
    parser.add_argument("--report", action="store_true", help="Generate comprehensive test report")
    parser.add_argument("--clean", action="store_true", help="Clean test artifacts")
    parser.add_argument("--all", action="store_true", help="Run all tests and checks")
    
    args = parser.parse_args()
    
    print("🤖 Jarvis Voice Assistant Test Runner")
    print("=" * 50)
    
    # Clean artifacts if requested
    if args.clean:
        clean_test_artifacts()
        return 0
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    success = True
    
    # Run specific test types
    if args.unit:
        success &= run_unit_tests(verbose=args.verbose, coverage=args.coverage)
    elif args.integration:
        success &= run_integration_tests(verbose=args.verbose)
    elif args.report:
        success &= generate_test_report()
    elif args.all:
        success &= run_unit_tests(verbose=args.verbose, coverage=args.coverage)
        success &= run_integration_tests(verbose=args.verbose)
        if args.lint:
            success &= run_linting()
        if args.type_check:
            success &= run_type_checking()
    else:
        # Default: run all tests
        success &= run_all_tests(verbose=args.verbose, coverage=args.coverage)
    
    # Run additional checks if requested
    if args.lint and not args.all:
        success &= run_linting()
    
    if args.type_check and not args.all:
        success &= run_type_checking()
    
    # Print summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests and checks passed!")
        return 0
    else:
        print("❌ Some tests or checks failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
