"""
Voice Setup Tool for Jarvis Voice Assistant.

This tool provides functionality to record voice samples, create voice profiles,
and manage voice cloning for the Coqui TTS system.
"""

import os
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

try:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
except ImportError:
    sd = None
    sf = None
    np = None

from ..audio.voice_profiles import VoiceProfileManager, VoiceProfile
from ..exceptions import TextToSpeechError
from .base import BaseTool, ToolResult, ToolStatus


logger = logging.getLogger(__name__)


@dataclass
class RecordingConfig:
    """Configuration for voice recording."""
    sample_rate: int = 22050  # XTTS-v2 uses 22050 Hz
    channels: int = 1  # Mono
    duration: float = 30.0  # Default 30 seconds
    device: Optional[int] = None  # Auto-detect
    format: str = 'wav'


class VoiceSetupTool(BaseTool):
    """
    Tool for setting up voice cloning profiles.
    
    This tool provides functionality to:
    - Record voice samples
    - Create voice profiles from audio files
    - Manage existing voice profiles
    - Test voice cloning
    """
    
    def __init__(self):
        """Initialize the voice setup tool."""
        super().__init__(
            name="voice_setup",
            description="Set up voice cloning profiles for Coqui TTS"
        )
        self.voice_manager = VoiceProfileManager()
        self.recording_config = RecordingConfig()
        
        # Check audio dependencies
        self.audio_available = sd is not None and sf is not None and np is not None
        if not self.audio_available:
            logger.warning("Audio recording dependencies not available. Install sounddevice, soundfile, and numpy.")

    def _success_result(self, message: str, data: Any = None) -> ToolResult:
        """Create a success ToolResult."""
        return ToolResult(status=ToolStatus.SUCCESS, message=message, data=data)

    def _error_result(self, message: str, data: Any = None, error: Exception = None) -> ToolResult:
        """Create an error ToolResult."""
        return ToolResult(status=ToolStatus.ERROR, message=message, data=data, error=error)

    def get_parameters(self) -> Dict[str, Any]:
        """
        Get tool parameter schema.

        Returns:
            Dictionary describing tool parameters
        """
        return {
            "action": {
                "type": "string",
                "description": "Action to perform",
                "required": True,
                "options": ["record", "create_profile", "list_profiles", "delete_profile", "test_voice", "import_audio", "get_stats", "validate_audio"]
            },
            "name": {
                "type": "string",
                "description": "Name for voice profile",
                "required": False
            },
            "audio_path": {
                "type": "string",
                "description": "Path to audio file",
                "required": False
            },
            "duration": {
                "type": "number",
                "description": "Recording duration in seconds",
                "required": False,
                "default": 30.0
            },
            "description": {
                "type": "string",
                "description": "Description of the voice",
                "required": False,
                "default": ""
            },
            "language": {
                "type": "string",
                "description": "Language code",
                "required": False,
                "default": "en"
            },
            "gender": {
                "type": "string",
                "description": "Gender of the voice",
                "required": False,
                "default": "unknown"
            },
            "age_group": {
                "type": "string",
                "description": "Age group of the voice",
                "required": False,
                "default": "unknown"
            },
            "profile_id": {
                "type": "string",
                "description": "Voice profile ID",
                "required": False
            },
            "test_text": {
                "type": "string",
                "description": "Text to use for voice testing",
                "required": False,
                "default": "Hello, this is a test of my cloned voice."
            },
            "active_only": {
                "type": "boolean",
                "description": "List only active profiles",
                "required": False,
                "default": True
            }
        }
    
    def execute(self, action: str, **kwargs) -> ToolResult:
        """
        Execute voice setup actions.
        
        Args:
            action: Action to perform ('record', 'create_profile', 'list_profiles', 
                   'delete_profile', 'test_voice', 'import_audio')
            **kwargs: Action-specific parameters
            
        Returns:
            ToolResult with operation results
        """
        try:
            if action == "record":
                return self._record_voice(**kwargs)
            elif action == "create_profile":
                return self._create_profile(**kwargs)
            elif action == "list_profiles":
                return self._list_profiles(**kwargs)
            elif action == "delete_profile":
                return self._delete_profile(**kwargs)
            elif action == "test_voice":
                return self._test_voice(**kwargs)
            elif action == "import_audio":
                return self._import_audio(**kwargs)
            elif action == "get_stats":
                return self._get_stats()
            elif action == "validate_audio":
                return self._validate_audio(**kwargs)
            else:
                return self._error_result(
                    f"Unknown action: {action}",
                    data={"available_actions": ["record", "create_profile", "list_profiles", "delete_profile", "test_voice", "import_audio", "get_stats", "validate_audio"]}
                )
                
        except Exception as e:
            logger.error(f"Voice setup tool error: {e}")
            return self._error_result(f"Voice setup failed: {str(e)}", data={"error": str(e)}, error=e)
    
    def _record_voice(
        self,
        name: str,
        duration: float = 30.0,
        output_path: Optional[str] = None,
        description: str = "",
        language: str = "en",
        gender: str = "unknown",
        age_group: str = "unknown"
    ) -> ToolResult:
        """
        Record a voice sample for voice cloning.
        
        Args:
            name: Name for the voice profile
            duration: Recording duration in seconds
            output_path: Optional output path for the recording
            description: Description of the voice
            language: Language of the voice
            gender: Gender of the voice
            age_group: Age group of the voice
            
        Returns:
            ToolResult with recording results
        """
        if not self.audio_available:
            return ToolResult(
                success=False,
                message="Audio recording not available. Please install sounddevice, soundfile, and numpy.",
                data={"missing_dependencies": ["sounddevice", "soundfile", "numpy"]}
            )
        
        try:
            # Prepare recording
            if not output_path:
                output_path = f"temp_recording_{name}_{int(time.time())}.wav"
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Starting voice recording for '{name}' ({duration} seconds)")
            
            # Get available audio devices
            devices = sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]
            
            if not input_devices:
                return ToolResult(
                    success=False,
                    message="No audio input devices found",
                    data={"devices": devices}
                )
            
            # Use default input device
            device_info = sd.query_devices(kind='input')
            logger.info(f"Using audio device: {device_info['name']}")
            
            # Record audio
            logger.info("Recording started... Please speak clearly.")
            recording = sd.rec(
                int(duration * self.recording_config.sample_rate),
                samplerate=self.recording_config.sample_rate,
                channels=self.recording_config.channels,
                dtype='float32'
            )
            
            # Wait for recording to complete
            sd.wait()
            
            # Save recording
            sf.write(str(output_path), recording, self.recording_config.sample_rate)
            
            logger.info(f"Recording completed and saved to: {output_path}")
            
            # Validate the recording
            validation_result = self.voice_manager.validate_audio_file(str(output_path))
            
            # Create voice profile automatically
            try:
                profile_id = self.voice_manager.create_profile(
                    name=name,
                    audio_path=str(output_path),
                    description=description or f"Recorded voice profile for {name}",
                    language=language,
                    gender=gender,
                    age_group=age_group
                )
                
                # Clean up temporary file if profile was created successfully
                if output_path.name.startswith("temp_recording_"):
                    output_path.unlink()
                
                return ToolResult(
                    success=True,
                    message=f"Voice profile '{name}' created successfully from recording",
                    data={
                        "profile_id": profile_id,
                        "name": name,
                        "duration": validation_result["duration"],
                        "quality_score": validation_result["quality_score"],
                        "sample_rate": validation_result["sample_rate"]
                    }
                )
                
            except Exception as e:
                logger.error(f"Failed to create profile from recording: {e}")
                return ToolResult(
                    success=True,
                    message=f"Recording completed but profile creation failed: {str(e)}",
                    data={
                        "recording_path": str(output_path),
                        "validation": validation_result,
                        "error": str(e)
                    }
                )
                
        except Exception as e:
            logger.error(f"Recording failed: {e}")
            return ToolResult(
                success=False,
                message=f"Recording failed: {str(e)}",
                data={"error": str(e)}
            )
    
    def _create_profile(
        self,
        name: str,
        audio_path: str,
        description: str = "",
        language: str = "en",
        gender: str = "unknown",
        age_group: str = "unknown"
    ) -> ToolResult:
        """
        Create a voice profile from an existing audio file.
        
        Args:
            name: Name for the voice profile
            audio_path: Path to the audio file
            description: Description of the voice
            language: Language of the voice
            gender: Gender of the voice
            age_group: Age group of the voice
            
        Returns:
            ToolResult with profile creation results
        """
        try:
            # Validate audio file first
            validation_result = self.voice_manager.validate_audio_file(audio_path)
            
            # Create profile
            profile_id = self.voice_manager.create_profile(
                name=name,
                audio_path=audio_path,
                description=description,
                language=language,
                gender=gender,
                age_group=age_group
            )
            
            profile = self.voice_manager.get_profile(profile_id)
            
            return ToolResult(
                success=True,
                message=f"Voice profile '{name}' created successfully",
                data={
                    "profile_id": profile_id,
                    "name": name,
                    "duration": profile.duration,
                    "quality_score": profile.quality_score,
                    "language": profile.language,
                    "created_at": profile.created_at
                }
            )
            
        except Exception as e:
            logger.error(f"Profile creation failed: {e}")
            return ToolResult(
                success=False,
                message=f"Failed to create voice profile: {str(e)}",
                data={"error": str(e)}
            )
    
    def _list_profiles(self, active_only: bool = True) -> ToolResult:
        """
        List all voice profiles.
        
        Args:
            active_only: Whether to list only active profiles
            
        Returns:
            ToolResult with profile list
        """
        try:
            if active_only:
                profiles = self.voice_manager.get_active_profiles()
            else:
                profiles = self.voice_manager.list_profiles()
            
            profile_data = []
            for profile in profiles:
                profile_data.append({
                    "id": profile.id,
                    "name": profile.name,
                    "description": profile.description,
                    "language": profile.language,
                    "gender": profile.gender,
                    "age_group": profile.age_group,
                    "duration": profile.duration,
                    "quality_score": profile.quality_score,
                    "created_at": profile.created_at,
                    "is_active": profile.is_active
                })
            
            return self._success_result(
                f"Found {len(profiles)} voice profile(s)",
                data={
                    "profiles": profile_data,
                    "count": len(profiles)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to list profiles: {e}")
            return self._error_result(f"Failed to list voice profiles: {str(e)}", data={"error": str(e)}, error=e)

    def _delete_profile(self, profile_id: str) -> ToolResult:
        """Delete a voice profile."""
        try:
            profile = self.voice_manager.get_profile(profile_id)
            if not profile:
                return ToolResult(
                    success=False,
                    message=f"Voice profile not found: {profile_id}",
                    data={"profile_id": profile_id}
                )

            profile_name = profile.name
            success = self.voice_manager.delete_profile(profile_id)

            if success:
                return ToolResult(
                    success=True,
                    message=f"Voice profile '{profile_name}' deleted successfully",
                    data={"profile_id": profile_id, "name": profile_name}
                )
            else:
                return ToolResult(
                    success=False,
                    message=f"Failed to delete voice profile '{profile_name}'",
                    data={"profile_id": profile_id, "name": profile_name}
                )

        except Exception as e:
            logger.error(f"Profile deletion failed: {e}")
            return ToolResult(
                success=False,
                message=f"Failed to delete voice profile: {str(e)}",
                data={"error": str(e)}
            )

    def _test_voice(self, profile_id: str, test_text: str = "Hello, this is a test of my cloned voice.") -> ToolResult:
        """Test a voice profile by generating speech."""
        try:
            profile = self.voice_manager.get_profile(profile_id)
            if not profile:
                return ToolResult(
                    success=False,
                    message=f"Voice profile not found: {profile_id}",
                    data={"profile_id": profile_id}
                )

            return ToolResult(
                success=True,
                message=f"Voice profile '{profile.name}' is ready for testing",
                data={
                    "profile_id": profile_id,
                    "profile_name": profile.name,
                    "test_text": test_text,
                    "quality_score": profile.quality_score,
                    "note": "Use TTS manager to actually test the voice"
                }
            )

        except Exception as e:
            logger.error(f"Voice test failed: {e}")
            return ToolResult(
                success=False,
                message=f"Voice test failed: {str(e)}",
                data={"error": str(e)}
            )

    def _import_audio(self, audio_path: str, name: Optional[str] = None, **kwargs) -> ToolResult:
        """Import an audio file and create a voice profile."""
        try:
            audio_path = Path(audio_path)

            if not audio_path.exists():
                return ToolResult(
                    success=False,
                    message=f"Audio file not found: {audio_path}",
                    data={"audio_path": str(audio_path)}
                )

            # Generate name if not provided
            if not name:
                name = f"Imported_{audio_path.stem}"

            # Create profile
            return self._create_profile(name=name, audio_path=str(audio_path), **kwargs)

        except Exception as e:
            logger.error(f"Audio import failed: {e}")
            return ToolResult(
                success=False,
                message=f"Failed to import audio: {str(e)}",
                data={"error": str(e)}
            )

    def _get_stats(self) -> ToolResult:
        """Get statistics about voice profiles."""
        try:
            stats = self.voice_manager.get_profile_stats()
            return self._success_result("Voice profile statistics retrieved", data=stats)
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return ToolResult(
                success=False,
                message=f"Failed to get statistics: {str(e)}",
                data={"error": str(e)}
            )

    def _validate_audio(self, audio_path: str) -> ToolResult:
        """Validate an audio file for voice cloning."""
        try:
            validation_result = self.voice_manager.validate_audio_file(audio_path)
            return ToolResult(
                success=True,
                message="Audio file validation completed",
                data=validation_result
            )
        except Exception as e:
            logger.error(f"Audio validation failed: {e}")
            return ToolResult(
                success=False,
                message=f"Audio validation failed: {str(e)}",
                data={"error": str(e)}
            )
