"""
Pytest configuration and fixtures for Jarvis Voice Assistant tests.

This module provides common fixtures and configuration for all tests,
including mocks, test data, and setup/teardown functionality.
"""

import pytest
import logging
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import tempfile
import shutil

# Import Jarvis components
from jarvis.config import JarvisConfig, AudioConfig, ConversationConfig, LLMConfig, LoggingConfig, GeneralConfig
from jarvis.audio import MicrophoneManager, TextToSpeechManager, AudioProcessor
from jarvis.core import JarvisAgent, SpeechManager, ConversationManager, WakeWordDetector
from jarvis.tools import TimeTool, VideoTool, ToolRegistry
from jarvis.exceptions import JarvisError


# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def audio_config():
    """Create test audio configuration."""
    return AudioConfig(
        mic_index=0,
        mic_name="Test Microphone",
        energy_threshold=100,
        timeout=1.0,
        phrase_time_limit=2.0,
        tts_rate=180,
        tts_volume=0.8,
        tts_voice_preference="test"
    )


@pytest.fixture
def conversation_config():
    """Create test conversation configuration."""
    return ConversationConfig(
        wake_word="test",
        conversation_timeout=10,
        max_retries=2,
        response_delay=0.1
    )


@pytest.fixture
def llm_config():
    """Create test LLM configuration."""
    return LLMConfig(
        model="test-model",
        verbose=False,
        reasoning=False,
        temperature=0.7,
        max_tokens=100
    )


@pytest.fixture
def logging_config():
    """Create test logging configuration."""
    return LoggingConfig(
        level="DEBUG",
        file=None,
        format="%(levelname)s - %(message)s",
        date_format="%Y-%m-%d %H:%M:%S"
    )


@pytest.fixture
def general_config(temp_dir):
    """Create test general configuration."""
    return GeneralConfig(
        debug=True,
        data_dir=temp_dir / "data",
        config_file=None
    )


@pytest.fixture
def jarvis_config(audio_config, conversation_config, llm_config, logging_config, general_config):
    """Create complete test Jarvis configuration."""
    return JarvisConfig(
        audio=audio_config,
        conversation=conversation_config,
        llm=llm_config,
        logging=logging_config,
        general=general_config
    )


@pytest.fixture
def mock_microphone():
    """Create mock microphone for testing."""
    mock_mic = Mock()
    mock_mic.__enter__ = Mock(return_value=mock_mic)
    mock_mic.__exit__ = Mock(return_value=None)
    return mock_mic


@pytest.fixture
def mock_recognizer():
    """Create mock speech recognizer for testing."""
    mock_recognizer = Mock()
    mock_recognizer.energy_threshold = 100
    mock_recognizer.dynamic_energy_threshold = True
    mock_recognizer.pause_threshold = 0.8
    mock_recognizer.operation_timeout = None
    return mock_recognizer


@pytest.fixture
def mock_audio_data():
    """Create mock audio data for testing."""
    mock_audio = Mock()
    mock_audio.get_raw_data.return_value = b'\x00' * 1000  # Mock audio bytes
    mock_audio.sample_rate = 16000
    mock_audio.sample_width = 2
    return mock_audio


@pytest.fixture
def mock_tts_engine():
    """Create mock TTS engine for testing."""
    mock_engine = Mock()
    mock_engine.getProperty.return_value = []  # Mock voices
    mock_engine.setProperty = Mock()
    mock_engine.say = Mock()
    mock_engine.runAndWait = Mock()
    mock_engine.stop = Mock()
    return mock_engine


@pytest.fixture
def mock_llm():
    """Create mock LLM for testing."""
    mock_llm = Mock()
    mock_llm.invoke.return_value = Mock(content="Test response")
    return mock_llm


@pytest.fixture
def mock_agent_executor():
    """Create mock agent executor for testing."""
    mock_executor = Mock()
    mock_executor.invoke.return_value = {"output": "Test agent response"}
    return mock_executor


@pytest.fixture
def sample_tools():
    """Create sample tools for testing."""
    return [TimeTool(), VideoTool()]


@pytest.fixture
def tool_registry_with_tools(sample_tools):
    """Create tool registry with sample tools."""
    registry = ToolRegistry()
    for tool in sample_tools:
        registry.register(tool)
    return registry


@pytest.fixture
def microphone_manager(audio_config):
    """Create microphone manager for testing."""
    return MicrophoneManager(audio_config)


@pytest.fixture
def tts_manager(audio_config):
    """Create TTS manager for testing."""
    return TextToSpeechManager(audio_config)


@pytest.fixture
def audio_processor():
    """Create audio processor for testing."""
    return AudioProcessor()


@pytest.fixture
def jarvis_agent(llm_config):
    """Create Jarvis agent for testing."""
    return JarvisAgent(llm_config)


@pytest.fixture
def speech_manager(audio_config):
    """Create speech manager for testing."""
    return SpeechManager(audio_config)


@pytest.fixture
def conversation_manager(conversation_config, speech_manager, jarvis_agent):
    """Create conversation manager for testing."""
    return ConversationManager(conversation_config, speech_manager, jarvis_agent)


@pytest.fixture
def wake_word_detector(conversation_config, speech_manager):
    """Create wake word detector for testing."""
    return WakeWordDetector(conversation_config, speech_manager)


@pytest.fixture
def time_tool():
    """Create time tool for testing."""
    return TimeTool()


@pytest.fixture
def video_tool():
    """Create video tool for testing."""
    return VideoTool()


# Mock patches for external dependencies
@pytest.fixture
def mock_speech_recognition():
    """Mock speech_recognition module."""
    with patch('jarvis.audio.microphone.sr') as mock_sr:
        mock_sr.Microphone = Mock
        mock_sr.Recognizer = Mock
        mock_sr.WaitTimeoutError = Exception
        mock_sr.UnknownValueError = Exception
        mock_sr.RequestError = Exception
        yield mock_sr


@pytest.fixture
def mock_pyttsx3():
    """Mock pyttsx3 module."""
    with patch('jarvis.audio.tts.pyttsx3') as mock_pyttsx3:
        mock_pyttsx3.init.return_value = Mock()
        yield mock_pyttsx3


@pytest.fixture
def mock_langchain_ollama():
    """Mock langchain_ollama module."""
    with patch('jarvis.core.agent.ChatOllama') as mock_ollama:
        mock_ollama.return_value = Mock()
        yield mock_ollama


@pytest.fixture
def mock_langchain_agents():
    """Mock langchain agents module."""
    with patch('jarvis.core.agent.create_tool_calling_agent') as mock_create_agent, \
         patch('jarvis.core.agent.AgentExecutor') as mock_executor:
        mock_create_agent.return_value = Mock()
        mock_executor.return_value = Mock()
        yield mock_create_agent, mock_executor


# mock_pytz fixture removed - no longer needed after TimeTool removal


# Test data fixtures
@pytest.fixture
def sample_audio_bytes():
    """Sample audio data as bytes."""
    return b'\x00\x01' * 500  # 1000 bytes of sample audio


@pytest.fixture
def sample_speech_text():
    """Sample speech recognition text."""
    return "Hello Jarvis, what time is it?"


@pytest.fixture
def sample_wake_word_phrases():
    """Sample phrases for wake word testing."""
    return [
        "Hey Jarvis",
        "Jarvis are you there",
        "Hello Jarvis",
        "This should not trigger",
        "Random speech without wake word"
    ]


@pytest.fixture
def sample_time_queries():
    """Sample time-related queries."""
    return [
        ("", "local time"),
        ("New York", "New York time"),
        ("London", "London time"),
        ("Tokyo", "Tokyo time"),
        ("InvalidCity", "error")
    ]


@pytest.fixture
def sample_video_queries():
    """Sample video content queries."""
    return [
        ("", "general advice"),
        ("productivity", "productivity advice"),
        ("technology", "technology advice")
    ]


# Utility functions for tests
def create_mock_audio_data(sample_rate=16000, sample_width=2, data_length=1000):
    """Create mock audio data with specified parameters."""
    mock_audio = Mock()
    mock_audio.get_raw_data.return_value = b'\x00' * data_length
    mock_audio.sample_rate = sample_rate
    mock_audio.sample_width = sample_width
    return mock_audio


def assert_log_contains(caplog, level, message):
    """Assert that log contains a specific message at a specific level."""
    for record in caplog.records:
        if record.levelname == level and message in record.message:
            return True
    pytest.fail(f"Log message '{message}' at level '{level}' not found")


def assert_exception_raised(func, exception_type, *args, **kwargs):
    """Assert that a function raises a specific exception type."""
    with pytest.raises(exception_type):
        func(*args, **kwargs)
