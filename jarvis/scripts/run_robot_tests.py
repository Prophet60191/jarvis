#!/usr/bin/env python3
"""
Robot Framework Test Execution Script for Jarvis Voice Assistant.

This script provides a convenient way to run Robot Framework tests
with various options and configurations.
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime


def setup_environment():
    """Set up the test environment."""
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    jarvis_root = script_dir.parent
    
    # Add jarvis to Python path
    os.environ['PYTHONPATH'] = str(jarvis_root)
    os.environ['JARVIS_TEST_MODE'] = 'true'
    
    # Create results directory
    results_dir = jarvis_root / "test_results"
    results_dir.mkdir(exist_ok=True)
    
    return jarvis_root, results_dir


def run_robot_tests(
    suite=None,
    tags=None,
    exclude_tags=None,
    output_dir=None,
    log_level="INFO",
    parallel=False,
    dry_run=False,
    variables=None
):
    """
    Run Robot Framework tests with specified parameters.
    
    Args:
        suite: Specific test suite to run
        tags: Tags to include
        exclude_tags: Tags to exclude
        output_dir: Output directory for results
        log_level: Logging level
        parallel: Run tests in parallel
        dry_run: Perform dry run without execution
        variables: Additional variables to pass
    
    Returns:
        bool: True if tests passed, False otherwise
    """
    jarvis_root, default_output_dir = setup_environment()
    
    if not output_dir:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = default_output_dir / f"robot_results_{timestamp}"
    
    # Build Robot Framework command
    cmd = ["robot"]
    
    # Add logging level
    cmd.extend(["--loglevel", log_level])
    
    # Add tags if specified
    if tags:
        for tag in tags:
            cmd.extend(["--include", tag])
    
    if exclude_tags:
        for tag in exclude_tags:
            cmd.extend(["--exclude", tag])
    
    # Add variables if specified
    if variables:
        for var_name, var_value in variables.items():
            cmd.extend(["--variable", f"{var_name}:{var_value}"])
    
    # Add output directory
    cmd.extend(["--outputdir", str(output_dir)])
    
    # Add report and log names with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cmd.extend([
        "--report", f"report_{timestamp}.html",
        "--log", f"log_{timestamp}.html",
        "--output", f"output_{timestamp}.xml"
    ])
    
    # Add dry run if specified
    if dry_run:
        cmd.append("--dryrun")
    
    # Add test suite path
    tests_dir = jarvis_root / "tests" / "robot"
    if suite:
        suite_path = tests_dir / "suites" / f"{suite}.robot"
        if not suite_path.exists():
            print(f"Error: Test suite '{suite}' not found at {suite_path}")
            return False
        cmd.append(str(suite_path))
    else:
        cmd.append(str(tests_dir / "suites"))
    
    print(f"Running Robot Framework tests...")
    print(f"Command: {' '.join(cmd)}")
    print(f"Output directory: {output_dir}")
    print("-" * 60)
    
    # Run the tests
    try:
        result = subprocess.run(cmd, cwd=str(jarvis_root))
        
        print("-" * 60)
        print(f"Tests completed with return code: {result.returncode}")
        print(f"Results saved to: {output_dir}")
        
        # Print summary
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed or had issues")
            
        return result.returncode == 0
        
    except FileNotFoundError:
        print("Error: Robot Framework not found. Please install it with:")
        print("pip install robotframework")
        return False
    except Exception as e:
        print(f"Error running tests: {e}")
        return False


def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Run Robot Framework tests for Jarvis Voice Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python run_robot_tests.py
  
  # Run specific test suite
  python run_robot_tests.py --suite core_functionality
  
  # Run tests with specific tags
  python run_robot_tests.py --tags smoke
  
  # Run tests excluding certain tags
  python run_robot_tests.py --exclude-tags slow
  
  # Run with debug logging
  python run_robot_tests.py --log-level DEBUG
  
  # Dry run to validate tests
  python run_robot_tests.py --dry-run
  
  # Run with custom variables
  python run_robot_tests.py --variable TIMEOUT:60s --variable DEBUG:true
        """
    )
    
    parser.add_argument(
        "--suite", "-s",
        help="Specific test suite to run (without .robot extension)"
    )
    
    parser.add_argument(
        "--tags", "-t",
        nargs="+",
        help="Tags to include in test execution"
    )
    
    parser.add_argument(
        "--exclude-tags", "-e",
        nargs="+",
        help="Tags to exclude from test execution"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        help="Output directory for test results"
    )
    
    parser.add_argument(
        "--log-level", "-l",
        choices=["TRACE", "DEBUG", "INFO", "WARN", "ERROR"],
        default="INFO",
        help="Logging level for test execution"
    )
    
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Run tests in parallel (requires pabot)"
    )
    
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Perform dry run without actually executing tests"
    )
    
    parser.add_argument(
        "--variable", "-v",
        action="append",
        help="Set variables for test execution (format: NAME:VALUE)"
    )
    
    parser.add_argument(
        "--list-suites",
        action="store_true",
        help="List available test suites"
    )
    
    args = parser.parse_args()
    
    # Handle list suites
    if args.list_suites:
        jarvis_root, _ = setup_environment()
        suites_dir = jarvis_root / "tests" / "robot" / "suites"
        
        print("Available test suites:")
        for suite_file in suites_dir.glob("*.robot"):
            suite_name = suite_file.stem
            print(f"  - {suite_name}")
        return 0
    
    # Parse variables
    variables = {}
    if args.variable:
        for var in args.variable:
            if ":" not in var:
                print(f"Error: Invalid variable format '{var}'. Use NAME:VALUE")
                return 1
            name, value = var.split(":", 1)
            variables[name] = value
    
    # Run tests
    success = run_robot_tests(
        suite=args.suite,
        tags=args.tags,
        exclude_tags=args.exclude_tags,
        output_dir=args.output_dir,
        log_level=args.log_level,
        parallel=args.parallel,
        dry_run=args.dry_run,
        variables=variables
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
