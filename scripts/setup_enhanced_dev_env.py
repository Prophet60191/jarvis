#!/usr/bin/env python3
"""
Enhanced Development Environment Setup Script

This script sets up the development environment for the System Integration & 
Source Code Consciousness features, including all necessary dependencies,
development tools, and infrastructure components.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedDevEnvironmentSetup:
    """Setup class for enhanced development environment."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.system_platform = platform.system().lower()
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        
        # Required Python version
        self.min_python_version = (3, 9)
        
        # Development directories to create
        self.dev_directories = [
            "tests/enhanced",
            "tests/benchmarks",
            "tests/integration",
            "docs/api",
            "docs/development",
            "scripts/monitoring",
            "scripts/deployment",
            "data/test_data",
            "data/benchmarks",
            "logs/development",
            "config/development",
            "jarvis/core/orchestration",
            "jarvis/core/context",
            "jarvis/core/consciousness",
            "jarvis/plugins/registry",
            "jarvis/tools/enhanced"
        ]
        
        # Development tools to install
        self.dev_tools = {
            "pre-commit": ">=3.3.0",
            "black": ">=23.7.0",
            "isort": ">=5.12.0",
            "flake8": ">=6.0.0",
            "mypy": ">=1.5.0",
            "pytest": ">=7.4.0",
            "pytest-cov": ">=4.1.0",
            "pytest-benchmark": ">=4.0.0"
        }
        
    def check_python_version(self) -> bool:
        """Check if Python version meets requirements."""
        current_version = (sys.version_info.major, sys.version_info.minor)
        if current_version < self.min_python_version:
            logger.error(f"Python {self.min_python_version[0]}.{self.min_python_version[1]}+ required, "
                        f"but {current_version[0]}.{current_version[1]} found")
            return False
        
        logger.info(f"✅ Python version {current_version[0]}.{current_version[1]} meets requirements")
        return True
    
    def check_system_dependencies(self) -> bool:
        """Check for required system dependencies."""
        required_tools = []
        
        # Platform-specific requirements
        if self.system_platform == "darwin":  # macOS
            required_tools.extend(["brew", "git"])
        elif self.system_platform == "linux":
            required_tools.extend(["apt-get", "git"])  # Assuming Ubuntu/Debian
        elif self.system_platform == "windows":
            required_tools.extend(["git"])
        
        # Common requirements
        required_tools.extend(["pip", "node", "npm"])
        
        missing_tools = []
        for tool in required_tools:
            if not shutil.which(tool):
                missing_tools.append(tool)
        
        if missing_tools:
            logger.error(f"❌ Missing required tools: {', '.join(missing_tools)}")
            return False
        
        logger.info("✅ All required system dependencies found")
        return True
    
    def create_development_directories(self) -> None:
        """Create necessary development directories."""
        logger.info("📁 Creating development directories...")
        
        for directory in self.dev_directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"   Created: {directory}")
        
        # Create __init__.py files for Python packages
        python_packages = [
            "jarvis/core/orchestration",
            "jarvis/core/context", 
            "jarvis/core/consciousness",
            "jarvis/plugins/registry",
            "jarvis/tools/enhanced",
            "tests/enhanced",
            "tests/benchmarks",
            "tests/integration"
        ]
        
        for package in python_packages:
            init_file = self.project_root / package / "__init__.py"
            if not init_file.exists():
                init_file.touch()
                logger.info(f"   Created: {package}/__init__.py")
    
    def install_enhanced_dependencies(self) -> bool:
        """Install enhanced dependencies from requirements-enhanced.txt."""
        logger.info("📦 Installing enhanced dependencies...")
        
        requirements_file = self.project_root / "requirements-enhanced.txt"
        if not requirements_file.exists():
            logger.error("❌ requirements-enhanced.txt not found")
            return False
        
        try:
            # Install in development mode with enhanced requirements
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True, capture_output=True, text=True)
            
            logger.info("✅ Enhanced dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install enhanced dependencies: {e.stderr}")
            return False
    
    def setup_development_tools(self) -> bool:
        """Set up development tools and configurations."""
        logger.info("🔧 Setting up development tools...")
        
        # Install pre-commit hooks
        try:
            subprocess.run([sys.executable, "-m", "pre_commit", "install"], 
                         check=True, capture_output=True, text=True)
            logger.info("✅ Pre-commit hooks installed")
        except subprocess.CalledProcessError:
            logger.warning("⚠️  Pre-commit hooks installation failed (optional)")
        
        # Create development configuration files
        self._create_dev_config_files()
        
        return True
    
    def _create_dev_config_files(self) -> None:
        """Create development configuration files."""
        
        # Create .pre-commit-config.yaml
        precommit_config = self.project_root / ".pre-commit-config.yaml"
        if not precommit_config.exists():
            precommit_content = """repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]
"""
            precommit_config.write_text(precommit_content)
            logger.info("   Created: .pre-commit-config.yaml")
        
        # Create pytest.ini
        pytest_config = self.project_root / "pytest.ini"
        if not pytest_config.exists():
            pytest_content = """[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --cov=jarvis
    --cov-report=html
    --cov-report=term-missing
    --benchmark-only
    --benchmark-sort=mean
markers =
    unit: Unit tests
    integration: Integration tests
    benchmark: Performance benchmark tests
    slow: Slow running tests
    enhanced: Tests for enhanced features
"""
            pytest_config.write_text(pytest_content)
            logger.info("   Created: pytest.ini")
        
        # Create mypy.ini
        mypy_config = self.project_root / "mypy.ini"
        if not mypy_config.exists():
            mypy_content = """[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True

[mypy-tests.*]
disallow_untyped_defs = False

[mypy-jarvis.plugins.*]
disallow_untyped_defs = False
"""
            mypy_config.write_text(mypy_content)
            logger.info("   Created: mypy.ini")
    
    def setup_database_for_development(self) -> bool:
        """Set up development database and test data."""
        logger.info("🗄️  Setting up development database...")
        
        # Create development data directories
        dev_data_dirs = [
            "data/development/chroma_db",
            "data/development/backups",
            "data/development/logs",
            "data/test_data/sample_documents",
            "data/test_data/sample_code",
            "data/benchmarks/datasets"
        ]
        
        for data_dir in dev_data_dirs:
            dir_path = self.project_root / data_dir
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"   Created: {data_dir}")
        
        # Create sample test data
        self._create_sample_test_data()
        
        return True
    
    def _create_sample_test_data(self) -> None:
        """Create sample test data for development."""
        
        # Sample document for RAG testing
        sample_doc = self.project_root / "data/test_data/sample_documents/test_document.txt"
        if not sample_doc.exists():
            sample_content = """# Sample Document for Testing

This is a sample document used for testing the enhanced RAG system.
It contains various types of information that can be used to test
document processing, chunking, and retrieval capabilities.

## Technical Information
- System: Jarvis Voice Assistant
- Features: Enhanced plugin registry, context management, orchestration
- Technologies: Python, LangChain, ChromaDB, Ollama

## Test Scenarios
1. Simple fact retrieval
2. Complex multi-step queries
3. Context-aware responses
4. Code consciousness queries

This document should be processed by the intelligent RAG system
and made available for semantic search and retrieval.
"""
            sample_doc.write_text(sample_content)
            logger.info("   Created: sample test document")
        
        # Sample Python code for code consciousness testing
        sample_code = self.project_root / "data/test_data/sample_code/sample_plugin.py"
        if not sample_code.exists():
            sample_code_content = '''"""
Sample plugin for testing code consciousness features.
"""

from langchain_core.tools import tool
from jarvis.plugins.base import PluginBase, PluginMetadata

class SamplePlugin(PluginBase):
    """Sample plugin for testing enhanced registry features."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="sample_plugin",
            version="1.0.0",
            description="Sample plugin for testing",
            author="Development Team"
        )
    
    def get_tools(self):
        return [sample_tool]

@tool
def sample_tool(query: str) -> str:
    """Sample tool for testing orchestration."""
    return f"Processed: {query}"
'''
            sample_code.write_text(sample_code_content)
            logger.info("   Created: sample code file")
    
    def verify_installation(self) -> bool:
        """Verify that the enhanced development environment is properly set up."""
        logger.info("🔍 Verifying installation...")
        
        verification_checks = [
            ("Python imports", self._verify_python_imports),
            ("Development tools", self._verify_dev_tools),
            ("Directory structure", self._verify_directories),
            ("Configuration files", self._verify_config_files)
        ]
        
        all_passed = True
        for check_name, check_func in verification_checks:
            try:
                if check_func():
                    logger.info(f"   ✅ {check_name}")
                else:
                    logger.error(f"   ❌ {check_name}")
                    all_passed = False
            except Exception as e:
                logger.error(f"   ❌ {check_name}: {e}")
                all_passed = False
        
        return all_passed
    
    def _verify_python_imports(self) -> bool:
        """Verify that key Python packages can be imported."""
        test_imports = [
            "networkx",
            "sklearn",
            "pytest",
            "black",
            "mypy"
        ]
        
        for package in test_imports:
            try:
                __import__(package)
            except ImportError:
                logger.error(f"Cannot import {package}")
                return False
        
        return True
    
    def _verify_dev_tools(self) -> bool:
        """Verify that development tools are available."""
        tools = ["black", "isort", "flake8", "mypy", "pytest"]
        
        for tool in tools:
            try:
                subprocess.run([sys.executable, "-m", tool, "--version"], 
                             check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError:
                logger.error(f"Tool {tool} not available")
                return False
        
        return True
    
    def _verify_directories(self) -> bool:
        """Verify that all required directories exist."""
        for directory in self.dev_directories:
            if not (self.project_root / directory).exists():
                logger.error(f"Directory {directory} not found")
                return False
        
        return True
    
    def _verify_config_files(self) -> bool:
        """Verify that configuration files exist."""
        config_files = [".pre-commit-config.yaml", "pytest.ini", "mypy.ini"]
        
        for config_file in config_files:
            if not (self.project_root / config_file).exists():
                logger.error(f"Configuration file {config_file} not found")
                return False
        
        return True
    
    def run_setup(self) -> bool:
        """Run the complete setup process."""
        logger.info("🚀 Starting enhanced development environment setup...")
        
        setup_steps = [
            ("Checking Python version", self.check_python_version),
            ("Checking system dependencies", self.check_system_dependencies),
            ("Creating development directories", lambda: (self.create_development_directories(), True)[1]),
            ("Installing enhanced dependencies", self.install_enhanced_dependencies),
            ("Setting up development tools", self.setup_development_tools),
            ("Setting up development database", self.setup_database_for_development),
            ("Verifying installation", self.verify_installation)
        ]
        
        for step_name, step_func in setup_steps:
            logger.info(f"📋 {step_name}...")
            try:
                if not step_func():
                    logger.error(f"❌ Failed: {step_name}")
                    return False
            except Exception as e:
                logger.error(f"❌ Error in {step_name}: {e}")
                return False
        
        logger.info("🎉 Enhanced development environment setup completed successfully!")
        logger.info("\n📝 Next steps:")
        logger.info("   1. Run 'pytest tests/' to verify tests work")
        logger.info("   2. Run 'python -m jarvis.main' to test the application")
        logger.info("   3. Check 'docs/DEVELOPMENT.md' for development guidelines")
        
        return True

def main():
    """Main entry point for the setup script."""
    setup = EnhancedDevEnvironmentSetup()
    
    if not setup.run_setup():
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
