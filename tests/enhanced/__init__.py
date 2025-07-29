"""
Enhanced Testing Framework for System Integration & Code Consciousness

This package provides comprehensive testing utilities and base classes
for testing the enhanced Jarvis features including:
- Enhanced Plugin Registry
- Context Management System
- Smart Tool Orchestration
- Source Code Consciousness

Test Categories:
- Unit tests: Individual component testing
- Integration tests: Component interaction testing
- Benchmark tests: Performance and scalability testing
- End-to-end tests: Complete workflow testing
"""

import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Test configuration
TEST_CONFIG = {
    "timeout": 30,
    "verbose": True,
    "coverage": True
}

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Generator
from unittest.mock import Mock, MagicMock, patch
import logging

# Configure test logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Test configuration
TEST_CONFIG = {
    "temp_dir": None,
    "mock_data_dir": None,
    "test_plugins": [],
    "benchmark_iterations": 100,
    "performance_thresholds": {
        "registry_query": 0.05,  # 50ms
        "context_retrieval": 0.02,  # 20ms
        "orchestration_decision": 0.15,  # 150ms
        "code_query": 0.5  # 500ms
    }
}

class EnhancedTestBase:
    """Base class for enhanced feature tests."""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Set up test environment for each test."""
        # Create temporary directory for test data
        self.temp_dir = Path(tempfile.mkdtemp(prefix="jarvis_test_"))
        TEST_CONFIG["temp_dir"] = self.temp_dir
        
        # Create test data directories
        self.test_data_dir = self.temp_dir / "test_data"
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create mock configuration
        self.mock_config = self._create_mock_config()
        
        yield
        
        # Cleanup
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_mock_config(self) -> Mock:
        """Create mock configuration for testing."""
        config = Mock()
        config.rag.enabled = True
        config.rag.vector_store_path = str(self.temp_dir / "chroma_db")
        config.rag.chunk_size = 1000
        config.rag.chunk_overlap = 150
        config.rag.search_k = 5
        config.llm.model = "test_model"
        return config
    
    def create_mock_plugin(self, name: str, capabilities: List[str] = None) -> Mock:
        """Create a mock plugin for testing."""
        plugin = Mock()
        plugin.name = name
        plugin.get_metadata.return_value = Mock(
            name=name,
            version="1.0.0",
            description=f"Test plugin {name}",
            capabilities=capabilities or ["test_capability"]
        )
        plugin.get_tools.return_value = [Mock(name=f"{name}_tool")]
        return plugin
    
    def create_test_context(self, **kwargs) -> Dict[str, Any]:
        """Create test context data."""
        default_context = {
            "conversation_context": {
                "current_topic": "test_topic",
                "intent_history": ["test_intent"],
                "active_tools": set()
            },
            "user_context": {
                "user_id": "test_user",
                "preferences": {"test_pref": "value"}
            },
            "system_context": {
                "timestamp": "2025-01-01T00:00:00Z",
                "system_load": 0.5
            }
        }
        default_context.update(kwargs)
        return default_context

# Export test utilities
__all__ = [
    "EnhancedTestBase",
    "TEST_CONFIG",
    "logger"
]
