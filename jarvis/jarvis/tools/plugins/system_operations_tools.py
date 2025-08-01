"""
System Operations Tools

System-wide tools for environment management, command execution, and system-level operations.
These tools enable Jarvis to create virtual environments, install packages, and perform system tasks.
"""

import os
import sys
import subprocess
import logging
import shutil
import platform
from typing import Dict, Any, List, Optional
from pathlib import Path
from langchain.tools import tool

from jarvis.plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)


@tool
def run_system_command(command: str, working_directory: str = "", timeout: int = 300) -> str:
    """
    Execute system commands safely with proper error handling and output capture.
    
    Args:
        command: Command to execute (e.g., "pip install requests", "python --version")
        working_directory: Directory to run command in (default: current directory)
        timeout: Command timeout in seconds (default: 300)
        
    Returns:
        Command output and execution status
    """
    try:
        logger.info(f"Executing command: {command}")
        
        # Set working directory
        cwd = Path(working_directory) if working_directory else Path.cwd()
        if not cwd.exists():
            return f"❌ Working directory does not exist: {cwd}"
        
        # Execute command
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Format output
        output = f"🔧 Command: {command}\n"
        output += f"📁 Directory: {cwd}\n"
        output += f"🔄 Return Code: {result.returncode}\n\n"
        
        if result.stdout:
            output += f"📤 STDOUT:\n{result.stdout}\n"
        
        if result.stderr:
            output += f"⚠️ STDERR:\n{result.stderr}\n"
        
        if result.returncode == 0:
            output += "✅ Command executed successfully"
        else:
            output += f"❌ Command failed with return code {result.returncode}"
        
        return output
        
    except subprocess.TimeoutExpired:
        return f"❌ Command timed out after {timeout} seconds: {command}"
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        return f"❌ Command execution failed: {str(e)}"


@tool
def create_virtual_environment(project_path: str, python_version: str = "") -> str:
    """
    Create a Python virtual environment for a project.
    
    Args:
        project_path: Path where to create the virtual environment
        python_version: Specific Python version to use (optional)
        
    Returns:
        Virtual environment creation status and activation instructions
    """
    try:
        logger.info(f"Creating virtual environment at: {project_path}")
        
        project_dir = Path(project_path)
        project_dir.mkdir(parents=True, exist_ok=True)
        
        venv_path = project_dir / "venv"
        
        # Choose Python executable
        if python_version:
            python_cmd = f"python{python_version}"
        else:
            python_cmd = sys.executable
        
        # Create virtual environment
        result = subprocess.run([
            python_cmd, "-m", "venv", str(venv_path)
        ], capture_output=True, text=True, cwd=project_dir)
        
        if result.returncode != 0:
            return f"❌ Virtual environment creation failed:\n{result.stderr}"
        
        # Get activation commands for different platforms
        if platform.system() == "Windows":
            activate_cmd = f"{venv_path}\\Scripts\\activate"
            pip_path = f"{venv_path}\\Scripts\\pip"
            python_path = f"{venv_path}\\Scripts\\python"
        else:
            activate_cmd = f"source {venv_path}/bin/activate"
            pip_path = f"{venv_path}/bin/pip"
            python_path = f"{venv_path}/bin/python"
        
        output = f"✅ Virtual environment created successfully!\n\n"
        output += f"📁 Location: {venv_path}\n"
        output += f"🐍 Python: {python_path}\n"
        output += f"📦 Pip: {pip_path}\n\n"
        output += f"🔧 To activate:\n{activate_cmd}\n\n"
        output += f"💡 Virtual environment is ready for use!"
        
        return output
        
    except Exception as e:
        logger.error(f"Virtual environment creation failed: {e}")
        return f"❌ Virtual environment creation failed: {str(e)}"


@tool
def install_python_package(package_name: str, project_path: str = "", use_venv: bool = True) -> str:
    """
    Install Python packages using pip, optionally in a virtual environment.
    
    Args:
        package_name: Package to install (e.g., "requests", "tkinter", "flask==2.0.1")
        project_path: Project directory containing virtual environment
        use_venv: Whether to use virtual environment if available
        
    Returns:
        Package installation status and details
    """
    try:
        logger.info(f"Installing Python package: {package_name}")
        
        # Determine pip command
        if use_venv and project_path:
            project_dir = Path(project_path)
            venv_path = project_dir / "venv"
            
            if venv_path.exists():
                if platform.system() == "Windows":
                    pip_cmd = str(venv_path / "Scripts" / "pip")
                else:
                    pip_cmd = str(venv_path / "bin" / "pip")
            else:
                pip_cmd = "pip"
        else:
            pip_cmd = "pip"
        
        # Install package
        command = f"{pip_cmd} install {package_name}"
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        output = f"📦 Installing: {package_name}\n"
        output += f"🔧 Command: {command}\n"
        output += f"🔄 Return Code: {result.returncode}\n\n"
        
        if result.stdout:
            output += f"📤 Installation Output:\n{result.stdout}\n"
        
        if result.stderr:
            output += f"⚠️ Warnings/Errors:\n{result.stderr}\n"
        
        if result.returncode == 0:
            output += f"✅ Package '{package_name}' installed successfully!"
        else:
            output += f"❌ Package installation failed"
        
        return output
        
    except Exception as e:
        logger.error(f"Package installation failed: {e}")
        return f"❌ Package installation failed: {str(e)}"


@tool
def install_requirements_file(requirements_file: str, project_path: str = "") -> str:
    """
    Install packages from a requirements.txt file.
    
    Args:
        requirements_file: Path to requirements.txt file
        project_path: Project directory (for virtual environment detection)
        
    Returns:
        Installation status for all requirements
    """
    try:
        logger.info(f"Installing from requirements file: {requirements_file}")
        
        req_path = Path(requirements_file)
        if not req_path.exists():
            return f"❌ Requirements file not found: {requirements_file}"
        
        # Determine pip command
        if project_path:
            project_dir = Path(project_path)
            venv_path = project_dir / "venv"
            
            if venv_path.exists():
                if platform.system() == "Windows":
                    pip_cmd = str(venv_path / "Scripts" / "pip")
                else:
                    pip_cmd = str(venv_path / "bin" / "pip")
            else:
                pip_cmd = "pip"
        else:
            pip_cmd = "pip"
        
        # Install requirements
        command = f"{pip_cmd} install -r {requirements_file}"
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=600  # Longer timeout for multiple packages
        )
        
        output = f"📋 Installing from: {requirements_file}\n"
        output += f"🔧 Command: {command}\n"
        output += f"🔄 Return Code: {result.returncode}\n\n"
        
        if result.stdout:
            output += f"📤 Installation Output:\n{result.stdout}\n"
        
        if result.stderr:
            output += f"⚠️ Warnings/Errors:\n{result.stderr}\n"
        
        if result.returncode == 0:
            output += f"✅ All requirements installed successfully!"
        else:
            output += f"❌ Requirements installation failed"
        
        return output
        
    except Exception as e:
        logger.error(f"Requirements installation failed: {e}")
        return f"❌ Requirements installation failed: {str(e)}"


@tool
def check_system_info() -> str:
    """
    Get system information including Python version, platform, and available tools.
    
    Returns:
        Comprehensive system information
    """
    try:
        logger.info("Gathering system information")
        
        output = "🖥️ SYSTEM INFORMATION\n"
        output += "=" * 40 + "\n\n"
        
        # Python information
        output += f"🐍 Python Version: {sys.version}\n"
        output += f"📁 Python Executable: {sys.executable}\n"
        output += f"📋 Python Path: {sys.path[0]}\n\n"
        
        # Platform information
        output += f"💻 Platform: {platform.platform()}\n"
        output += f"🏗️ Architecture: {platform.architecture()[0]}\n"
        output += f"🖥️ Machine: {platform.machine()}\n"
        output += f"🔧 Processor: {platform.processor()}\n\n"
        
        # Check for common tools
        tools_to_check = ['git', 'node', 'npm', 'pip', 'docker']
        output += "🛠️ AVAILABLE TOOLS:\n"
        
        for tool in tools_to_check:
            try:
                result = subprocess.run([tool, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    output += f"✅ {tool}: {version}\n"
                else:
                    output += f"❌ {tool}: Not available\n"
            except:
                output += f"❌ {tool}: Not found\n"
        
        # Environment variables
        output += f"\n🌍 ENVIRONMENT:\n"
        important_vars = ['PATH', 'PYTHONPATH', 'HOME', 'USER']
        for var in important_vars:
            value = os.environ.get(var, 'Not set')
            if var == 'PATH':
                value = value[:100] + '...' if len(value) > 100 else value
            output += f"{var}: {value}\n"
        
        return output
        
    except Exception as e:
        logger.error(f"System info gathering failed: {e}")
        return f"❌ System info gathering failed: {str(e)}"


@tool
def create_project_structure(project_path: str, structure_type: str = "python") -> str:
    """
    Create a standard project directory structure.
    
    Args:
        project_path: Path where to create the project structure
        structure_type: Type of project (python, web, react, etc.)
        
    Returns:
        Project structure creation status
    """
    try:
        logger.info(f"Creating {structure_type} project structure at: {project_path}")
        
        project_dir = Path(project_path)
        project_dir.mkdir(parents=True, exist_ok=True)
        
        if structure_type.lower() == "python":
            # Python project structure
            directories = [
                "src",
                "tests",
                "docs",
                "scripts",
                "data"
            ]
            
            files = {
                "README.md": "# Project\n\nDescription of the project.\n",
                "requirements.txt": "# Python dependencies\n",
                ".gitignore": """__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
.venv/
.env
.DS_Store
*.log
""",
                "setup.py": """from setuptools import setup, find_packages

setup(
    name="project",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
)
"""
            }
        
        elif structure_type.lower() == "web":
            # Web project structure
            directories = [
                "src",
                "public",
                "assets",
                "css",
                "js",
                "tests"
            ]
            
            files = {
                "README.md": "# Web Project\n\nDescription of the web project.\n",
                "package.json": """{
  "name": "web-project",
  "version": "1.0.0",
  "description": "",
  "main": "index.js",
  "scripts": {
    "start": "node server.js"
  }
}""",
                "index.html": """<!DOCTYPE html>
<html>
<head>
    <title>Web Project</title>
</head>
<body>
    <h1>Hello World</h1>
</body>
</html>"""
            }
        
        else:
            # Generic project structure
            directories = ["src", "tests", "docs"]
            files = {"README.md": f"# {structure_type.title()} Project\n"}
        
        # Create directories
        for directory in directories:
            (project_dir / directory).mkdir(exist_ok=True)
        
        # Create files
        for filename, content in files.items():
            with open(project_dir / filename, 'w') as f:
                f.write(content)
        
        output = f"✅ {structure_type.title()} project structure created!\n\n"
        output += f"📁 Project Directory: {project_dir}\n\n"
        output += "📋 Created Directories:\n"
        for directory in directories:
            output += f"   📁 {directory}/\n"
        
        output += "\n📄 Created Files:\n"
        for filename in files.keys():
            output += f"   📄 {filename}\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Project structure creation failed: {e}")
        return f"❌ Project structure creation failed: {str(e)}"


class SystemOperationsPlugin(PluginBase):
    """Plugin providing system operations and environment management tools."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="SystemOperations",
            version="1.0.0",
            description="System operations, virtual environment management, and package installation tools",
            author="Jarvis Team",
            dependencies=[]
        )
    
    def get_tools(self):
        return [
            run_system_command,
            create_virtual_environment,
            install_python_package,
            install_requirements_file,
            check_system_info,
            create_project_structure
        ]
