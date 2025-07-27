"""
Unit tests for Jarvis configuration management.

This module tests the configuration system including environment variable
loading, validation, and default values.
"""

import pytest
import os
from unittest.mock import patch
from pathlib import Path

from jarvis.config import (
    AudioConfig, ConversationConfig, LLMConfig, LoggingConfig, GeneralConfig,
    JarvisConfig, get_config, reload_config
)
from jarvis.exceptions import ConfigurationError


class TestAudioConfig:
    """Test AudioConfig class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = AudioConfig()
        
        assert config.mic_index == 2
        assert config.mic_name == "MacBook Pro Microphone"
        assert config.energy_threshold == 100
        assert config.timeout == 2.0
        assert config.phrase_time_limit == 4.0
        assert config.tts_rate == 180
        assert config.tts_volume == 1.0
        assert config.tts_voice_preference == "jamie"
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = AudioConfig(
            mic_index=1,
            mic_name="Test Mic",
            energy_threshold=200,
            timeout=3.0,
            phrase_time_limit=5.0,
            tts_rate=150,
            tts_volume=0.8,
            tts_voice_preference="alex"
        )
        
        assert config.mic_index == 1
        assert config.mic_name == "Test Mic"
        assert config.energy_threshold == 200
        assert config.timeout == 3.0
        assert config.phrase_time_limit == 5.0
        assert config.tts_rate == 150
        assert config.tts_volume == 0.8
        assert config.tts_voice_preference == "alex"


class TestConversationConfig:
    """Test ConversationConfig class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = ConversationConfig()
        
        assert config.wake_word == "jarvis"
        assert config.conversation_timeout == 30
        assert config.max_retries == 3
        assert config.response_delay == 0.3
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = ConversationConfig(
            wake_word="test",
            conversation_timeout=60,
            max_retries=5,
            response_delay=0.5
        )
        
        assert config.wake_word == "test"
        assert config.conversation_timeout == 60
        assert config.max_retries == 5
        assert config.response_delay == 0.5


class TestLLMConfig:
    """Test LLMConfig class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = LLMConfig()

        assert config.model == "llama3.1:8b"
        assert config.verbose is False
        assert config.reasoning is False
        assert config.temperature == 0.7
        assert config.max_tokens is None
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = LLMConfig(
            model="test-model",
            verbose=True,
            reasoning=True,
            temperature=0.5,
            max_tokens=1000
        )
        
        assert config.model == "test-model"
        assert config.verbose is True
        assert config.reasoning is True
        assert config.temperature == 0.5
        assert config.max_tokens == 1000


class TestLoggingConfig:
    """Test LoggingConfig class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = LoggingConfig()
        
        assert config.level == "INFO"
        assert config.file is None
        assert "%(asctime)s" in config.format
        assert config.date_format == "%Y-%m-%d %H:%M:%S"
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = LoggingConfig(
            level="DEBUG",
            file="/tmp/test.log",
            format="%(message)s",
            date_format="%H:%M:%S"
        )
        
        assert config.level == "DEBUG"
        assert config.file == "/tmp/test.log"
        assert config.format == "%(message)s"
        assert config.date_format == "%H:%M:%S"


class TestGeneralConfig:
    """Test GeneralConfig class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = GeneralConfig()
        
        assert config.debug is False
        assert config.data_dir == Path.home() / ".jarvis"
        assert config.config_file is None
    
    def test_custom_values(self, temp_dir):
        """Test custom configuration values."""
        config_file = temp_dir / "config.toml"
        
        config = GeneralConfig(
            debug=True,
            data_dir=temp_dir,
            config_file=config_file
        )
        
        assert config.debug is True
        assert config.data_dir == temp_dir
        assert config.config_file == config_file


class TestJarvisConfig:
    """Test JarvisConfig class."""
    
    def test_default_initialization(self):
        """Test default configuration initialization."""
        config = JarvisConfig()
        
        assert isinstance(config.audio, AudioConfig)
        assert isinstance(config.conversation, ConversationConfig)
        assert isinstance(config.llm, LLMConfig)
        assert isinstance(config.logging, LoggingConfig)
        assert isinstance(config.general, GeneralConfig)
    
    def test_from_env_with_no_env_vars(self):
        """Test configuration from environment with no variables set."""
        with patch.dict(os.environ, {}, clear=True):
            config = JarvisConfig.from_env()
            
            # Should use default values
            assert config.audio.mic_index == 2
            assert config.conversation.wake_word == "jarvis"
            assert config.llm.model == "qwen2.5:1.5b"
    
    def test_from_env_with_env_vars(self):
        """Test configuration from environment variables."""
        env_vars = {
            'JARVIS_MIC_INDEX': '1',
            'JARVIS_WAKE_WORD': 'test',
            'JARVIS_MODEL': 'test-model',
            'JARVIS_VERBOSE': 'true',
            'JARVIS_LOG_LEVEL': 'DEBUG',
            'JARVIS_DEBUG': 'yes'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = JarvisConfig.from_env()
            
            assert config.audio.mic_index == 1
            assert config.conversation.wake_word == "test"
            assert config.llm.model == "test-model"
            assert config.llm.verbose is True
            assert config.logging.level == "DEBUG"
            assert config.general.debug is True
    
    def test_from_env_with_invalid_values(self):
        """Test configuration with invalid environment values."""
        env_vars = {
            'JARVIS_MIC_INDEX': 'invalid',
            'JARVIS_ENERGY_THRESHOLD': 'not_a_number',
            'JARVIS_TTS_VOLUME': 'invalid_float'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = JarvisConfig.from_env()
            
            # Should fall back to defaults for invalid values
            assert config.audio.mic_index == 2  # Default
            assert config.audio.energy_threshold == 100  # Default
            assert config.audio.tts_volume == 1.0  # Default
    
    def test_validate_success(self):
        """Test successful configuration validation."""
        config = JarvisConfig()
        
        # Should not raise any exceptions
        config.validate()
    
    def test_validate_invalid_mic_index(self):
        """Test validation with invalid microphone index."""
        config = JarvisConfig()
        config.audio.mic_index = -1
        
        with pytest.raises(ValueError, match="Microphone index must be non-negative"):
            config.validate()
    
    def test_validate_invalid_energy_threshold(self):
        """Test validation with invalid energy threshold."""
        config = JarvisConfig()
        config.audio.energy_threshold = 0
        
        with pytest.raises(ValueError, match="Energy threshold must be positive"):
            config.validate()
    
    def test_validate_invalid_tts_volume(self):
        """Test validation with invalid TTS volume."""
        config = JarvisConfig()
        config.audio.tts_volume = 1.5
        
        with pytest.raises(ValueError, match="TTS volume must be between 0 and 1"):
            config.validate()
    
    def test_validate_empty_wake_word(self):
        """Test validation with empty wake word."""
        config = JarvisConfig()
        config.conversation.wake_word = ""
        
        with pytest.raises(ValueError, match="Wake word cannot be empty"):
            config.validate()
    
    def test_validate_invalid_log_level(self):
        """Test validation with invalid log level."""
        config = JarvisConfig()
        config.logging.level = "INVALID"
        
        with pytest.raises(ValueError, match="Log level must be one of"):
            config.validate()
    
    def test_validate_creates_data_directory(self, temp_dir):
        """Test that validation creates data directory."""
        config = JarvisConfig()
        config.general.data_dir = temp_dir / "new_dir"
        
        assert not config.general.data_dir.exists()
        config.validate()
        assert config.general.data_dir.exists()


class TestConfigurationFunctions:
    """Test configuration utility functions."""
    
    def test_get_config_singleton(self):
        """Test that get_config returns the same instance."""
        config1 = get_config()
        config2 = get_config()
        
        assert config1 is config2
    
    def test_reload_config(self):
        """Test configuration reloading."""
        # Get initial config
        config1 = get_config()
        
        # Reload config
        config2 = reload_config()
        
        # Should be different instances but same values
        assert config1 is not config2
        assert config1.audio.mic_index == config2.audio.mic_index
    
    def test_reload_config_with_env_changes(self):
        """Test configuration reloading with environment changes."""
        # Get initial config
        config1 = get_config()
        original_wake_word = config1.conversation.wake_word
        
        # Change environment and reload
        with patch.dict(os.environ, {'JARVIS_WAKE_WORD': 'new_wake_word'}):
            config2 = reload_config()
            
            assert config2.conversation.wake_word == 'new_wake_word'
            assert config2.conversation.wake_word != original_wake_word
