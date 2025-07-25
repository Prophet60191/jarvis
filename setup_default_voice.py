#!/usr/bin/env python3
"""
Default Voice Setup for Jarvis Voice Assistant.

This script helps set up a default voice profile for Jarvis using Coqui TTS.
It provides options to record a new voice or use a sample voice.
"""

import sys
import os
import logging
from pathlib import Path

# Add the jarvis directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'jarvis'))

from jarvis.tools.voice_setup import VoiceSetupTool
from jarvis.audio.voice_profiles import VoiceProfileManager
from jarvis.config import JarvisConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_sample_voice_profile():
    """
    Create a sample voice profile using a built-in voice sample.
    
    This creates a basic voice profile that can be used as a starting point.
    """
    logger.info("Creating sample voice profile...")
    
    # Create a simple text-to-speech sample for demonstration
    # In a real implementation, you would use a high-quality voice sample
    sample_text = """
    Hello, I am Jarvis, your voice assistant. This is a sample voice profile 
    that demonstrates the voice cloning capabilities of the Coqui TTS system. 
    You can replace this with your own voice recording for a personalized experience.
    """
    
    try:
        # For now, we'll create a placeholder profile
        # In Phase 3, we'll implement actual voice generation
        voice_manager = VoiceProfileManager()
        
        # Check if we already have a default profile
        existing_profiles = voice_manager.list_profiles()
        default_profiles = [p for p in existing_profiles if "jarvis_default" in p.name.lower()]
        
        if default_profiles:
            logger.info(f"Default voice profile already exists: {default_profiles[0].name}")
            return default_profiles[0].id
        
        logger.info("No sample voice available yet. Please record your own voice or provide an audio file.")
        return None
        
    except Exception as e:
        logger.error(f"Failed to create sample voice profile: {e}")
        return None


def record_custom_voice():
    """Record a custom voice for Jarvis."""
    logger.info("Starting custom voice recording...")
    
    try:
        voice_tool = VoiceSetupTool()
        
        # Check if audio recording is available
        if not voice_tool.audio_available:
            logger.error("Audio recording not available. Please install required dependencies:")
            logger.error("pip install sounddevice soundfile numpy")
            return None
        
        # Get available recording devices
        devices = voice_tool.get_recording_devices()
        if not devices:
            logger.error("No audio input devices found")
            return None
        
        logger.info("Available recording devices:")
        for device in devices:
            logger.info(f"  {device['index']}: {device['name']} ({device['channels']} channels)")
        
        # Record voice
        logger.info("\n" + "="*60)
        logger.info("VOICE RECORDING INSTRUCTIONS")
        logger.info("="*60)
        logger.info("1. Speak clearly and naturally")
        logger.info("2. Record in a quiet environment")
        logger.info("3. Speak for the full 30 seconds")
        logger.info("4. Include varied sentences and emotions")
        logger.info("5. Avoid background noise")
        logger.info("="*60)
        
        input("\nPress Enter when ready to start recording...")
        
        result = voice_tool.execute(
            "record",
            name="Jarvis_Default_Voice",
            duration=30.0,
            description="Default voice profile for Jarvis assistant",
            language="en",
            gender="unknown",
            age_group="adult"
        )
        
        if result.success:
            logger.info(f"✅ Voice recording successful!")
            logger.info(f"Profile ID: {result.data['profile_id']}")
            logger.info(f"Quality Score: {result.data['quality_score']:.2f}")
            return result.data['profile_id']
        else:
            logger.error(f"❌ Voice recording failed: {result.message}")
            return None
            
    except Exception as e:
        logger.error(f"Custom voice recording failed: {e}")
        return None


def import_voice_file():
    """Import a voice file for Jarvis."""
    logger.info("Importing voice file...")
    
    try:
        voice_tool = VoiceSetupTool()
        
        # Get audio file path from user
        while True:
            audio_path = input("\nEnter path to your audio file (or 'cancel' to skip): ").strip()
            
            if audio_path.lower() == 'cancel':
                return None
            
            if not audio_path:
                continue
            
            audio_path = Path(audio_path).expanduser()
            
            if not audio_path.exists():
                logger.error(f"File not found: {audio_path}")
                continue
            
            # Validate audio file
            validation_result = voice_tool.execute("validate_audio", audio_path=str(audio_path))
            
            if not validation_result.success:
                logger.error(f"Audio validation failed: {validation_result.message}")
                continue
            
            # Show validation results
            data = validation_result.data
            logger.info(f"✅ Audio file validated successfully:")
            logger.info(f"  Duration: {data['duration']:.1f} seconds")
            logger.info(f"  Quality Score: {data['quality_score']:.2f}")
            logger.info(f"  Sample Rate: {data['sample_rate']} Hz")
            
            # Create profile
            result = voice_tool.execute(
                "create_profile",
                name="Jarvis_Default_Voice",
                audio_path=str(audio_path),
                description="Default voice profile for Jarvis assistant (imported)",
                language="en",
                gender="unknown",
                age_group="adult"
            )
            
            if result.success:
                logger.info(f"✅ Voice profile created successfully!")
                logger.info(f"Profile ID: {result.data['profile_id']}")
                return result.data['profile_id']
            else:
                logger.error(f"❌ Profile creation failed: {result.message}")
                return None
                
    except Exception as e:
        logger.error(f"Voice file import failed: {e}")
        return None


def set_default_voice_profile(profile_id: str):
    """Set a voice profile as the default for Jarvis."""
    try:
        # Update configuration to use this profile by default
        config = JarvisConfig.from_env()
        
        # Get profile info
        voice_manager = VoiceProfileManager()
        profile = voice_manager.get_profile(profile_id)
        
        if not profile:
            logger.error(f"Profile not found: {profile_id}")
            return False
        
        # Set the speaker_wav in config
        config.audio.coqui_speaker_wav = profile.audio_path
        
        logger.info(f"✅ Default voice profile set: {profile.name}")
        logger.info(f"Audio path: {profile.audio_path}")
        logger.info(f"Quality: {profile.quality_score:.2f}")
        
        # Save to environment variable suggestion
        logger.info("\n" + "="*60)
        logger.info("CONFIGURATION UPDATE")
        logger.info("="*60)
        logger.info("Add this to your .env file or environment variables:")
        logger.info(f"JARVIS_COQUI_SPEAKER_WAV={profile.audio_path}")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to set default voice profile: {e}")
        return False


def main():
    """Main setup function."""
    logger.info("🎤 Jarvis Default Voice Setup")
    logger.info("="*50)
    
    # Check existing profiles
    voice_manager = VoiceProfileManager()
    existing_profiles = voice_manager.list_profiles()
    
    if existing_profiles:
        logger.info(f"Found {len(existing_profiles)} existing voice profile(s):")
        for profile in existing_profiles:
            logger.info(f"  - {profile.name} (Quality: {profile.quality_score:.2f})")
    
    # Setup options
    logger.info("\nSetup Options:")
    logger.info("1. Record new voice (recommended)")
    logger.info("2. Import existing audio file")
    logger.info("3. Use existing profile")
    logger.info("4. Skip setup")
    
    while True:
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            profile_id = record_custom_voice()
            break
        elif choice == "2":
            profile_id = import_voice_file()
            break
        elif choice == "3":
            if not existing_profiles:
                logger.error("No existing profiles available")
                continue
            
            logger.info("Available profiles:")
            for i, profile in enumerate(existing_profiles):
                logger.info(f"  {i+1}. {profile.name} (Quality: {profile.quality_score:.2f})")
            
            try:
                selection = int(input("Select profile number: ")) - 1
                if 0 <= selection < len(existing_profiles):
                    profile_id = existing_profiles[selection].id
                    break
                else:
                    logger.error("Invalid selection")
                    continue
            except ValueError:
                logger.error("Please enter a valid number")
                continue
        elif choice == "4":
            logger.info("Setup skipped")
            return
        else:
            logger.error("Invalid choice. Please select 1-4.")
            continue
    
    # Set default profile if one was created/selected
    if profile_id:
        if set_default_voice_profile(profile_id):
            logger.info("\n🎉 Default voice setup completed successfully!")
            logger.info("You can now use Jarvis with your custom voice.")
        else:
            logger.error("Failed to set default voice profile")
    else:
        logger.info("No voice profile was set up")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nSetup cancelled by user")
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)
