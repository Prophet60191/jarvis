"""
Custom exception hierarchy for Jarvis Voice Assistant.

This module defines all custom exceptions used throughout the application,
providing clear error categorization and helpful error messages.
"""

from typing import Optional, Any


class JarvisError(Exception):
    """
    Base exception class for all Jarvis-related errors.
    
    All custom exceptions in the Jarvis application should inherit from this class.
    """
    
    def __init__(self, message: str, details: Optional[dict] = None, cause: Optional[Exception] = None):
        """
        Initialize JarvisError.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error details
            cause: Optional underlying exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.cause = cause
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        result = self.message
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            result += f" (Details: {details_str})"
        if self.cause:
            result += f" (Caused by: {self.cause})"
        return result


class ConfigurationError(JarvisError):
    """Raised when there are configuration-related errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, config_value: Optional[Any] = None):
        """
        Initialize ConfigurationError.
        
        Args:
            message: Error message
            config_key: The configuration key that caused the error
            config_value: The invalid configuration value
        """
        details = {}
        if config_key:
            details["config_key"] = config_key
        if config_value is not None:
            details["config_value"] = config_value
        
        super().__init__(message, details)
        self.config_key = config_key
        self.config_value = config_value


class AudioError(JarvisError):
    """Base class for audio-related errors."""
    pass


class MicrophoneError(AudioError):
    """Raised when there are microphone-related errors."""
    
    def __init__(self, message: str, mic_index: Optional[int] = None, mic_name: Optional[str] = None):
        """
        Initialize MicrophoneError.
        
        Args:
            message: Error message
            mic_index: The microphone index that caused the error
            mic_name: The microphone name that caused the error
        """
        details = {}
        if mic_index is not None:
            details["mic_index"] = mic_index
        if mic_name:
            details["mic_name"] = mic_name
        
        super().__init__(message, details)
        self.mic_index = mic_index
        self.mic_name = mic_name


class SpeechRecognitionError(AudioError):
    """Raised when speech recognition fails."""
    
    def __init__(self, message: str, recognition_service: Optional[str] = None):
        """
        Initialize SpeechRecognitionError.
        
        Args:
            message: Error message
            recognition_service: The speech recognition service that failed
        """
        details = {}
        if recognition_service:
            details["recognition_service"] = recognition_service
        
        super().__init__(message, details)
        self.recognition_service = recognition_service


class TextToSpeechError(AudioError):
    """Raised when text-to-speech fails."""
    
    def __init__(self, message: str, text: Optional[str] = None, voice: Optional[str] = None):
        """
        Initialize TextToSpeechError.
        
        Args:
            message: Error message
            text: The text that failed to be spoken
            voice: The voice that was being used
        """
        details = {}
        if text:
            details["text"] = text[:100] + "..." if len(text) > 100 else text
        if voice:
            details["voice"] = voice
        
        super().__init__(message, details)
        self.text = text
        self.voice = voice


class LLMError(JarvisError):
    """Base class for language model related errors."""
    pass


class ModelLoadError(LLMError):
    """Raised when the language model fails to load."""
    
    def __init__(self, message: str, model_name: Optional[str] = None):
        """
        Initialize ModelLoadError.
        
        Args:
            message: Error message
            model_name: The name of the model that failed to load
        """
        details = {}
        if model_name:
            details["model_name"] = model_name
        
        super().__init__(message, details)
        self.model_name = model_name


class ModelInferenceError(LLMError):
    """Raised when model inference fails."""
    
    def __init__(self, message: str, input_text: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize ModelInferenceError.
        
        Args:
            message: Error message
            input_text: The input text that caused the error
            model_name: The name of the model that failed
        """
        details = {}
        if input_text:
            details["input_text"] = input_text[:100] + "..." if len(input_text) > 100 else input_text
        if model_name:
            details["model_name"] = model_name
        
        super().__init__(message, details)
        self.input_text = input_text
        self.model_name = model_name


class ToolError(JarvisError):
    """Base class for tool-related errors."""
    pass


class ToolExecutionError(ToolError):
    """Raised when a tool fails to execute."""
    
    def __init__(self, message: str, tool_name: Optional[str] = None, tool_args: Optional[dict] = None):
        """
        Initialize ToolExecutionError.
        
        Args:
            message: Error message
            tool_name: The name of the tool that failed
            tool_args: The arguments passed to the tool
        """
        details = {}
        if tool_name:
            details["tool_name"] = tool_name
        if tool_args:
            details["tool_args"] = tool_args
        
        super().__init__(message, details)
        self.tool_name = tool_name
        self.tool_args = tool_args


class ToolRegistrationError(ToolError):
    """Raised when tool registration fails."""
    
    def __init__(self, message: str, tool_name: Optional[str] = None):
        """
        Initialize ToolRegistrationError.
        
        Args:
            message: Error message
            tool_name: The name of the tool that failed to register
        """
        details = {}
        if tool_name:
            details["tool_name"] = tool_name
        
        super().__init__(message, details)
        self.tool_name = tool_name


class ConversationError(JarvisError):
    """Base class for conversation flow errors."""
    pass


class WakeWordError(ConversationError):
    """Raised when wake word detection fails."""
    
    def __init__(self, message: str, wake_word: Optional[str] = None):
        """
        Initialize WakeWordError.
        
        Args:
            message: Error message
            wake_word: The wake word that failed to be detected
        """
        details = {}
        if wake_word:
            details["wake_word"] = wake_word
        
        super().__init__(message, details)
        self.wake_word = wake_word


class ConversationTimeoutError(ConversationError):
    """Raised when conversation times out."""
    
    def __init__(self, message: str, timeout_seconds: Optional[int] = None):
        """
        Initialize ConversationTimeoutError.
        
        Args:
            message: Error message
            timeout_seconds: The timeout value that was exceeded
        """
        details = {}
        if timeout_seconds is not None:
            details["timeout_seconds"] = timeout_seconds
        
        super().__init__(message, details)
        self.timeout_seconds = timeout_seconds


class InitializationError(JarvisError):
    """Raised when system initialization fails."""
    
    def __init__(self, message: str, component: Optional[str] = None):
        """
        Initialize InitializationError.
        
        Args:
            message: Error message
            component: The component that failed to initialize
        """
        details = {}
        if component:
            details["component"] = component
        
        super().__init__(message, details)
        self.component = component


# Convenience functions for common error scenarios

def raise_config_error(message: str, key: Optional[str] = None, value: Optional[Any] = None) -> None:
    """Raise a ConfigurationError with the given parameters."""
    raise ConfigurationError(message, key, value)


def raise_audio_error(message: str, error_type: str = "general") -> None:
    """Raise an appropriate audio error based on the error type."""
    if error_type == "microphone":
        raise MicrophoneError(message)
    elif error_type == "speech_recognition":
        raise SpeechRecognitionError(message)
    elif error_type == "tts":
        raise TextToSpeechError(message)
    else:
        raise AudioError(message)


def raise_llm_error(message: str, error_type: str = "general", model_name: Optional[str] = None) -> None:
    """Raise an appropriate LLM error based on the error type."""
    if error_type == "load":
        raise ModelLoadError(message, model_name)
    elif error_type == "inference":
        raise ModelInferenceError(message, model_name=model_name)
    else:
        raise LLMError(message)


def raise_tool_error(message: str, tool_name: Optional[str] = None, tool_args: Optional[dict] = None) -> None:
    """Raise a ToolExecutionError with the given parameters."""
    raise ToolExecutionError(message, tool_name, tool_args)
