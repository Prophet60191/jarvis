"""
Voice Profile Management for Coqui TTS Voice Cloning.

This module handles voice profile creation, validation, storage, and management
for the Jarvis voice assistant's voice cloning capabilities.
"""

import os
import json
import logging
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    import librosa
    import soundfile as sf
    import numpy as np
except ImportError:
    librosa = None
    sf = None
    np = None

from ..exceptions import TextToSpeechError
from .voice_enhancement import VoiceEnhancementProcessor, EnhancementConfig


logger = logging.getLogger(__name__)


@dataclass
class VoiceProfile:
    """Represents a voice profile for voice cloning."""
    
    id: str
    name: str
    description: str
    audio_path: str
    created_at: str
    sample_rate: int
    duration: float
    quality_score: float
    language: str = "en"
    gender: str = "unknown"
    age_group: str = "unknown"
    is_active: bool = True
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class VoiceProfileManager:
    """
    Manages voice profiles for Coqui TTS voice cloning.
    
    This class handles voice profile creation, validation, storage,
    and management operations.
    """
    
    def __init__(self, profiles_dir: str = "voices"):
        """
        Initialize the voice profile manager.
        
        Args:
            profiles_dir: Directory to store voice profiles
        """
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.audio_dir = self.profiles_dir / "audio"
        self.metadata_dir = self.profiles_dir / "metadata"
        self.audio_dir.mkdir(exist_ok=True)
        self.metadata_dir.mkdir(exist_ok=True)
        
        self.profiles_file = self.profiles_dir / "profiles.json"
        self._profiles: Dict[str, VoiceProfile] = {}
        
        # Audio validation settings
        self.min_duration = 10.0  # Minimum 10 seconds
        self.max_duration = 120.0  # Maximum 2 minutes
        self.target_sample_rate = 22050  # XTTS-v2 uses 22050 Hz
        self.supported_formats = {'.wav', '.mp3', '.flac', '.m4a', '.ogg'}

        # Voice enhancement processor
        self.voice_enhancer = VoiceEnhancementProcessor()

        logger.info(f"VoiceProfileManager initialized with profiles directory: {self.profiles_dir}")
        self._load_profiles()
    
    def _load_profiles(self) -> None:
        """Load existing voice profiles from storage."""
        try:
            if self.profiles_file.exists():
                with open(self.profiles_file, 'r') as f:
                    profiles_data = json.load(f)
                
                for profile_id, profile_data in profiles_data.items():
                    self._profiles[profile_id] = VoiceProfile(**profile_data)
                
                logger.info(f"Loaded {len(self._profiles)} voice profiles")
            else:
                logger.info("No existing voice profiles found")
                
        except Exception as e:
            logger.error(f"Failed to load voice profiles: {e}")
            self._profiles = {}
    
    def _save_profiles(self) -> None:
        """Save voice profiles to storage."""
        try:
            profiles_data = {
                profile_id: asdict(profile) 
                for profile_id, profile in self._profiles.items()
            }
            
            with open(self.profiles_file, 'w') as f:
                json.dump(profiles_data, f, indent=2)
                
            logger.debug("Voice profiles saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save voice profiles: {e}")
            raise TextToSpeechError(f"Failed to save voice profiles: {e}")
    
    def validate_audio_file(self, audio_path: str) -> Dict[str, Any]:
        """
        Validate an audio file for voice cloning.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary with validation results and audio metadata
            
        Raises:
            TextToSpeechError: If validation fails
        """
        if not librosa or not sf:
            raise TextToSpeechError("Audio processing libraries not available. Install librosa and soundfile.")
        
        audio_path = Path(audio_path)
        
        # Check file exists
        if not audio_path.exists():
            raise TextToSpeechError(f"Audio file not found: {audio_path}")
        
        # Check file format
        if audio_path.suffix.lower() not in self.supported_formats:
            raise TextToSpeechError(
                f"Unsupported audio format: {audio_path.suffix}. "
                f"Supported formats: {', '.join(self.supported_formats)}"
            )
        
        try:
            # Load audio file
            audio, sample_rate = librosa.load(str(audio_path), sr=None)
            duration = len(audio) / sample_rate
            
            # Validate duration
            if duration < self.min_duration:
                raise TextToSpeechError(
                    f"Audio too short: {duration:.1f}s. Minimum required: {self.min_duration}s"
                )
            
            if duration > self.max_duration:
                raise TextToSpeechError(
                    f"Audio too long: {duration:.1f}s. Maximum allowed: {self.max_duration}s"
                )
            
            # Calculate quality metrics
            quality_score = self._calculate_quality_score(audio, sample_rate)
            
            # Audio analysis
            rms_energy = np.sqrt(np.mean(audio**2))
            zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(audio))
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(audio, sr=sample_rate))
            
            validation_result = {
                "valid": True,
                "duration": duration,
                "sample_rate": sample_rate,
                "quality_score": quality_score,
                "rms_energy": float(rms_energy),
                "zero_crossing_rate": float(zero_crossing_rate),
                "spectral_centroid": float(spectral_centroid),
                "file_size": audio_path.stat().st_size,
                "channels": 1 if audio.ndim == 1 else audio.shape[0]
            }
            
            logger.info(f"Audio validation successful: {audio_path.name} ({duration:.1f}s, quality: {quality_score:.2f})")
            return validation_result
            
        except Exception as e:
            if isinstance(e, TextToSpeechError):
                raise
            else:
                raise TextToSpeechError(f"Audio validation failed: {str(e)}")
    
    def _calculate_quality_score(self, audio: np.ndarray, sample_rate: int) -> float:
        """
        Calculate a quality score for the audio (0.0 to 1.0).

        Args:
            audio: Audio waveform
            sample_rate: Sample rate

        Returns:
            Quality score between 0.0 and 1.0
        """
        try:
            # Use voice enhancement processor for comprehensive quality analysis
            quality_metrics = self.voice_enhancer.analyze_voice_quality(audio, sample_rate)
            return quality_metrics.quality_score

        except Exception as e:
            logger.warning(f"Quality score calculation failed: {e}")
            return 0.5  # Default moderate quality
    
    def create_profile(
        self,
        name: str,
        audio_path: str,
        description: str = "",
        language: str = "en",
        gender: str = "unknown",
        age_group: str = "unknown"
    ) -> str:
        """
        Create a new voice profile from an audio file.
        
        Args:
            name: Human-readable name for the profile
            audio_path: Path to the source audio file
            description: Optional description
            language: Language of the voice
            gender: Gender of the voice
            age_group: Age group of the voice
            
        Returns:
            Profile ID of the created profile
            
        Raises:
            TextToSpeechError: If profile creation fails
        """
        try:
            # Validate audio file
            validation_result = self.validate_audio_file(audio_path)
            
            # Generate unique profile ID
            profile_id = self._generate_profile_id(name, audio_path)
            
            # Check if profile already exists
            if profile_id in self._profiles:
                raise TextToSpeechError(f"Voice profile '{name}' already exists")
            
            # Copy and process audio file
            processed_audio_path = self._process_audio_file(audio_path, profile_id)
            
            # Create profile
            profile = VoiceProfile(
                id=profile_id,
                name=name,
                description=description,
                audio_path=str(processed_audio_path),
                created_at=datetime.now().isoformat(),
                sample_rate=validation_result["sample_rate"],
                duration=validation_result["duration"],
                quality_score=validation_result["quality_score"],
                language=language,
                gender=gender,
                age_group=age_group,
                metadata={
                    "source_file": str(audio_path),
                    "rms_energy": validation_result["rms_energy"],
                    "zero_crossing_rate": validation_result["zero_crossing_rate"],
                    "spectral_centroid": validation_result["spectral_centroid"],
                    "file_size": validation_result["file_size"]
                }
            )
            
            # Store profile
            self._profiles[profile_id] = profile
            self._save_profiles()
            
            logger.info(f"Voice profile created successfully: {name} (ID: {profile_id})")
            return profile_id
            
        except Exception as e:
            if isinstance(e, TextToSpeechError):
                raise
            else:
                raise TextToSpeechError(f"Failed to create voice profile: {str(e)}")
    
    def _generate_profile_id(self, name: str, audio_path: str) -> str:
        """Generate a unique profile ID."""
        # Create hash from name and file content
        content = f"{name}_{Path(audio_path).name}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _process_audio_file(self, source_path: str, profile_id: str) -> Path:
        """
        Process and store audio file for voice cloning.
        
        Args:
            source_path: Source audio file path
            profile_id: Profile ID
            
        Returns:
            Path to processed audio file
        """
        if not librosa or not sf:
            # Fallback: just copy the file
            source_path = Path(source_path)
            target_path = self.audio_dir / f"{profile_id}.wav"
            shutil.copy2(source_path, target_path)
            return target_path
        
        try:
            # Load audio
            audio, sample_rate = librosa.load(str(source_path), sr=self.target_sample_rate)

            # Apply voice enhancement
            enhanced_audio, enhanced_sample_rate = self.voice_enhancer.enhance_voice_audio(audio, sample_rate)

            # Save processed audio
            target_path = self.audio_dir / f"{profile_id}.wav"
            sf.write(str(target_path), enhanced_audio, enhanced_sample_rate)

            logger.debug(f"Audio processed with enhancement and saved: {target_path}")
            return target_path
            
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            # Fallback: copy original file
            source_path = Path(source_path)
            target_path = self.audio_dir / f"{profile_id}{source_path.suffix}"
            shutil.copy2(source_path, target_path)
            return target_path

    def get_profile(self, profile_id: str) -> Optional[VoiceProfile]:
        """Get a voice profile by ID."""
        return self._profiles.get(profile_id)

    def get_profile_by_name(self, name: str) -> Optional[VoiceProfile]:
        """Get a voice profile by name."""
        for profile in self._profiles.values():
            if profile.name.lower() == name.lower():
                return profile
        return None

    def list_profiles(self) -> List[VoiceProfile]:
        """Get all voice profiles."""
        return list(self._profiles.values())

    def delete_profile(self, profile_id: str) -> bool:
        """Delete a voice profile."""
        try:
            if profile_id not in self._profiles:
                return False

            profile = self._profiles[profile_id]

            # Delete audio file
            audio_path = Path(profile.audio_path)
            if audio_path.exists():
                audio_path.unlink()

            # Remove from profiles
            del self._profiles[profile_id]
            self._save_profiles()

            logger.info(f"Voice profile deleted: {profile.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete voice profile: {e}")
            return False

    def get_active_profiles(self) -> List[VoiceProfile]:
        """Get all active voice profiles."""
        return [profile for profile in self._profiles.values() if profile.is_active]

    def get_best_quality_profile(self) -> Optional[VoiceProfile]:
        """Get the voice profile with the highest quality score."""
        active_profiles = self.get_active_profiles()
        if not active_profiles:
            return None
        return max(active_profiles, key=lambda p: p.quality_score)

    def get_profiles_by_language(self, language: str) -> List[VoiceProfile]:
        """
        Get voice profiles by language.

        Args:
            language: Language code

        Returns:
            List of profiles for the specified language
        """
        return [
            profile for profile in self._profiles.values()
            if profile.language.lower() == language.lower() and profile.is_active
        ]

    def get_profile_stats(self) -> Dict[str, Any]:
        """
        Get statistics about voice profiles.

        Returns:
            Dictionary with profile statistics
        """
        profiles = list(self._profiles.values())
        active_profiles = [p for p in profiles if p.is_active]

        if not profiles:
            return {
                "total_profiles": 0,
                "active_profiles": 0,
                "languages": [],
                "average_quality": 0.0,
                "total_duration": 0.0
            }

        languages = list(set(p.language for p in active_profiles))
        average_quality = sum(p.quality_score for p in active_profiles) / len(active_profiles) if active_profiles else 0.0
        total_duration = sum(p.duration for p in active_profiles)

        return {
            "total_profiles": len(profiles),
            "active_profiles": len(active_profiles),
            "languages": languages,
            "average_quality": average_quality,
            "total_duration": total_duration,
            "best_quality": max(p.quality_score for p in active_profiles) if active_profiles else 0.0,
            "storage_used": sum(Path(p.audio_path).stat().st_size for p in profiles if Path(p.audio_path).exists())
        }
