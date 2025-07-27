"""
Multi-language TTS support for Jarvis Voice Assistant.

This module provides comprehensive multi-language text-to-speech capabilities
with automatic language detection, voice profile language matching, and
language-specific voice selection.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

try:
    from langdetect import detect, detect_langs
    from langdetect.lang_detect_exception import LangDetectException
except ImportError:
    detect = None
    detect_langs = None
    LangDetectException = Exception

from ..config import AudioConfig
from ..exceptions import TextToSpeechError
from .coqui_tts import CoquiTTSManager
from .voice_profiles import VoiceProfileManager


logger = logging.getLogger(__name__)


class LanguageCode(Enum):
    """Supported language codes for XTTS-v2."""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    POLISH = "pl"
    TURKISH = "tr"
    RUSSIAN = "ru"
    DUTCH = "nl"
    CZECH = "cs"
    ARABIC = "ar"
    CHINESE = "zh-cn"
    JAPANESE = "ja"
    HUNGARIAN = "hu"
    KOREAN = "ko"


@dataclass
class LanguageDetectionResult:
    """Result of language detection."""
    language: str
    confidence: float
    alternatives: List[Tuple[str, float]]


@dataclass
class MultiLanguageConfig:
    """Configuration for multi-language TTS."""
    auto_detect_language: bool = True
    fallback_language: str = "en"
    min_confidence_threshold: float = 0.7
    prefer_voice_profile_language: bool = True
    mixed_language_support: bool = True
    language_switching_enabled: bool = True


class MultiLanguageTTSManager:
    """
    Manages multi-language text-to-speech operations.
    
    This class provides comprehensive multi-language TTS support with
    automatic language detection, voice profile language matching,
    and intelligent language switching.
    """
    
    def __init__(self, config: AudioConfig, multilang_config: Optional[MultiLanguageConfig] = None):
        """
        Initialize the multi-language TTS manager.
        
        Args:
            config: Audio configuration settings
            multilang_config: Multi-language specific configuration
        """
        self.config = config
        self.multilang_config = multilang_config or MultiLanguageConfig()
        
        # Initialize base TTS manager and voice manager
        self.tts_manager = CoquiTTSManager(config)
        self.voice_manager = VoiceProfileManager()
        
        # Language detection availability
        self.lang_detection_available = detect is not None and detect_langs is not None
        if not self.lang_detection_available:
            logger.warning("Language detection not available. Install langdetect: pip install langdetect")
        
        # Supported languages
        self.supported_languages = {lang.value for lang in LanguageCode}
        
        # Language name mappings
        self.language_names = {
            "en": "English",
            "es": "Spanish", 
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "pl": "Polish",
            "tr": "Turkish",
            "ru": "Russian",
            "nl": "Dutch",
            "cs": "Czech",
            "ar": "Arabic",
            "zh-cn": "Chinese",
            "ja": "Japanese",
            "hu": "Hungarian",
            "ko": "Korean"
        }
        
        # Current language state
        self.current_language = self.multilang_config.fallback_language
        self.current_voice_profile_by_language: Dict[str, str] = {}
        
        logger.info(f"MultiLanguageTTSManager initialized with {len(self.supported_languages)} supported languages")
    
    def initialize(self) -> None:
        """Initialize the underlying TTS engine."""
        self.tts_manager.initialize()
        logger.info("Multi-language TTS manager initialized")
    
    def is_initialized(self) -> bool:
        """Check if the TTS engine is initialized."""
        return self.tts_manager.is_initialized()
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported language codes.
        
        Returns:
            List of supported language codes
        """
        return list(self.supported_languages)
    
    def get_language_name(self, language_code: str) -> str:
        """
        Get human-readable language name.
        
        Args:
            language_code: Language code
            
        Returns:
            Human-readable language name
        """
        return self.language_names.get(language_code, language_code.upper())
    
    def detect_language(self, text: str) -> Optional[LanguageDetectionResult]:
        """
        Detect the language of the given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            LanguageDetectionResult if detection successful, None otherwise
        """
        if not self.lang_detection_available:
            logger.debug("Language detection not available")
            return None
        
        if not text or not text.strip():
            return None
        
        try:
            # Clean text for better detection
            clean_text = re.sub(r'[^\w\s]', ' ', text)
            clean_text = ' '.join(clean_text.split())
            
            if len(clean_text) < 10:  # Too short for reliable detection
                return None
            
            # Detect language with alternatives
            detected_langs = detect_langs(clean_text)
            
            if not detected_langs:
                return None
            
            primary_lang = detected_langs[0]
            
            # Map langdetect codes to our supported codes
            lang_code = self._map_language_code(primary_lang.lang)
            
            if lang_code not in self.supported_languages:
                logger.debug(f"Detected language '{lang_code}' not supported")
                return None
            
            # Build alternatives list
            alternatives = []
            for lang_result in detected_langs[1:5]:  # Top 5 alternatives
                mapped_code = self._map_language_code(lang_result.lang)
                if mapped_code in self.supported_languages:
                    alternatives.append((mapped_code, lang_result.prob))
            
            return LanguageDetectionResult(
                language=lang_code,
                confidence=primary_lang.prob,
                alternatives=alternatives
            )
            
        except LangDetectException as e:
            logger.debug(f"Language detection failed: {e}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error in language detection: {e}")
            return None
    
    def _map_language_code(self, detected_code: str) -> str:
        """
        Map langdetect language codes to our supported codes.
        
        Args:
            detected_code: Language code from langdetect
            
        Returns:
            Mapped language code
        """
        # Mapping from langdetect codes to XTTS-v2 codes
        code_mapping = {
            "zh-cn": "zh-cn",
            "zh": "zh-cn",
            "zh-tw": "zh-cn",  # Map Traditional Chinese to Simplified
            "pt": "pt",
            "pt-br": "pt",  # Map Brazilian Portuguese to Portuguese
            "ar": "ar",
            "ca": "es",  # Map Catalan to Spanish
            "eu": "es",  # Map Basque to Spanish
            "gl": "es",  # Map Galician to Spanish
        }
        
        return code_mapping.get(detected_code, detected_code)
    
    def get_voice_profiles_for_language(self, language: str) -> List[Any]:
        """
        Get voice profiles available for a specific language.
        
        Args:
            language: Language code
            
        Returns:
            List of voice profiles for the language
        """
        return self.voice_manager.get_profiles_by_language(language)
    
    def set_language_voice_profile(self, language: str, profile_id: str) -> bool:
        """
        Set the voice profile to use for a specific language.
        
        Args:
            language: Language code
            profile_id: Voice profile ID
            
        Returns:
            True if set successfully, False otherwise
        """
        if language not in self.supported_languages:
            logger.warning(f"Unsupported language: {language}")
            return False
        
        profile = self.voice_manager.get_profile(profile_id)
        if not profile:
            logger.warning(f"Voice profile not found: {profile_id}")
            return False
        
        self.current_voice_profile_by_language[language] = profile_id
        logger.info(f"Set voice profile '{profile.name}' for language '{language}'")
        return True
    
    def get_best_voice_profile_for_language(self, language: str) -> Optional[str]:
        """
        Get the best voice profile for a specific language.
        
        Args:
            language: Language code
            
        Returns:
            Profile ID of the best voice profile, None if not found
        """
        # Check if we have a manually set profile for this language
        if language in self.current_voice_profile_by_language:
            return self.current_voice_profile_by_language[language]
        
        # Get profiles for this language
        profiles = self.get_voice_profiles_for_language(language)
        
        if not profiles:
            # Fallback to any active profile
            all_profiles = self.voice_manager.get_active_profiles()
            if all_profiles:
                best_profile = max(all_profiles, key=lambda p: p.quality_score)
                logger.info(f"Using fallback voice profile '{best_profile.name}' for language '{language}'")
                return best_profile.id
            return None
        
        # Select the best quality profile for this language
        best_profile = max(profiles, key=lambda p: p.quality_score)
        logger.info(f"Selected best voice profile '{best_profile.name}' for language '{language}'")
        return best_profile.id
    
    def speak_multilingual(self, text: str, language: Optional[str] = None, auto_detect: bool = None) -> None:
        """
        Convert text to speech with multi-language support.
        
        Args:
            text: Text to convert to speech
            language: Specific language to use (optional)
            auto_detect: Whether to auto-detect language (optional)
            
        Raises:
            TextToSpeechError: If TTS operation fails
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for multi-language TTS")
            return
        
        if not self.is_initialized():
            raise TextToSpeechError("Multi-language TTS engine not initialized. Call initialize() first.")
        
        # Determine language to use
        target_language = self._determine_target_language(text, language, auto_detect)
        
        logger.info(f"Speaking text in language: {self.get_language_name(target_language)} ({target_language})")
        
        # Get appropriate voice profile for the language
        voice_profile_id = self.get_best_voice_profile_for_language(target_language)
        
        if not voice_profile_id:
            logger.warning(f"No voice profile available for language '{target_language}', using default")
        else:
            # Set the voice profile
            self.tts_manager.set_voice_profile(voice_profile_id)
        
        # Set the language
        self.tts_manager.set_language(target_language)
        self.current_language = target_language
        
        # Perform TTS
        self.tts_manager.speak(text)
    
    def _determine_target_language(self, text: str, explicit_language: Optional[str], auto_detect: Optional[bool]) -> str:
        """
        Determine the target language for TTS.
        
        Args:
            text: Text to analyze
            explicit_language: Explicitly specified language
            auto_detect: Whether to auto-detect language
            
        Returns:
            Target language code
        """
        # If language is explicitly specified, use it
        if explicit_language:
            if explicit_language in self.supported_languages:
                return explicit_language
            else:
                logger.warning(f"Unsupported explicit language '{explicit_language}', falling back to detection")
        
        # Determine if we should auto-detect
        should_auto_detect = (
            auto_detect if auto_detect is not None 
            else self.multilang_config.auto_detect_language
        )
        
        if should_auto_detect and self.lang_detection_available:
            detection_result = self.detect_language(text)
            
            if detection_result and detection_result.confidence >= self.multilang_config.min_confidence_threshold:
                logger.debug(f"Language detected: {detection_result.language} (confidence: {detection_result.confidence:.2f})")
                return detection_result.language
            else:
                logger.debug("Language detection failed or low confidence, using fallback")
        
        # Fallback to current language or default
        return self.current_language or self.multilang_config.fallback_language
    
    def get_language_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about language support and voice profiles.
        
        Returns:
            Dictionary with language statistics
        """
        stats = {
            "supported_languages": len(self.supported_languages),
            "current_language": self.current_language,
            "language_detection_available": self.lang_detection_available,
            "languages_with_profiles": {},
            "total_profiles": 0
        }
        
        # Count profiles per language
        for lang in self.supported_languages:
            profiles = self.get_voice_profiles_for_language(lang)
            if profiles:
                stats["languages_with_profiles"][lang] = {
                    "count": len(profiles),
                    "language_name": self.get_language_name(lang),
                    "best_quality": max(p.quality_score for p in profiles)
                }
                stats["total_profiles"] += len(profiles)
        
        return stats
    
    def cleanup(self) -> None:
        """Clean up multi-language TTS resources."""
        self.tts_manager.cleanup()
        logger.info("Multi-language TTS resources cleaned up")
