"""
Configuration management for Jarvis Voice Assistant.

This module handles all configuration settings with environment variable support,
validation, and sensible defaults.
"""

import os
import logging
from typing import Optional, Union, Any
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv


@dataclass
class AudioConfig:
    """Audio-related configuration settings."""
    mic_index: int = 0  # Default microphone
    mic_name: str = ". . . Microphone"
    energy_threshold: int = 100
    timeout: float = 2.0
    phrase_time_limit: float = 4.0

    # Legacy TTS settings (kept for compatibility)
    tts_rate: int = 180
    tts_volume: float = 0.8
    tts_voice_preference: str = "Daniel"  # Preferred voice name (British male voice)
    response_delay: float = 0.5  # Delay after speech completion

    # Whisper Speech Recognition settings
    whisper_model_size: str = "base"  # tiny, base, small, medium, large
    whisper_device: str = "cpu"
    whisper_language: str = "en"  # or "auto" for auto-detection
    whisper_compute_type: str = "float32"

    # Coqui TTS settings
    coqui_model: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    coqui_language: str = "en"
    coqui_device: str = "auto"  # auto, cpu, cuda, mps
    coqui_use_gpu: bool = True
    coqui_speaker_wav: Optional[str] = None  # Path to voice cloning audio
    coqui_temperature: float = 0.75
    coqui_length_penalty: float = 1.0
    coqui_repetition_penalty: float = 5.0
    coqui_top_k: int = 50
    coqui_top_p: float = 0.85
    coqui_streaming: bool = False  # Enable streaming mode (future feature)


@dataclass
class ConversationConfig:
    """Conversation flow configuration settings."""
    wake_word: str = "jarvis"
    conversation_timeout: int = 30  # seconds
    max_retries: int = 3


@dataclass
class LLMConfig:
    """Language model configuration settings."""
    model: str = "qwen2.5:1.5b"
    verbose: bool = False
    reasoning: bool = False
    temperature: float = 0.7
    max_tokens: Optional[int] = None


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    file: Optional[str] = None
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"


@dataclass
class GeneralConfig:
    """General application configuration settings."""
    debug: bool = False
    data_dir: Path = field(default_factory=lambda: Path.home() / ".jarvis")
    config_file: Optional[Path] = None


@dataclass
class JarvisConfig:
    """Main configuration class containing all settings."""
    audio: AudioConfig = field(default_factory=AudioConfig)
    conversation: ConversationConfig = field(default_factory=ConversationConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    general: GeneralConfig = field(default_factory=GeneralConfig)
    
    @classmethod
    def from_env(cls) -> 'JarvisConfig':
        """
        Create configuration from environment variables.
        
        Returns:
            JarvisConfig instance with values from environment variables.
        """
        config = cls()
        
        # Audio configuration
        config.audio.mic_index = _get_env_int("JARVIS_MIC_INDEX", config.audio.mic_index)
        config.audio.mic_name = _get_env_str("JARVIS_MIC_NAME", config.audio.mic_name)
        config.audio.energy_threshold = _get_env_int("JARVIS_ENERGY_THRESHOLD", config.audio.energy_threshold)
        config.audio.timeout = _get_env_float("JARVIS_AUDIO_TIMEOUT", config.audio.timeout)
        config.audio.phrase_time_limit = _get_env_float("JARVIS_PHRASE_TIME_LIMIT", config.audio.phrase_time_limit)
        config.audio.tts_rate = _get_env_int("JARVIS_TTS_RATE", config.audio.tts_rate)
        config.audio.tts_volume = _get_env_float("JARVIS_TTS_VOLUME", config.audio.tts_volume)
        config.audio.tts_voice_preference = _get_env_str("JARVIS_TTS_VOICE", config.audio.tts_voice_preference)
        config.audio.response_delay = _get_env_float("JARVIS_RESPONSE_DELAY", config.audio.response_delay)

        # Whisper Speech Recognition configuration
        config.audio.whisper_model_size = _get_env_str("JARVIS_WHISPER_MODEL_SIZE", config.audio.whisper_model_size)
        config.audio.whisper_device = _get_env_str("JARVIS_WHISPER_DEVICE", config.audio.whisper_device)
        config.audio.whisper_language = _get_env_str("JARVIS_WHISPER_LANGUAGE", config.audio.whisper_language)
        config.audio.whisper_compute_type = _get_env_str("JARVIS_WHISPER_COMPUTE_TYPE", config.audio.whisper_compute_type)

        # Coqui TTS configuration
        config.audio.coqui_model = _get_env_str("JARVIS_COQUI_MODEL", config.audio.coqui_model)
        config.audio.coqui_language = _get_env_str("JARVIS_COQUI_LANGUAGE", config.audio.coqui_language)
        config.audio.coqui_device = _get_env_str("JARVIS_COQUI_DEVICE", config.audio.coqui_device)
        config.audio.coqui_use_gpu = _get_env_bool("JARVIS_COQUI_USE_GPU", config.audio.coqui_use_gpu)
        config.audio.coqui_speaker_wav = _get_env_str("JARVIS_COQUI_SPEAKER_WAV", config.audio.coqui_speaker_wav)
        config.audio.coqui_temperature = _get_env_float("JARVIS_COQUI_TEMPERATURE", config.audio.coqui_temperature)
        config.audio.coqui_length_penalty = _get_env_float("JARVIS_COQUI_LENGTH_PENALTY", config.audio.coqui_length_penalty)
        config.audio.coqui_repetition_penalty = _get_env_float("JARVIS_COQUI_REPETITION_PENALTY", config.audio.coqui_repetition_penalty)
        config.audio.coqui_top_k = _get_env_int("JARVIS_COQUI_TOP_K", config.audio.coqui_top_k)
        config.audio.coqui_top_p = _get_env_float("JARVIS_COQUI_TOP_P", config.audio.coqui_top_p)
        config.audio.coqui_streaming = _get_env_bool("JARVIS_COQUI_STREAMING", config.audio.coqui_streaming)
        
        # Conversation configuration
        config.conversation.wake_word = _get_env_str("JARVIS_WAKE_WORD", config.conversation.wake_word)
        config.conversation.conversation_timeout = _get_env_int("JARVIS_CONVERSATION_TIMEOUT", config.conversation.conversation_timeout)
        config.conversation.max_retries = _get_env_int("JARVIS_MAX_RETRIES", config.conversation.max_retries)
        
        # LLM configuration
        config.llm.model = _get_env_str("JARVIS_MODEL", config.llm.model)
        config.llm.verbose = _get_env_bool("JARVIS_VERBOSE", config.llm.verbose)
        config.llm.reasoning = _get_env_bool("JARVIS_REASONING", config.llm.reasoning)
        config.llm.temperature = _get_env_float("JARVIS_TEMPERATURE", config.llm.temperature)
        max_tokens_str = os.getenv("JARVIS_MAX_TOKENS")
        if max_tokens_str:
            config.llm.max_tokens = int(max_tokens_str)
        
        # Logging configuration
        config.logging.level = _get_env_str("JARVIS_LOG_LEVEL", config.logging.level)
        config.logging.file = _get_env_str("JARVIS_LOG_FILE", config.logging.file)
        config.logging.format = _get_env_str("JARVIS_LOG_FORMAT", config.logging.format)
        config.logging.date_format = _get_env_str("JARVIS_LOG_DATE_FORMAT", config.logging.date_format)
        
        # General configuration
        config.general.debug = _get_env_bool("JARVIS_DEBUG", config.general.debug)
        data_dir_str = os.getenv("JARVIS_DATA_DIR")
        if data_dir_str:
            config.general.data_dir = Path(data_dir_str)
        config_file_str = os.getenv("JARVIS_CONFIG_FILE")
        if config_file_str:
            config.general.config_file = Path(config_file_str)
        
        return config
    
    def validate(self) -> None:
        """
        Validate configuration settings.
        
        Raises:
            ValueError: If any configuration values are invalid.
        """
        # Validate audio settings
        if self.audio.mic_index < 0:
            raise ValueError("Microphone index must be non-negative")
        if self.audio.energy_threshold <= 0:
            raise ValueError("Energy threshold must be positive")
        if self.audio.timeout <= 0:
            raise ValueError("Audio timeout must be positive")
        if self.audio.phrase_time_limit <= 0:
            raise ValueError("Phrase time limit must be positive")
        if not 0 <= self.audio.tts_volume <= 1:
            raise ValueError("TTS volume must be between 0 and 1")
        if self.audio.tts_rate <= 0:
            raise ValueError("TTS rate must be positive")
        
        # Validate conversation settings
        if not self.conversation.wake_word.strip():
            raise ValueError("Wake word cannot be empty")
        if self.conversation.conversation_timeout <= 0:
            raise ValueError("Conversation timeout must be positive")
        if self.conversation.max_retries < 0:
            raise ValueError("Max retries must be non-negative")
        
        # Validate LLM settings
        if not self.llm.model.strip():
            raise ValueError("LLM model name cannot be empty")
        if not 0 <= self.llm.temperature <= 2:
            raise ValueError("LLM temperature must be between 0 and 2")
        if self.llm.max_tokens is not None and self.llm.max_tokens <= 0:
            raise ValueError("Max tokens must be positive if specified")
        
        # Validate logging settings
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.logging.level.upper() not in valid_log_levels:
            raise ValueError(f"Log level must be one of: {valid_log_levels}")
        
        # Create data directory if it doesn't exist
        self.general.data_dir.mkdir(parents=True, exist_ok=True)


def _get_env_str(key: str, default: str) -> str:
    """Get string value from environment variable."""
    return os.getenv(key, default)


def _get_env_int(key: str, default: int) -> int:
    """Get integer value from environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        logging.warning(f"Invalid integer value for {key}: {value}, using default: {default}")
        return default


def _get_env_float(key: str, default: float) -> float:
    """Get float value from environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        logging.warning(f"Invalid float value for {key}: {value}, using default: {default}")
        return default


def _get_env_bool(key: str, default: bool) -> bool:
    """Get boolean value from environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes", "on")


# Global configuration instance
_config: Optional[JarvisConfig] = None


def get_config() -> JarvisConfig:
    """
    Get the global configuration instance.

    Returns:
        JarvisConfig instance.
    """
    global _config
    if _config is None:
        # Load environment variables from .env file
        load_dotenv()
        _config = JarvisConfig.from_env()
        _config.validate()
    return _config


def reload_config() -> JarvisConfig:
    """
    Reload configuration from environment variables.

    Returns:
        New JarvisConfig instance.
    """
    global _config
    _config = JarvisConfig.from_env()
    _config.validate()
    return _config


def clear_config_cache() -> None:
    """Clear the cached configuration to force reload."""
    global _config
    _config = None
