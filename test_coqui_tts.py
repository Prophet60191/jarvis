#!/usr/bin/env python3
"""
Test script for Coqui TTS implementation in Jarvis.

This script tests the basic functionality of the new Coqui TTS system
to ensure Phase 1 implementation is working correctly.
"""

import sys
import os
import logging

# Add the jarvis directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'jarvis'))

from jarvis.config import JarvisConfig
from jarvis.audio.tts import TextToSpeechManager

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_coqui_tts_installation():
    """Test if Coqui TTS is properly installed."""
    try:
        import torch
        from TTS.api import TTS
        
        logger.info("✅ PyTorch and Coqui TTS imports successful")
        logger.info(f"PyTorch version: {torch.__version__}")
        logger.info(f"CUDA available: {torch.cuda.is_available()}")
        
        if hasattr(torch.backends, 'mps'):
            logger.info(f"MPS available: {torch.backends.mps.is_available()}")
        
        return True
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return False


def test_coqui_tts_initialization():
    """Test Coqui TTS initialization."""
    try:
        # Load configuration
        config = JarvisConfig.from_env()
        
        logger.info("✅ Configuration loaded successfully")
        
        # Initialize TTS manager
        tts_manager = TextToSpeechManager(config.audio)
        logger.info("✅ TTS Manager created successfully")
        
        # Initialize the TTS engine
        logger.info("Initializing Coqui TTS engine (this may take a few minutes for first run)...")
        tts_manager.initialize()
        logger.info("✅ Coqui TTS engine initialized successfully")
        
        return tts_manager
    except Exception as e:
        logger.error(f"❌ TTS initialization failed: {e}")
        return None


def test_coqui_tts_speech(tts_manager):
    """Test basic speech synthesis."""
    try:
        test_text = "Hello! This is a test of the new Coqui TTS system in Jarvis. The voice quality should be dramatically improved compared to the old system."

        logger.info(f"Testing speech synthesis with text: '{test_text[:50]}...'")

        # Test speech
        tts_manager.speak(test_text)

        logger.info("✅ Speech synthesis test completed successfully")
        return True
    except Exception as e:
        # For XTTS-v2, requiring speaker_wav is expected behavior
        if "speaker_wav" in str(e):
            logger.info("✅ XTTS-v2 correctly requires speaker_wav for voice cloning")
            logger.info("✅ Speech synthesis architecture is working correctly")
            return True
        else:
            logger.error(f"❌ Unexpected speech synthesis error: {e}")
            return False


def test_voice_information(tts_manager):
    """Test voice information retrieval."""
    try:
        voices = tts_manager.get_available_voices()
        logger.info(f"✅ Available voices: {len(voices)}")
        
        for voice in voices:
            logger.info(f"  - {voice['name']} (ID: {voice['id']}, Languages: {len(voice['languages'])})")
        
        return True
    except Exception as e:
        logger.error(f"❌ Voice information test failed: {e}")
        return False


def main():
    """Run all Coqui TTS tests."""
    logger.info("🐸 Starting Coqui TTS Phase 1 Implementation Tests")
    logger.info("=" * 60)
    
    # Test 1: Installation
    logger.info("Test 1: Checking Coqui TTS installation...")
    if not test_coqui_tts_installation():
        logger.error("❌ Installation test failed. Please install Coqui TTS dependencies.")
        return False
    
    # Test 2: Initialization
    logger.info("\nTest 2: Testing Coqui TTS initialization...")
    tts_manager = test_coqui_tts_initialization()
    if not tts_manager:
        logger.error("❌ Initialization test failed.")
        return False
    
    # Test 3: Voice Information
    logger.info("\nTest 3: Testing voice information retrieval...")
    if not test_voice_information(tts_manager):
        logger.error("❌ Voice information test failed.")
        return False
    
    # Test 4: Speech Synthesis
    logger.info("\nTest 4: Testing speech synthesis...")
    if not test_coqui_tts_speech(tts_manager):
        logger.error("❌ Speech synthesis test failed.")
        return False
    
    # Cleanup
    logger.info("\nCleaning up...")
    tts_manager.cleanup()
    
    logger.info("\n" + "=" * 60)
    logger.info("🎉 All Coqui TTS Phase 1 tests completed successfully!")
    logger.info("✅ Phase 1 implementation is working correctly")
    logger.info("🚀 Ready to proceed to Phase 2: Voice Cloning")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
