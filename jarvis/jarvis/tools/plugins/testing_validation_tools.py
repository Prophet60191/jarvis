"""
Testing & Validation Tools

System-wide tools for application testing, syntax validation, and quality assurance.
These tools enable Jarvis to test applications, validate code, and ensure quality.
"""

import os
import sys
import subprocess
import ast
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from langchain.tools import tool
import importlib.util
import tempfile

from jarvis.plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)


@tool
def validate_python_syntax(file_path: str) -> str:
    """
    Validate Python file syntax and check for basic errors.
    
    Args:
        file_path: Path to Python file to validate
        
    Returns:
        Syntax validation results
    """
    try:
        logger.info(f"Validating Python syntax: {file_path}")
        
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return f"❌ File not found: {file_path}"
        
        if not file_path_obj.suffix == '.py':
            return f"❌ Not a Python file: {file_path}"
        
        # Read file content
        with open(file_path_obj, 'r', encoding='utf-8') as f:
            content = f.read()
        
        output = f"🔍 Python Syntax Validation: {file_path}\n"
        output += "=" * 50 + "\n\n"
        
        # Check syntax using ast.parse
        try:
            ast.parse(content)
            output += "✅ Syntax is valid\n"
            syntax_valid = True
        except SyntaxError as e:
            output += f"❌ Syntax Error:\n"
            output += f"   Line {e.lineno}: {e.text.strip() if e.text else 'Unknown'}\n"
            output += f"   Error: {e.msg}\n"
            syntax_valid = False
        
        # Additional checks if syntax is valid
        if syntax_valid:
            # Check for common issues
            issues = []
            
            # Check for missing imports
            if 'tkinter' in content and 'import tkinter' not in content and 'from tkinter' not in content:
                issues.append("⚠️ Uses 'tkinter' but no import found")
            
            # Check for undefined variables (basic check)
            if 'print(' in content and content.count('print(') > 2:
                issues.append("ℹ️ Multiple print statements found (consider using logging)")
            
            # Check for main guard
            if 'def main(' in content and 'if __name__ == "__main__"' not in content:
                issues.append("⚠️ Has main() function but no __name__ guard")
            
            if issues:
                output += "\n🔍 ADDITIONAL CHECKS:\n"
                for issue in issues:
                    output += f"{issue}\n"
            else:
                output += "\n✅ No additional issues found\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Syntax validation failed: {e}")
        return f"❌ Syntax validation failed: {str(e)}"


@tool
def check_python_imports(file_path: str) -> str:
    """
    Check if all imports in a Python file are available.
    
    Args:
        file_path: Path to Python file to check
        
    Returns:
        Import validation results
    """
    try:
        logger.info(f"Checking Python imports: {file_path}")
        
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return f"❌ File not found: {file_path}"
        
        # Read file content
        with open(file_path_obj, 'r', encoding='utf-8') as f:
            content = f.read()
        
        output = f"📦 Import Check: {file_path}\n"
        output += "=" * 40 + "\n\n"
        
        # Parse imports
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return f"❌ Cannot check imports due to syntax error: {e.msg}"
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        if not imports:
            return output + "ℹ️ No imports found in file\n"
        
        # Check each import
        available_imports = []
        missing_imports = []
        
        for imp in imports:
            try:
                # Try to find the module
                spec = importlib.util.find_spec(imp)
                if spec is not None:
                    available_imports.append(imp)
                else:
                    missing_imports.append(imp)
            except (ImportError, ModuleNotFoundError, ValueError):
                missing_imports.append(imp)
        
        # Report results
        if available_imports:
            output += "✅ AVAILABLE IMPORTS:\n"
            for imp in available_imports:
                output += f"   ✅ {imp}\n"
        
        if missing_imports:
            output += "\n❌ MISSING IMPORTS:\n"
            for imp in missing_imports:
                output += f"   ❌ {imp}\n"
            output += "\n💡 Install missing packages with: pip install <package_name>\n"
        else:
            output += "\n🎉 All imports are available!\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Import check failed: {e}")
        return f"❌ Import check failed: {str(e)}"


@tool
def test_python_application(file_path: str, timeout: int = 10) -> str:
    """
    Test a Python application by running it briefly to check for runtime errors.
    
    Args:
        file_path: Path to Python application to test
        timeout: Maximum time to run the application (seconds)
        
    Returns:
        Application test results
    """
    try:
        logger.info(f"Testing Python application: {file_path}")
        
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return f"❌ File not found: {file_path}"
        
        output = f"🧪 Application Test: {file_path}\n"
        output += "=" * 40 + "\n\n"
        
        # First check syntax
        with open(file_path_obj, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            ast.parse(content)
            output += "✅ Syntax validation passed\n"
        except SyntaxError as e:
            return output + f"❌ Syntax error prevents testing: {e.msg}\n"
        
        # Run the application
        try:
            # Use the virtual environment Python if available
            project_dir = file_path_obj.parent
            venv_python = None
            
            # Check for virtual environment
            venv_paths = [
                project_dir / "venv" / "bin" / "python",  # Unix
                project_dir / "venv" / "Scripts" / "python.exe",  # Windows
                project_dir / ".venv" / "bin" / "python",  # Unix
                project_dir / ".venv" / "Scripts" / "python.exe"  # Windows
            ]
            
            for venv_path in venv_paths:
                if venv_path.exists():
                    venv_python = str(venv_path)
                    break
            
            python_cmd = venv_python or sys.executable
            
            # Run application with timeout
            result = subprocess.run([
                python_cmd, str(file_path_obj)
            ], cwd=file_path_obj.parent, capture_output=True, text=True, timeout=timeout)
            
            output += f"🔧 Command: {python_cmd} {file_path_obj.name}\n"
            output += f"⏱️ Timeout: {timeout} seconds\n"
            output += f"🔄 Return Code: {result.returncode}\n\n"
            
            if result.stdout:
                output += f"📤 STDOUT:\n{result.stdout}\n"
            
            if result.stderr:
                output += f"⚠️ STDERR:\n{result.stderr}\n"
            
            if result.returncode == 0:
                output += "✅ Application ran without errors!\n"
            else:
                output += f"❌ Application exited with error code {result.returncode}\n"
            
        except subprocess.TimeoutExpired:
            output += f"⏰ Application ran for {timeout} seconds (timeout reached)\n"
            output += "ℹ️ This might be normal for GUI applications\n"
            output += "✅ No immediate startup errors detected\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Application test failed: {e}")
        return f"❌ Application test failed: {str(e)}"


@tool
def run_python_tests(project_path: str, test_pattern: str = "test_*.py") -> str:
    """
    Run Python unit tests in a project directory.
    
    Args:
        project_path: Path to project directory
        test_pattern: Pattern to match test files
        
    Returns:
        Test execution results
    """
    try:
        logger.info(f"Running Python tests in: {project_path}")
        
        project_dir = Path(project_path)
        if not project_dir.exists():
            return f"❌ Project directory not found: {project_path}"
        
        # Find test files
        test_files = list(project_dir.rglob(test_pattern))
        
        output = f"🧪 Python Tests: {project_path}\n"
        output += "=" * 40 + "\n\n"
        output += f"🔍 Pattern: {test_pattern}\n"
        output += f"📄 Found {len(test_files)} test files\n\n"
        
        if not test_files:
            return output + "ℹ️ No test files found\n"
        
        # List found test files
        output += "📋 TEST FILES:\n"
        for test_file in test_files:
            relative_path = test_file.relative_to(project_dir)
            output += f"   📄 {relative_path}\n"
        
        # Try to run tests with pytest first, then unittest
        python_cmd = sys.executable
        
        # Check for virtual environment
        venv_paths = [
            project_dir / "venv" / "bin" / "python",
            project_dir / "venv" / "Scripts" / "python.exe",
        ]
        
        for venv_path in venv_paths:
            if venv_path.exists():
                python_cmd = str(venv_path)
                break
        
        # Try pytest first
        try:
            pytest_result = subprocess.run([
                python_cmd, "-m", "pytest", "-v"
            ], cwd=project_dir, capture_output=True, text=True, timeout=60)
            
            output += f"\n🔬 PYTEST RESULTS:\n"
            output += f"Return Code: {pytest_result.returncode}\n"
            
            if pytest_result.stdout:
                output += f"Output:\n{pytest_result.stdout}\n"
            
            if pytest_result.stderr:
                output += f"Errors:\n{pytest_result.stderr}\n"
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback to unittest
            output += f"\n🔬 UNITTEST RESULTS:\n"
            
            try:
                unittest_result = subprocess.run([
                    python_cmd, "-m", "unittest", "discover", "-v"
                ], cwd=project_dir, capture_output=True, text=True, timeout=60)
                
                output += f"Return Code: {unittest_result.returncode}\n"
                
                if unittest_result.stdout:
                    output += f"Output:\n{unittest_result.stdout}\n"
                
                if unittest_result.stderr:
                    output += f"Errors:\n{unittest_result.stderr}\n"
                
            except subprocess.TimeoutExpired:
                output += "⏰ Tests timed out after 60 seconds\n"
            except Exception as e:
                output += f"❌ Test execution failed: {str(e)}\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return f"❌ Test execution failed: {str(e)}"


@tool
def validate_project_structure(project_path: str) -> str:
    """
    Validate project structure and check for common issues.
    
    Args:
        project_path: Path to project directory
        
    Returns:
        Project structure validation results
    """
    try:
        logger.info(f"Validating project structure: {project_path}")
        
        project_dir = Path(project_path)
        if not project_dir.exists():
            return f"❌ Project directory not found: {project_path}"
        
        output = f"🏗️ Project Structure Validation: {project_path}\n"
        output += "=" * 50 + "\n\n"
        
        # Check for essential files
        essential_files = {
            "README.md": "Project documentation",
            "requirements.txt": "Python dependencies",
            ".gitignore": "Git ignore rules"
        }
        
        output += "📄 ESSENTIAL FILES:\n"
        for filename, description in essential_files.items():
            file_path = project_dir / filename
            if file_path.exists():
                size = file_path.stat().st_size
                output += f"   ✅ {filename} ({size} bytes) - {description}\n"
            else:
                output += f"   ⚠️ {filename} - Missing ({description})\n"
        
        # Check for Python files
        python_files = list(project_dir.rglob("*.py"))
        output += f"\n🐍 PYTHON FILES: {len(python_files)} found\n"
        
        if python_files:
            main_files = [f for f in python_files if f.name in ['main.py', 'app.py', '__main__.py']]
            if main_files:
                output += f"   ✅ Main file found: {main_files[0].name}\n"
            else:
                output += f"   ⚠️ No main file found (main.py, app.py, __main__.py)\n"
        
        # Check directory structure
        common_dirs = ['src', 'tests', 'docs', 'scripts']
        output += f"\n📁 DIRECTORIES:\n"
        for dirname in common_dirs:
            dir_path = project_dir / dirname
            if dir_path.exists() and dir_path.is_dir():
                file_count = len(list(dir_path.rglob("*")))
                output += f"   ✅ {dirname}/ ({file_count} items)\n"
            else:
                output += f"   ℹ️ {dirname}/ - Not present\n"
        
        # Check for virtual environment
        venv_paths = ['venv', '.venv', 'env', '.env']
        venv_found = False
        for venv_name in venv_paths:
            venv_path = project_dir / venv_name
            if venv_path.exists() and venv_path.is_dir():
                output += f"\n🐍 Virtual Environment: {venv_name}/ found\n"
                venv_found = True
                break
        
        if not venv_found:
            output += f"\n⚠️ No virtual environment found\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Project validation failed: {e}")
        return f"❌ Project validation failed: {str(e)}"


class TestingValidationPlugin(PluginBase):
    """Plugin providing testing and validation tools."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="TestingValidation",
            version="1.0.0",
            description="Application testing, syntax validation, and quality assurance tools",
            author="Jarvis Team",
            dependencies=[]
        )
    
    def get_tools(self):
        return [
            validate_python_syntax,
            check_python_imports,
            test_python_application,
            run_python_tests,
            validate_project_structure
        ]
