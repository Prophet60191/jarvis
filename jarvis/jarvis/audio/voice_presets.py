"""
Voice preset management for Jarvis TTS system.

This module provides a comprehensive catalog of US English voices
and handles the mapping between voice presets and TTS model configurations.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class VoicePresetManager:
    """Manages voice presets and model configurations for Jarvis TTS."""
    
    def __init__(self):
        """Initialize the voice preset manager."""
        self.voice_catalog = self._load_voice_catalog()
        
    def _load_voice_catalog(self) -> Dict[str, Any]:
        """Load the voice catalog from the JSON file."""
        try:
            # Try to load from the main directory first
            catalog_path = Path(__file__).parent.parent.parent.parent / "us_voice_catalog.json"
            
            if not catalog_path.exists():
                # Fallback to embedded catalog
                return self._get_embedded_catalog()
            
            with open(catalog_path, 'r') as f:
                catalog = json.load(f)
            
            logger.info(f"Loaded voice catalog with {len(catalog.get('single_speaker_models', []))} single-speaker and {len(catalog.get('multi_speaker_models', []))} multi-speaker voices")
            return catalog
            
        except Exception as e:
            logger.warning(f"Failed to load voice catalog: {e}, using embedded catalog")
            return self._get_embedded_catalog()
    
    def _get_embedded_catalog(self) -> Dict[str, Any]:
        """Get embedded voice catalog as fallback."""
        return {
            "single_speaker_models": [
                {
                    "id": "ljspeech_tacotron2",
                    "name": "Linda Johnson (LJSpeech)",
                    "model": "tts_models/en/ljspeech/tacotron2-DDC",
                    "gender": "female",
                    "accent": "American",
                    "age": "adult",
                    "description": "Clear, professional female voice",
                    "quality": "high",
                    "speed": "medium"
                },
                {
                    "id": "ljspeech_fastpitch",
                    "name": "Linda Johnson (FastPitch)",
                    "model": "tts_models/en/ljspeech/fast_pitch",
                    "gender": "female",
                    "accent": "American",
                    "age": "adult",
                    "description": "Clear, professional female voice (faster)",
                    "quality": "high",
                    "speed": "fast"
                },
                {
                    "id": "ljspeech_glow",
                    "name": "Linda Johnson (Glow-TTS)",
                    "model": "tts_models/en/ljspeech/glow-tts",
                    "gender": "female",
                    "accent": "American",
                    "age": "adult",
                    "description": "Clear, professional female voice (premium)",
                    "quality": "premium",
                    "speed": "medium"
                }
            ],
            "multi_speaker_models": []
        }
    
    def get_voice_config(self, preset_id: str) -> Dict[str, Any]:
        """
        Get the TTS configuration for a voice preset.
        
        Args:
            preset_id: Voice preset identifier
            
        Returns:
            Dictionary with model, speaker_id, and other configuration
        """
        # Check single speaker models
        for voice in self.voice_catalog.get("single_speaker_models", []):
            if voice["id"] == preset_id:
                return {
                    "model": voice["model"],
                    "speaker_id": None,
                    "voice_info": voice
                }
        
        # Check multi-speaker models
        for voice in self.voice_catalog.get("multi_speaker_models", []):
            if voice["id"] == preset_id:
                return {
                    "model": voice["model"],
                    "speaker_id": voice["speaker_id"],
                    "voice_info": voice
                }
        
        # Fallback to default
        logger.warning(f"Voice preset '{preset_id}' not found, using default")
        return {
            "model": "tts_models/en/ljspeech/tacotron2-DDC",
            "speaker_id": None,
            "voice_info": {
                "name": "Default Voice",
                "gender": "female",
                "description": "Default LJSpeech voice"
            }
        }
    
    def get_available_voices(self) -> Dict[str, list]:
        """
        Get all available voices organized by category.
        
        Returns:
            Dictionary with voice categories and lists
        """
        voices = {
            "single_speaker": self.voice_catalog.get("single_speaker_models", []),
            "multi_speaker": self.voice_catalog.get("multi_speaker_models", []),
            "us_male": [],
            "us_female": []
        }
        
        # Categorize multi-speaker voices by gender
        for voice in voices["multi_speaker"]:
            if voice.get("gender") == "male" and voice.get("accent") == "American":
                voices["us_male"].append(voice)
            elif voice.get("gender") == "female" and voice.get("accent") == "American":
                voices["us_female"].append(voice)
        
        return voices
    
    def get_voice_info(self, preset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a voice preset.
        
        Args:
            preset_id: Voice preset identifier
            
        Returns:
            Voice information dictionary or None if not found
        """
        config = self.get_voice_config(preset_id)
        return config.get("voice_info")
    
    def list_voice_presets(self) -> list:
        """
        Get a list of all available voice preset IDs.
        
        Returns:
            List of voice preset identifiers
        """
        presets = []
        
        # Add single speaker presets
        for voice in self.voice_catalog.get("single_speaker_models", []):
            presets.append(voice["id"])
        
        # Add multi-speaker presets
        for voice in self.voice_catalog.get("multi_speaker_models", []):
            presets.append(voice["id"])
        
        return presets
    
    def get_recommended_voices(self) -> Dict[str, str]:
        """
        Get recommended voice presets for different use cases.
        
        Returns:
            Dictionary mapping use cases to voice preset IDs
        """
        return {
            "default": "ljspeech_tacotron2",
            "fast": "ljspeech_fastpitch",
            "premium": "ljspeech_glow",
            "male_young": "vctk_p360",  # Age 19
            "male_adult": "vctk_p374",  # Age 28
            "female_young": "vctk_p301",  # Age 18
            "female_adult": "vctk_p300",  # Age 26
        }
    
    def search_voices(self, **criteria) -> list:
        """
        Search for voices matching specific criteria.
        
        Args:
            **criteria: Search criteria (gender, age_min, age_max, accent, etc.)
            
        Returns:
            List of matching voice configurations
        """
        matches = []
        all_voices = (
            self.voice_catalog.get("single_speaker_models", []) +
            self.voice_catalog.get("multi_speaker_models", [])
        )
        
        for voice in all_voices:
            match = True
            
            # Check gender
            if "gender" in criteria and voice.get("gender") != criteria["gender"]:
                match = False
            
            # Check accent
            if "accent" in criteria and voice.get("accent") != criteria["accent"]:
                match = False
            
            # Check age range
            if "age_min" in criteria:
                voice_age = voice.get("age")
                if isinstance(voice_age, int) and voice_age < criteria["age_min"]:
                    match = False
            
            if "age_max" in criteria:
                voice_age = voice.get("age")
                if isinstance(voice_age, int) and voice_age > criteria["age_max"]:
                    match = False
            
            if match:
                matches.append(voice)
        
        return matches


# Global instance
voice_preset_manager = VoicePresetManager()


def get_voice_config(preset_id: str) -> Dict[str, Any]:
    """
    Get voice configuration for a preset ID.
    
    Args:
        preset_id: Voice preset identifier
        
    Returns:
        Voice configuration dictionary
    """
    return voice_preset_manager.get_voice_config(preset_id)


def get_voice_info(preset_id: str) -> Optional[Dict[str, Any]]:
    """
    Get voice information for a preset ID.
    
    Args:
        preset_id: Voice preset identifier
        
    Returns:
        Voice information dictionary or None
    """
    return voice_preset_manager.get_voice_info(preset_id)


def list_available_voices() -> Dict[str, list]:
    """
    Get all available voices organized by category.
    
    Returns:
        Dictionary with voice categories
    """
    return voice_preset_manager.get_available_voices()
