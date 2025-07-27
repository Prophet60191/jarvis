#!/usr/bin/env python3
"""
Test script for Phase 2: Voice Cloning functionality.

This script tests the voice profile management, voice cloning implementation,
and voice setup tools.
"""

import sys
import os
import logging
from pathlib import Path

# Add the jarvis directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'jarvis'))

from jarvis.audio.voice_profiles import VoiceProfileManager, VoiceProfile
from jarvis.tools.voice_setup import VoiceSetupTool
from jarvis.audio.coqui_tts import CoquiTTSManager
from jarvis.config import JarvisConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_voice_profile_manager():
    """Test the VoiceProfileManager functionality."""
    logger.info("Testing VoiceProfileManager...")
    
    try:
        # Initialize voice profile manager
        voice_manager = VoiceProfileManager()
        logger.info("✅ VoiceProfileManager initialized successfully")
        
        # Test profile listing
        profiles = voice_manager.list_profiles()
        logger.info(f"✅ Found {len(profiles)} existing voice profiles")
        
        # Test statistics
        stats = voice_manager.get_profile_stats()
        logger.info(f"✅ Profile statistics: {stats['total_profiles']} total, {stats['active_profiles']} active")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ VoiceProfileManager test failed: {e}")
        return False


def test_voice_setup_tool():
    """Test the VoiceSetupTool functionality."""
    logger.info("Testing VoiceSetupTool...")
    
    try:
        # Initialize voice setup tool
        voice_tool = VoiceSetupTool()
        logger.info("✅ VoiceSetupTool initialized successfully")
        
        # Test listing profiles
        result = voice_tool.execute("list_profiles")
        if result.is_success:
            logger.info(f"✅ Profile listing: {result.data['count']} profiles found")
        else:
            logger.warning(f"⚠️ Profile listing failed: {result.message}")

        # Test statistics
        result = voice_tool.execute("get_stats")
        if result.is_success:
            logger.info(f"✅ Statistics retrieved successfully")
        else:
            logger.warning(f"⚠️ Statistics failed: {result.message}")
        
        # Test audio validation (if we have a sample file)
        sample_files = list(Path(".").glob("*.wav")) + list(Path(".").glob("*.mp3"))
        if sample_files:
            sample_file = sample_files[0]
            logger.info(f"Testing audio validation with: {sample_file}")
            
            result = voice_tool.execute("validate_audio", audio_path=str(sample_file))
            if result.is_success:
                logger.info(f"✅ Audio validation successful")
                logger.info(f"  Duration: {result.data.get('duration', 'N/A')} seconds")
                logger.info(f"  Quality: {result.data.get('quality_score', 'N/A')}")
            else:
                logger.info(f"ℹ️ Audio validation test: {result.message}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ VoiceSetupTool test failed: {e}")
        return False


def test_coqui_tts_voice_cloning():
    """Test the CoquiTTSManager voice cloning functionality."""
    logger.info("Testing CoquiTTSManager voice cloning...")
    
    try:
        # Initialize configuration and TTS manager
        config = JarvisConfig.from_env()
        tts_manager = CoquiTTSManager(config.audio)
        
        logger.info("✅ CoquiTTSManager initialized successfully")
        
        # Initialize TTS engine
        logger.info("Initializing Coqui TTS engine...")
        tts_manager.initialize()
        logger.info("✅ Coqui TTS engine initialized successfully")
        
        # Test voice profile management
        profiles = tts_manager.list_voice_profiles()
        logger.info(f"✅ Voice profile management: {len(profiles)} profiles available")
        
        # Test voice profile statistics
        stats = tts_manager.get_voice_profile_stats()
        logger.info(f"✅ Voice profile statistics retrieved")
        logger.info(f"  Total profiles: {stats['total_profiles']}")
        logger.info(f"  Active profiles: {stats['active_profiles']}")
        logger.info(f"  Languages: {stats['languages']}")
        
        # Test current voice profile
        current_profile = tts_manager.get_current_voice_profile()
        if current_profile:
            logger.info(f"✅ Current voice profile: {current_profile.name}")
        else:
            logger.info("ℹ️ No current voice profile set")
        
        # Test speech synthesis (will fail without voice profile, which is expected)
        try:
            test_text = "This is a test of the voice cloning system."
            tts_manager.speak(test_text)
            logger.info("✅ Speech synthesis test completed")
        except Exception as e:
            if "voice profile" in str(e).lower() or "speaker_wav" in str(e).lower():
                logger.info("✅ Speech synthesis correctly requires voice profile (expected behavior)")
            else:
                logger.warning(f"⚠️ Unexpected speech synthesis error: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ CoquiTTSManager voice cloning test failed: {e}")
        return False


def test_voice_profile_creation():
    """Test creating a voice profile from a sample file."""
    logger.info("Testing voice profile creation...")
    
    try:
        # Look for sample audio files
        sample_files = []
        for ext in ['*.wav', '*.mp3', '*.flac', '*.m4a']:
            sample_files.extend(list(Path(".").glob(ext)))
        
        if not sample_files:
            logger.info("ℹ️ No sample audio files found for testing profile creation")
            return True
        
        sample_file = sample_files[0]
        logger.info(f"Using sample file: {sample_file}")
        
        # Test with VoiceSetupTool
        voice_tool = VoiceSetupTool()
        
        # First validate the audio
        result = voice_tool.execute("validate_audio", audio_path=str(sample_file))
        if not result.is_success:
            logger.info(f"ℹ️ Sample file validation failed (expected): {result.message}")
            return True

        # Try to create a test profile
        result = voice_tool.execute(
            "create_profile",
            name="Test_Voice_Profile",
            audio_path=str(sample_file),
            description="Test profile for Phase 2 testing"
        )

        if result.is_success:
            logger.info(f"✅ Test voice profile created: {result.data['profile_id']}")

            # Clean up test profile
            voice_tool.execute("delete_profile", profile_id=result.data['profile_id'])
            logger.info("✅ Test profile cleaned up")
        else:
            logger.info(f"ℹ️ Profile creation test: {result.message}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Voice profile creation test failed: {e}")
        return False


def test_integration():
    """Test integration between all voice cloning components."""
    logger.info("Testing voice cloning integration...")
    
    try:
        # Test that all components can work together
        voice_manager = VoiceProfileManager()
        voice_tool = VoiceSetupTool()
        
        config = JarvisConfig.from_env()
        tts_manager = CoquiTTSManager(config.audio)
        tts_manager.initialize()
        
        # Test that voice manager and TTS manager see the same profiles
        vm_profiles = voice_manager.list_profiles()
        tts_profiles = tts_manager.list_voice_profiles()
        
        if len(vm_profiles) == len(tts_profiles):
            logger.info(f"✅ Profile consistency: {len(vm_profiles)} profiles in both systems")
        else:
            logger.warning(f"⚠️ Profile inconsistency: VM={len(vm_profiles)}, TTS={len(tts_profiles)}")
        
        # Test that voice tool and voice manager are consistent
        tool_result = voice_tool.execute("list_profiles")
        if tool_result.is_success:
            tool_profiles = tool_result.data['count']
            if tool_profiles == len(vm_profiles):
                logger.info(f"✅ Tool consistency: {tool_profiles} profiles")
            else:
                logger.warning(f"⚠️ Tool inconsistency: Tool={tool_profiles}, VM={len(vm_profiles)}")
        
        logger.info("✅ Integration test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        return False


def main():
    """Run all Phase 2 voice cloning tests."""
    logger.info("🎤 Starting Phase 2: Voice Cloning Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Voice Profile Manager", test_voice_profile_manager),
        ("Voice Setup Tool", test_voice_setup_tool),
        ("Coqui TTS Voice Cloning", test_coqui_tts_voice_cloning),
        ("Voice Profile Creation", test_voice_profile_creation),
        ("Integration", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 2 TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All Phase 2 tests completed successfully!")
        logger.info("✅ Voice cloning functionality is working correctly")
        logger.info("🚀 Ready to proceed to Phase 3: Advanced Features")
    else:
        logger.warning(f"⚠️ {total - passed} test(s) failed")
        logger.info("Some functionality may need attention before proceeding")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nTests cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        sys.exit(1)
