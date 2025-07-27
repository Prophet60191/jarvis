"""
Unit tests for Jarvis tools system.

This module tests the tools architecture including base classes,
registry, and individual tool implementations.
"""

import pytest
from unittest.mock import Mock, patch
import datetime

from jarvis.tools.base import BaseTool, ToolResult, ToolStatus, LangChainToolAdapter
from jarvis.tools.registry import ToolRegistry
from jarvis.tools.video_tool import VideoTool
from jarvis.exceptions import ToolRegistrationError, ToolExecutionError


class TestToolResult:
    """Test ToolResult class."""
    
    def test_success_result(self):
        """Test successful tool result."""
        result = ToolResult(
            status=ToolStatus.SUCCESS,
            data="test data",
            message="Success message"
        )
        
        assert result.is_success
        assert not result.is_error
        assert result.to_string() == "test data"
        
        result_dict = result.to_dict()
        assert result_dict["status"] == "success"
        assert result_dict["data"] == "test data"
        assert result_dict["message"] == "Success message"
    
    def test_error_result(self):
        """Test error tool result."""
        error = Exception("Test error")
        result = ToolResult(
            status=ToolStatus.ERROR,
            error=error,
            message="Error occurred"
        )
        
        assert not result.is_success
        assert result.is_error
        assert "Error: Test error" in result.to_string()
        
        result_dict = result.to_dict()
        assert result_dict["status"] == "error"
        assert result_dict["error"] == "Test error"
    
    def test_result_with_metadata(self):
        """Test tool result with metadata."""
        metadata = {"key": "value", "count": 42}
        result = ToolResult(
            status=ToolStatus.SUCCESS,
            data="test",
            metadata=metadata
        )
        
        assert result.metadata == metadata
        assert result.to_dict()["metadata"] == metadata


class MockTool(BaseTool):
    """Mock tool for testing."""
    
    def __init__(self, name="mock_tool", description="Mock tool for testing"):
        super().__init__(name, description)
        self.execute_called = False
        self.execute_args = None
        self.execute_kwargs = None
    
    def execute(self, **kwargs):
        """Mock execute method."""
        self.execute_called = True
        self.execute_args = ()
        self.execute_kwargs = kwargs
        
        if kwargs.get("should_fail"):
            raise ToolExecutionError("Mock tool failure")
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            data=f"Mock result: {kwargs}",
            message="Mock execution successful"
        )
    
    def get_parameters(self):
        """Mock parameter schema."""
        return {
            "test_param": {
                "type": "string",
                "description": "Test parameter",
                "required": False
            }
        }


class TestBaseTool:
    """Test BaseTool abstract class."""
    
    def test_tool_initialization(self):
        """Test tool initialization."""
        tool = MockTool("test_tool", "Test description")
        
        assert tool.name == "test_tool"
        assert tool.description == "Test description"
        assert tool.enabled is True
        assert tool.metadata == {}
    
    def test_tool_enable_disable(self):
        """Test tool enable/disable functionality."""
        tool = MockTool()
        
        assert tool.is_enabled()
        
        tool.disable()
        assert not tool.is_enabled()
        
        tool.enable()
        assert tool.is_enabled()
    
    def test_tool_metadata(self):
        """Test tool metadata management."""
        tool = MockTool()
        
        tool.set_metadata("key1", "value1")
        tool.set_metadata("key2", 42)
        
        assert tool.get_metadata("key1") == "value1"
        assert tool.get_metadata("key2") == 42
        assert tool.get_metadata("nonexistent", "default") == "default"
    
    def test_tool_info(self):
        """Test tool information retrieval."""
        tool = MockTool("test_tool", "Test description")
        tool.set_metadata("version", "1.0")
        
        info = tool.get_info()
        
        assert info["name"] == "test_tool"
        assert info["description"] == "Test description"
        assert info["enabled"] is True
        assert "parameters" in info
        assert info["metadata"]["version"] == "1.0"
    
    def test_tool_execution(self):
        """Test tool execution."""
        tool = MockTool()
        
        result = tool.execute(test_param="test_value")
        
        assert tool.execute_called
        assert tool.execute_kwargs["test_param"] == "test_value"
        assert result.is_success
        assert "test_value" in result.data
    
    def test_tool_execution_failure(self):
        """Test tool execution failure."""
        tool = MockTool()
        
        result = tool.execute(should_fail=True)
        
        assert result.is_error
        assert isinstance(result.error, ToolExecutionError)


class TestLangChainToolAdapter:
    """Test LangChain tool adapter."""
    
    def test_adapter_initialization(self):
        """Test adapter initialization."""
        tool = MockTool("test_tool", "Test description")
        adapter = LangChainToolAdapter(tool)
        
        assert adapter.name == "test_tool"
        assert adapter.description == "Test description"
        assert adapter.jarvis_tool is tool
    
    def test_adapter_run_success(self):
        """Test successful adapter execution."""
        tool = MockTool()
        adapter = LangChainToolAdapter(tool)
        
        result = adapter._run(test_param="test_value")
        
        assert tool.execute_called
        assert "test_value" in result
    
    def test_adapter_run_disabled_tool(self):
        """Test adapter with disabled tool."""
        tool = MockTool()
        tool.disable()
        adapter = LangChainToolAdapter(tool)
        
        with pytest.raises(ToolExecutionError, match="disabled"):
            adapter._run()
    
    def test_adapter_run_failure(self):
        """Test adapter execution failure."""
        tool = MockTool()
        adapter = LangChainToolAdapter(tool)
        
        with pytest.raises(ToolExecutionError):
            adapter._run(should_fail=True)


class TestToolRegistry:
    """Test ToolRegistry class."""
    
    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = ToolRegistry()
        
        assert len(registry) == 0
        assert registry.list_tools() == []
    
    def test_register_tool(self):
        """Test tool registration."""
        registry = ToolRegistry()
        tool = MockTool("test_tool")
        
        registry.register(tool)
        
        assert len(registry) == 1
        assert "test_tool" in registry
        assert registry.has_tool("test_tool")
        assert registry.get_tool("test_tool") is tool
    
    def test_register_duplicate_tool(self):
        """Test registering duplicate tool."""
        registry = ToolRegistry()
        tool1 = MockTool("test_tool")
        tool2 = MockTool("test_tool")
        
        registry.register(tool1)
        registry.register(tool2)  # Should replace tool1
        
        assert len(registry) == 1
        assert registry.get_tool("test_tool") is tool2
    
    def test_register_invalid_tool(self):
        """Test registering invalid tool."""
        registry = ToolRegistry()
        
        with pytest.raises(ToolRegistrationError):
            registry.register("not a tool")
    
    def test_unregister_tool(self):
        """Test tool unregistration."""
        registry = ToolRegistry()
        tool = MockTool("test_tool")
        
        registry.register(tool)
        assert registry.has_tool("test_tool")
        
        result = registry.unregister("test_tool")
        assert result is True
        assert not registry.has_tool("test_tool")
        
        # Unregistering non-existent tool
        result = registry.unregister("nonexistent")
        assert result is False
    
    def test_get_all_tools(self):
        """Test getting all tools."""
        registry = ToolRegistry()
        tool1 = MockTool("tool1")
        tool2 = MockTool("tool2")
        tool3 = MockTool("tool3")
        tool3.disable()
        
        registry.register(tool1)
        registry.register(tool2)
        registry.register(tool3)
        
        all_tools = registry.get_all_tools()
        assert len(all_tools) == 3
        
        enabled_tools = registry.get_all_tools(enabled_only=True)
        assert len(enabled_tools) == 2
        assert tool3 not in enabled_tools
    
    def test_get_langchain_tools(self):
        """Test getting LangChain-compatible tools."""
        registry = ToolRegistry()
        tool1 = MockTool("tool1")
        tool2 = MockTool("tool2")
        tool2.disable()
        
        registry.register(tool1)
        registry.register(tool2)
        
        langchain_tools = registry.get_langchain_tools()
        assert len(langchain_tools) == 1  # Only enabled tools
        assert isinstance(langchain_tools[0], LangChainToolAdapter)
        
        all_langchain_tools = registry.get_langchain_tools(enabled_only=False)
        assert len(all_langchain_tools) == 2
    
    def test_execute_tool(self):
        """Test tool execution through registry."""
        registry = ToolRegistry()
        tool = MockTool("test_tool")
        registry.register(tool)
        
        result = registry.execute_tool("test_tool", test_param="test_value")
        
        assert tool.execute_called
        assert result.is_success
    
    def test_execute_nonexistent_tool(self):
        """Test executing non-existent tool."""
        registry = ToolRegistry()
        
        with pytest.raises(Exception):  # ToolError
            registry.execute_tool("nonexistent")
    
    def test_registry_info(self):
        """Test registry information."""
        registry = ToolRegistry()
        tool1 = MockTool("tool1")
        tool2 = MockTool("tool2")
        tool2.disable()
        
        registry.register(tool1)
        registry.register(tool2)
        
        info = registry.get_registry_info()
        
        assert info["total_tools"] == 2
        assert info["instantiated_tools"] == 2
        assert info["enabled_tools"] == 1
        assert "tool1" in info["tool_names"]
        assert "tool2" in info["tool_names"]
        assert "tool1" in info["enabled_tool_names"]
        assert "tool2" not in info["enabled_tool_names"]


# TimeTool tests removed - now using MCP plugin system (device_time_tool.py)
        assert len(cities) > 0
        assert "New York" in cities
        assert "London" in cities
        assert "Tokyo" in cities


class TestVideoTool:
    """Test VideoTool implementation."""
    
    def test_video_tool_initialization(self):
        """Test video tool initialization."""
        tool = VideoTool()
        
        assert tool.name == "video_day"
        assert "video content" in tool.description.lower()
        assert tool.is_enabled()
    
    def test_get_parameters(self):
        """Test video tool parameters."""
        tool = VideoTool()
        params = tool.get_parameters()
        
        assert "topic" in params
        assert "platform" in params
        assert params["topic"]["required"] is False
        assert params["platform"]["required"] is False
    
    def test_execute_general_advice(self):
        """Test getting general video advice."""
        tool = VideoTool()
        
        with patch('jarvis.tools.video_tool.datetime') as mock_datetime:
            mock_now = Mock()
            mock_now.strftime.return_value = "Monday"
            mock_datetime.datetime.now.return_value = mock_now
            
            result = tool.execute()
            
            assert result.is_success
            assert "Monday" in result.data
            assert "Pro tip:" in result.data
            assert "Trending topic" in result.data
    
    def test_execute_with_topic(self):
        """Test getting topic-specific advice."""
        tool = VideoTool()
        
        result = tool.execute(topic="productivity")
        
        assert result.is_success
        assert isinstance(result.data, str)
    
    def test_execute_with_platform(self):
        """Test getting platform-specific advice."""
        tool = VideoTool()
        
        result = tool.execute(platform="YouTube")
        
        assert result.is_success
        assert "YouTube" in result.data or "tip:" in result.data
    
    def test_get_trending_topics(self):
        """Test getting trending topics."""
        tool = VideoTool()
        
        topics = tool.get_trending_topics()
        
        assert isinstance(topics, list)
        assert len(topics) > 0
        assert "AI and Technology" in topics
    
    def test_get_platform_tips(self):
        """Test getting platform tips."""
        tool = VideoTool()
        
        youtube_tips = tool.get_platform_tips("YouTube")
        assert isinstance(youtube_tips, list)
        assert len(youtube_tips) > 0
        
        invalid_tips = tool.get_platform_tips("InvalidPlatform")
        assert invalid_tips == []
