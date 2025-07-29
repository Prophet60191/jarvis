"""
Robot Framework Controller Plugin for Jarvis Voice Assistant.

This plugin allows users to run Robot Framework tests through voice commands
while Jarvis is running in regular mode.
"""

import asyncio
import logging
import os
import subprocess
import threading
from pathlib import Path
from typing import List, Optional

from langchain_core.tools import tool
from jarvis.tools.base import BaseTool
from jarvis.plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)


@tool
def run_robot_tests(test_type: str = "smoke", suite: str = "", tags: str = "", log_level: str = "INFO") -> str:
    """
    Run Robot Framework tests for Jarvis through voice commands.
    
    Use this tool when users ask to:
    - "Run tests" or "Test Jarvis"
    - "Run smoke tests" or "Check if everything is working"
    - "Run core functionality tests"
    - "Test Open Interpreter"
    - "Validate the system"
    - "Check system health"
    
    Args:
        test_type: Type of test to run - 'smoke', 'all', 'core', 'open-interpreter'
        suite: Specific test suite name (optional)
        tags: Specific tags to run (optional)
        log_level: Logging level - 'INFO', 'DEBUG', 'WARN'
    
    Returns:
        Test execution results and summary
    """
    try:
        logger.info(f"Running Robot Framework tests: type={test_type}, suite={suite}, tags={tags}")
        
        # Get the Jarvis root directory
        # The plugin is in jarvis/jarvis/tools/plugins/, so go up 4 levels to get to jarvis/
        current_file = Path(__file__)
        jarvis_root = current_file.parent.parent.parent.parent
        
        # Verify the script exists
        script_path = jarvis_root / "scripts" / "run_robot_tests.py"
        if not script_path.exists():
            return f"❌ Robot Framework test script not found at: {script_path}\n\nPlease ensure the Robot Framework integration is properly set up."

        # Build the test command
        cmd = ["python", str(script_path)]
        
        # Add log level
        cmd.extend(["--log-level", log_level])
        
        # Determine what tests to run based on test_type
        if test_type.lower() == "smoke":
            cmd.extend(["--tags", "smoke"])
            test_description = "smoke tests (essential functionality)"
        elif test_type.lower() == "all":
            test_description = "all tests"
        elif test_type.lower() == "core":
            cmd.extend(["--suite", "core_functionality"])
            test_description = "core functionality tests"
        elif test_type.lower() in ["open-interpreter", "open_interpreter", "interpreter"]:
            cmd.extend(["--suite", "open_interpreter_tests"])
            test_description = "Open Interpreter tests"
        elif suite:
            cmd.extend(["--suite", suite])
            test_description = f"{suite} test suite"
        elif tags:
            cmd.extend(["--tags", tags])
            test_description = f"tests with tags: {tags}"
        else:
            # Default to smoke tests
            cmd.extend(["--tags", "smoke"])
            test_description = "smoke tests (default)"
        
        # Create a unique output directory
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = jarvis_root / "test_results" / f"voice_triggered_{timestamp}"
        cmd.extend(["--output-dir", str(output_dir)])
        
        logger.info(f"Starting {test_description}...")
        
        # Run tests in a separate process to avoid conflicts
        result = subprocess.run(
            cmd,
            cwd=str(jarvis_root),
            capture_output=True,
            text=True,
            timeout=60  # 1 minute timeout for voice commands
        )
        
        # Parse the results
        success = result.returncode == 0
        
        # Extract test summary from output
        output_lines = result.stdout.split('\n')
        summary_line = ""
        for line in reversed(output_lines):
            if "tests," in line and ("passed" in line or "failed" in line):
                summary_line = line.strip()
                break
        
        if success:
            response = f"✅ Test execution completed successfully!\n\n"
            response += f"📋 Ran: {test_description}\n"
            if summary_line:
                response += f"📊 Results: {summary_line}\n"
            response += f"📁 Detailed reports saved to: {output_dir.name}\n\n"
            response += "All tests passed! Your Jarvis system is working correctly."
        else:
            response = f"❌ Test execution completed with issues.\n\n"
            response += f"📋 Ran: {test_description}\n"
            if summary_line:
                response += f"📊 Results: {summary_line}\n"
            response += f"📁 Detailed reports saved to: {output_dir.name}\n\n"
            response += "Some tests failed. Check the HTML reports for details."
            
            # Include error information if available
            if result.stderr:
                response += f"\n🔍 Error details:\n{result.stderr[:500]}"
        
        logger.info(f"Test execution completed: success={success}")
        return response
        
    except subprocess.TimeoutExpired:
        error_msg = f"⏰ Test execution timed out after 1 minute.\n\nThe {test_description} took too long to complete. You can run tests manually with:\n\npython scripts/run_robot_tests.py --tags {test_type}"
        logger.error("Test execution timed out")
        return error_msg
        
    except Exception as e:
        error_msg = f"❌ Failed to run tests: {str(e)}\n\nThere was an error executing the Robot Framework tests. Please check that the test system is properly set up."
        logger.error(f"Test execution failed: {e}")
        return error_msg


@tool
def check_test_results(result_dir: str = "latest") -> str:
    """
    Check the results of previously run Robot Framework tests.
    
    Use this tool when users ask to:
    - "Check test results" or "Show me the test results"
    - "What were the results of the last test"
    - "Did the tests pass"
    - "Show me test reports"
    
    Args:
        result_dir: Which results to check - 'latest' or specific directory name
    
    Returns:
        Summary of test results and report locations
    """
    try:
        # Get the Jarvis root directory
        # The plugin is in jarvis/jarvis/tools/plugins/, so go up 4 levels to get to jarvis/
        current_file = Path(__file__)
        jarvis_root = current_file.parent.parent.parent.parent
        test_results_dir = jarvis_root / "test_results"
        
        if not test_results_dir.exists():
            return "📁 No test results found. Run some tests first with 'run tests' or 'test Jarvis'."
        
        # Find the latest results directory
        if result_dir == "latest":
            result_dirs = [d for d in test_results_dir.iterdir() if d.is_dir() and d.name.startswith(('robot_results_', 'voice_triggered_'))]
            if not result_dirs:
                return "📁 No test results found. Run some tests first with 'run tests' or 'test Jarvis'."
            
            # Get the most recent directory
            latest_dir = max(result_dirs, key=lambda d: d.stat().st_mtime)
        else:
            latest_dir = test_results_dir / result_dir
            if not latest_dir.exists():
                return f"📁 Test results directory '{result_dir}' not found."
        
        # Look for result files
        report_files = list(latest_dir.glob("report_*.html"))
        log_files = list(latest_dir.glob("log_*.html"))
        output_files = list(latest_dir.glob("output_*.xml"))
        
        if not report_files:
            return f"📁 No test reports found in {latest_dir.name}."
        
        # Try to extract summary from the output file
        summary = "Results available"
        if output_files:
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(output_files[0])
                root = tree.getroot()
                
                # Extract test statistics
                stats = root.find('.//statistics/total/stat')
                if stats is not None:
                    total = stats.get('pass', '0')
                    failed = stats.get('fail', '0')
                    summary = f"{total} passed, {failed} failed"
            except Exception:
                pass  # If XML parsing fails, use default summary
        
        response = f"📊 Latest Test Results ({latest_dir.name}):\n\n"
        response += f"📈 Summary: {summary}\n"
        response += f"📁 Location: test_results/{latest_dir.name}/\n\n"
        response += "📋 Available Reports:\n"
        
        if report_files:
            response += f"• Executive Report: {report_files[0].name}\n"
        if log_files:
            response += f"• Detailed Log: {log_files[0].name}\n"
        if output_files:
            response += f"• Raw Results: {output_files[0].name}\n"
        
        response += f"\n💡 To view detailed results, open the HTML files in your browser from the test_results/{latest_dir.name}/ directory."
        
        return response
        
    except Exception as e:
        error_msg = f"❌ Failed to check test results: {str(e)}"
        logger.error(f"Failed to check test results: {e}")
        return error_msg


@tool
def validate_test_system() -> str:
    """
    Validate that the Robot Framework test system is ready.

    Use this tool when users ask:
    - "Is the test system ready"
    - "Can I run tests"
    - "Check test setup"

    Returns:
        Status of the test system setup
    """
    try:
        # Get the Jarvis root directory
        current_file = Path(__file__)
        jarvis_root = current_file.parent.parent.parent.parent

        # Check if script exists
        script_path = jarvis_root / "scripts" / "run_robot_tests.py"
        if not script_path.exists():
            return f"❌ Test script not found at: {script_path}\n\nRobot Framework integration needs to be set up."

        # Check if test directories exist
        test_dir = jarvis_root / "tests" / "robot"
        if not test_dir.exists():
            return f"❌ Test directory not found at: {test_dir}\n\nRobot Framework tests need to be created."

        # Check for test suites
        suites_dir = test_dir / "suites"
        if not suites_dir.exists():
            return f"❌ Test suites directory not found at: {suites_dir}"

        suite_files = list(suites_dir.glob("*.robot"))
        if not suite_files:
            return f"❌ No test suite files found in: {suites_dir}"

        # All checks passed
        response = "✅ Robot Framework test system is ready!\n\n"
        response += f"📁 Test script: {script_path.name}\n"
        response += f"📁 Test directory: {test_dir}\n"
        response += f"📋 Found {len(suite_files)} test suites:\n"
        for suite_file in suite_files:
            response += f"  • {suite_file.stem}\n"

        response += "\n🎤 You can now run tests with voice commands like:\n"
        response += "• 'Run smoke tests'\n"
        response += "• 'Test core functionality'\n"
        response += "• 'Run all tests'"

        return response

    except Exception as e:
        return f"❌ Error validating test system: {str(e)}"


@tool
def list_available_tests() -> str:
    """
    List available Robot Framework test suites and tags.
    
    Use this tool when users ask:
    - "What tests are available"
    - "Show me test options"
    - "What can I test"
    - "List test suites"
    
    Returns:
        List of available test suites and common test tags
    """
    try:
        # Get the Jarvis root directory
        # The plugin is in jarvis/jarvis/tools/plugins/, so go up 4 levels to get to jarvis/
        current_file = Path(__file__)
        jarvis_root = current_file.parent.parent.parent.parent
        
        # Run the list-suites command
        cmd = ["python", "scripts/run_robot_tests.py", "--list-suites"]
        result = subprocess.run(
            cmd,
            cwd=str(jarvis_root),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        response = "🧪 Available Robot Framework Tests:\n\n"
        
        if result.returncode == 0:
            response += "📋 Test Suites:\n"
            response += result.stdout
        else:
            response += "📋 Test Suites:\n"
            response += "• core_functionality - Core Jarvis functionality tests\n"
            response += "• open_interpreter_tests - Open Interpreter integration tests\n"
        
        response += "\n🏷️ Common Test Types:\n"
        response += "• smoke - Essential functionality (fastest)\n"
        response += "• core - Core system tests\n"
        response += "• memory - Memory system tests\n"
        response += "• open-interpreter - Code execution tests\n"
        response += "• performance - Performance and timing tests\n"
        response += "• error-handling - Error handling validation\n"
        
        response += "\n🎤 Voice Commands:\n"
        response += "• 'Run smoke tests' - Quick essential tests\n"
        response += "• 'Test core functionality' - Core system tests\n"
        response += "• 'Test Open Interpreter' - Code execution tests\n"
        response += "• 'Run all tests' - Complete test suite\n"
        response += "• 'Check test results' - View latest results\n"
        
        return response
        
    except Exception as e:
        error_msg = f"❌ Failed to list available tests: {str(e)}"
        logger.error(f"Failed to list tests: {e}")
        return error_msg


class RobotFrameworkControllerPlugin(PluginBase):
    """Plugin that provides voice-controlled Robot Framework test execution."""

    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="RobotFrameworkController",
            version="1.0.0",
            description="Voice-controlled Robot Framework test execution and results checking",
            author="Jarvis Team"
        )

    def get_tools(self) -> List[BaseTool]:
        """Return the Robot Framework controller tools."""
        return [run_robot_tests, check_test_results, list_available_tests, validate_test_system]


# Required variables for plugin discovery system
PLUGIN_CLASS = RobotFrameworkControllerPlugin
PLUGIN_METADATA = RobotFrameworkControllerPlugin().get_metadata()
