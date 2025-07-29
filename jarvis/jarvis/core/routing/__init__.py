"""
Fast/Slow Path Routing System

Industry-standard routing implementation for optimizing AI assistant performance.
Based on patterns used by Alexa, Google Assistant, and other high-performance systems.
"""

from .intent_router import IntentRouter, ExecutionPath, RouteResult
from .execution_engine import ExecutionEngine, ExecutionResult
from .smart_conversation_manager import SmartConversationManager

__all__ = [
    'IntentRouter',
    'ExecutionPath', 
    'RouteResult',
    'ExecutionEngine',
    'ExecutionResult',
    'SmartConversationManager'
]

# Version info
__version__ = "1.0.0"
__description__ = "Fast/Slow Path Routing System for Jarvis"
