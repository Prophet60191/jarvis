"""
Base tool classes for Jarvis Voice Assistant.

This module defines the base interfaces and classes for all tools,
providing a consistent API and proper error handling.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
from enum import Enum
from langchain_core.tools import tool as langchain_tool


logger = logging.getLogger(__name__)


class ToolStatus(Enum):
    """Enumeration of tool execution statuses."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PARTIAL = "partial"


@dataclass
class ToolResult:
    """
    Result of a tool execution.
    
    This class encapsulates the result of tool execution with status,
    data, and error information.
    """
    status: ToolStatus
    data: Any = None
    message: str = ""
    error: Optional[Exception] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def is_success(self) -> bool:
        """Check if the tool execution was successful."""
        return self.status == ToolStatus.SUCCESS
    
    @property
    def is_error(self) -> bool:
        """Check if the tool execution resulted in an error."""
        return self.status == ToolStatus.ERROR
    
    def to_string(self) -> str:
        """
        Convert result to string representation.
        
        Returns:
            String representation of the result
        """
        if self.is_success and self.data is not None:
            return str(self.data)
        elif self.message:
            return self.message
        elif self.is_error and self.error:
            return f"Error: {str(self.error)}"
        else:
            return f"Tool execution {self.status.value}"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary representation.
        
        Returns:
            Dictionary representation of the result
        """
        return {
            "status": self.status.value,
            "data": self.data,
            "message": self.message,
            "error": str(self.error) if self.error else None,
            "metadata": self.metadata
        }


class BaseTool(ABC):
    """
    Abstract base class for all Jarvis tools.
    
    This class defines the interface that all tools must implement,
    providing consistent behavior and error handling.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize the base tool.
        
        Args:
            name: Tool name (should be unique)
            description: Tool description for the LLM
        """
        self.name = name
        self.description = description
        self.enabled = True
        self.metadata: Dict[str, Any] = {}
        
        logger.debug(f"Initialized tool: {name}")
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with given parameters.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            ToolResult containing execution results
            
        Raises:
            ToolExecutionError: If tool execution fails
        """
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get tool parameter schema.
        
        Returns:
            Dictionary describing tool parameters
        """
        pass
    
    def validate_parameters(self, **kwargs: Any) -> bool:
        """
        Validate tool parameters before execution.
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            True if parameters are valid, False otherwise
        """
        # Default implementation - can be overridden by subclasses
        return True
    
    def is_enabled(self) -> bool:
        """
        Check if the tool is enabled.
        
        Returns:
            True if tool is enabled, False otherwise
        """
        return self.enabled
    
    def enable(self) -> None:
        """Enable the tool."""
        self.enabled = True
        logger.debug(f"Tool enabled: {self.name}")
    
    def disable(self) -> None:
        """Disable the tool."""
        self.enabled = False
        logger.debug(f"Tool disabled: {self.name}")
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get tool information.
        
        Returns:
            Dictionary containing tool information
        """
        return {
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "parameters": self.get_parameters(),
            "metadata": self.metadata
        }
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set tool metadata.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get tool metadata.
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)
    
    def __str__(self) -> str:
        """String representation of the tool."""
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        """Detailed string representation of the tool."""
        return f"BaseTool(name='{self.name}', description='{self.description}', enabled={self.enabled})"


def create_langchain_tool(jarvis_tool: BaseTool):
    """
    Create a LangChain tool from a Jarvis tool using the @tool decorator.

    Args:
        jarvis_tool: Jarvis tool to convert

    Returns:
        LangChain tool function
    """
    # Create the tool function with proper signature
    def tool_function(**kwargs) -> str:
        """Execute the Jarvis tool and return result as string."""
        try:
            result = jarvis_tool.execute(**kwargs)
            if result.is_success:
                return str(result.data)
            else:
                return f"Error: {result.error_message}"
        except Exception as e:
            return f"Error executing tool: {str(e)}"

    # Set the function name and docstring for LangChain
    tool_function.__name__ = jarvis_tool.name
    tool_function.__doc__ = jarvis_tool.description

    # Create LangChain tool using the @tool decorator
    return langchain_tool(tool_function)


def create_success_result(data: Any, message: str = "", metadata: Dict[str, Any] = None) -> ToolResult:
    """
    Create a successful tool result.
    
    Args:
        data: Result data
        message: Optional success message
        metadata: Optional metadata
        
    Returns:
        ToolResult with success status
    """
    return ToolResult(
        status=ToolStatus.SUCCESS,
        data=data,
        message=message,
        metadata=metadata or {}
    )


def create_error_result(error: Exception, message: str = "", metadata: Dict[str, Any] = None) -> ToolResult:
    """
    Create an error tool result.
    
    Args:
        error: Exception that occurred
        message: Optional error message
        metadata: Optional metadata
        
    Returns:
        ToolResult with error status
    """
    return ToolResult(
        status=ToolStatus.ERROR,
        error=error,
        message=message or str(error),
        metadata=metadata or {}
    )


def create_warning_result(data: Any, message: str, metadata: Dict[str, Any] = None) -> ToolResult:
    """
    Create a warning tool result.
    
    Args:
        data: Result data
        message: Warning message
        metadata: Optional metadata
        
    Returns:
        ToolResult with warning status
    """
    return ToolResult(
        status=ToolStatus.WARNING,
        data=data,
        message=message,
        metadata=metadata or {}
    )
