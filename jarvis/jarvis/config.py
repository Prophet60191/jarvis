"""
Configuration management for Jarvis Voice Assistant.

This module handles all configuration settings with environment variable support,
validation, and sensible defaults.
"""

import os
import logging
from typing import Optional, Union, Any, Callable, Dict, List
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv
import threading
import time
from enum import Enum


class ConfigSection(Enum):
    """Configuration sections that can be monitored for changes."""
    AUDIO = "audio"
    CONVERSATION = "conversation"
    LLM = "llm"
    LOGGING = "logging"
    GENERAL = "general"
    MCP = "mcp"
    RAG = "rag"
    ALL = "all"


class ConfigChangeNotifier:
    """Manages configuration change notifications and callbacks."""

    def __init__(self):
        self._callbacks: Dict[ConfigSection, List[Callable]] = {
            section: [] for section in ConfigSection
        }
        self._lock = threading.Lock()

    def register_callback(self, section: ConfigSection, callback: Callable[[Any], None]) -> None:
        """
        Register a callback for configuration changes.

        Args:
            section: Configuration section to monitor
            callback: Function to call when configuration changes
        """
        with self._lock:
            self._callbacks[section].append(callback)
            logging.debug(f"Registered callback for {section.value} configuration changes")

    def unregister_callback(self, section: ConfigSection, callback: Callable[[Any], None]) -> None:
        """
        Unregister a callback for configuration changes.

        Args:
            section: Configuration section
            callback: Function to remove
        """
        with self._lock:
            if callback in self._callbacks[section]:
                self._callbacks[section].remove(callback)
                logging.debug(f"Unregistered callback for {section.value} configuration changes")

    def notify_change(self, section: ConfigSection, new_config: Any) -> None:
        """
        Notify all registered callbacks of a configuration change.

        Args:
            section: Configuration section that changed
            new_config: New configuration object
        """
        with self._lock:
            # Notify specific section callbacks
            for callback in self._callbacks[section]:
                try:
                    callback(new_config)
                except Exception as e:
                    logging.error(f"Error in config change callback for {section.value}: {e}")

            # Notify ALL section callbacks
            for callback in self._callbacks[ConfigSection.ALL]:
                try:
                    callback(new_config)
                except Exception as e:
                    logging.error(f"Error in config change callback for ALL: {e}")


# Global configuration change notifier
_config_notifier = ConfigChangeNotifier()


def get_config_notifier() -> ConfigChangeNotifier:
    """Get the global configuration change notifier."""
    return _config_notifier


@dataclass
class AudioConfig:
    """Audio-related configuration settings."""
    mic_index: int = 0  # Default microphone
    mic_name: str = ". . . Microphone"
    energy_threshold: int = 100
    timeout: float = 3.0  # Balanced for responsiveness and reliability
    phrase_time_limit: float = 5.0  # Optimized for natural speech patterns

    # Legacy TTS settings (kept for compatibility)
    tts_rate: int = 180
    tts_volume: float = 0.8
    tts_voice_preference: str = "Daniel"  # Preferred voice name (British male voice)
    response_delay: float = 0.5  # Delay after speech completion

    # Whisper Speech Recognition settings - Optimized for speed
    whisper_model_size: str = "tiny"  # tiny=fastest, base=balanced, small=accurate
    whisper_device: str = "cpu"  # Apple Silicon optimized
    whisper_language: str = "en"  # Fixed language for speed
    whisper_compute_type: str = "int8"  # Quantized for faster inference

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

    # TTS Fallback settings (configurable through settings UI)
    tts_fallback_voices: List[str] = field(default_factory=lambda: [
        "daniel", "alex", "samantha", "victoria", "karen"
    ])  # Priority order for voice selection
    tts_fallback_rate_cap: int = 200  # Maximum TTS rate for clarity
    tts_fallback_enabled: bool = True  # Enable enhanced fallback TTS


@dataclass
class ConversationConfig:
    """Conversation flow configuration settings."""
    wake_word: str = "jarvis"
    conversation_timeout: int = 30  # seconds
    max_retries: int = 3
    enable_full_duplex: bool = False  # DISABLED: Full-duplex was too sensitive, causing cutoffs


@dataclass
class LLMConfig:
    """Language model configuration settings."""
    model: str = "qwen2.5:7b-instruct"  # Excellent tool calling, natural language, and reasoning capabilities
    verbose: bool = False
    reasoning: bool = False
    temperature: float = 0.7
    max_tokens: Optional[int] = None


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    file: Optional[str] = "jarvis_debug.log"  # Default to log file for terminal viewing
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"


@dataclass
class MCPServerConfig:
    """Configuration for a single MCP server."""
    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Optional[Dict[str, str]] = None
    enabled: bool = True
    timeout: int = 30


@dataclass
class MCPConfig:
    """MCP (Model Context Protocol) configuration settings."""
    servers: Dict[str, MCPServerConfig] = field(default_factory=lambda: {
        "memory_storage": MCPServerConfig(
            name="memory_storage",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-memory"],
            env=None,
            enabled=False,  # Disabled - using RAG memory system instead
            timeout=30
        )
    })
    enabled: bool = True


@dataclass
class GeneralConfig:
    """General application configuration settings."""
    debug: bool = False
    data_dir: Path = field(default_factory=lambda: Path.home() / ".jarvis")
    config_file: Optional[Path] = None


@dataclass
class RAGConfig:
    """RAG (Retrieval-Augmented Generation) memory system configuration."""
    enabled: bool = True
    vector_store_path: str = "data/chroma_db"
    documents_path: str = "data/documents"
    backup_path: str = "data/backups"
    collection_name: str = "jarvis_memory"
    chunk_size: int = 1000
    chunk_overlap: int = 150
    search_k: int = 5


@dataclass
class JarvisConfig:
    """Main configuration class containing all settings."""
    audio: AudioConfig = field(default_factory=AudioConfig)
    conversation: ConversationConfig = field(default_factory=ConversationConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    general: GeneralConfig = field(default_factory=GeneralConfig)
    mcp: MCPConfig = field(default_factory=MCPConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    
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

        # TTS Fallback configuration
        fallback_voices_str = os.getenv("JARVIS_TTS_FALLBACK_VOICES")
        if fallback_voices_str:
            config.audio.tts_fallback_voices = [v.strip() for v in fallback_voices_str.split(",") if v.strip()]
        config.audio.tts_fallback_rate_cap = _get_env_int("JARVIS_TTS_FALLBACK_RATE_CAP", config.audio.tts_fallback_rate_cap)
        config.audio.tts_fallback_enabled = _get_env_bool("JARVIS_TTS_FALLBACK_ENABLED", config.audio.tts_fallback_enabled)

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

        # MCP configuration
        config.mcp.enabled = _get_env_bool("JARVIS_MCP_ENABLED", config.mcp.enabled)

        # RAG configuration
        config.rag.enabled = _get_env_bool("JARVIS_RAG_ENABLED", config.rag.enabled)
        config.rag.vector_store_path = _get_env_str("JARVIS_RAG_VECTOR_STORE_PATH", config.rag.vector_store_path)
        config.rag.documents_path = _get_env_str("JARVIS_RAG_DOCUMENTS_PATH", config.rag.documents_path)
        config.rag.backup_path = _get_env_str("JARVIS_RAG_BACKUP_PATH", config.rag.backup_path)
        config.rag.collection_name = _get_env_str("JARVIS_RAG_COLLECTION_NAME", config.rag.collection_name)
        config.rag.chunk_size = _get_env_int("JARVIS_RAG_CHUNK_SIZE", config.rag.chunk_size)
        config.rag.chunk_overlap = _get_env_int("JARVIS_RAG_CHUNK_OVERLAP", config.rag.chunk_overlap)
        config.rag.search_k = _get_env_int("JARVIS_RAG_SEARCH_K", config.rag.search_k)

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
    Reload configuration from environment variables and notify components.

    Returns:
        New JarvisConfig instance.
    """
    global _config
    old_config = _config

    # Load new configuration
    load_dotenv(override=True)  # Reload .env file with override
    _config = JarvisConfig.from_env()
    _config.validate()

    # Notify components of configuration changes
    if old_config is not None:
        notifier = get_config_notifier()

        # Check which sections changed and notify accordingly
        if old_config.audio != _config.audio:
            notifier.notify_change(ConfigSection.AUDIO, _config.audio)
            logging.info("Audio configuration reloaded")

        if old_config.conversation != _config.conversation:
            notifier.notify_change(ConfigSection.CONVERSATION, _config.conversation)
            logging.info("Conversation configuration reloaded")

        if old_config.llm != _config.llm:
            notifier.notify_change(ConfigSection.LLM, _config.llm)
            logging.info("LLM configuration reloaded")

        if old_config.logging != _config.logging:
            notifier.notify_change(ConfigSection.LOGGING, _config.logging)
            logging.info("Logging configuration reloaded")

        if old_config.general != _config.general:
            notifier.notify_change(ConfigSection.GENERAL, _config.general)
            logging.info("General configuration reloaded")

        # Always notify ALL listeners
        notifier.notify_change(ConfigSection.ALL, _config)

    logging.info("Configuration reloaded successfully")
    return _config


def clear_config_cache() -> None:
    """Clear the cached configuration to force reload."""
    global _config
    _config = None


def trigger_config_reload() -> JarvisConfig:
    """
    Trigger a configuration reload from external sources (like UI).

    This function is designed to be called when configuration is updated
    externally (e.g., through the web UI) and components need to be notified.

    Returns:
        New JarvisConfig instance.
    """
    logging.info("Configuration reload triggered externally")
    return reload_config()


def register_config_change_callback(section: ConfigSection, callback: Callable[[Any], None]) -> None:
    """
    Register a callback to be notified when configuration changes.

    Args:
        section: Configuration section to monitor
        callback: Function to call when configuration changes
    """
    get_config_notifier().register_callback(section, callback)


def unregister_config_change_callback(section: ConfigSection, callback: Callable[[Any], None]) -> None:
    """
    Unregister a configuration change callback.

    Args:
        section: Configuration section
        callback: Function to remove
    """
    get_config_notifier().unregister_callback(section, callback)
