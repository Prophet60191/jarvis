"""
Integration tests for Jarvis speech system.

This module tests the integration between speech recognition,
text-to-speech, and audio processing components.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time

from jarvis.core.speech import SpeechManager
from jarvis.audio import MicrophoneManager, TextToSpeechManager, AudioProcessor
from jarvis.config import AudioConfig
from jarvis.exceptions import AudioError, SpeechRecognitionError, TextToSpeechError


class TestSpeechManagerIntegration:
    """Test SpeechManager integration with audio components."""
    
    @pytest.fixture
    def speech_manager(self, audio_config):
        """Create speech manager for testing."""
        return SpeechManager(audio_config)
    
    @patch('jarvis.audio.microphone.sr')
    @patch('jarvis.audio.tts.pyttsx3')
    def test_speech_manager_initialization(self, mock_pyttsx3, mock_sr, speech_manager):
        """Test speech manager initialization."""
        # Mock speech recognition
        mock_recognizer = Mock()
        mock_microphone = Mock()
        mock_sr.Recognizer.return_value = mock_recognizer
        mock_sr.Microphone.return_value = mock_microphone
        mock_microphone.__enter__ = Mock(return_value=mock_microphone)
        mock_microphone.__exit__ = Mock(return_value=None)
        
        # Mock TTS engine
        mock_engine = Mock()
        mock_pyttsx3.init.return_value = mock_engine
        mock_engine.getProperty.return_value = []
        
        # Initialize
        speech_manager.initialize()
        
        assert speech_manager.is_initialized()
        assert speech_manager.microphone_manager.is_initialized()
        assert speech_manager.tts_manager.is_initialized()
    
    @patch('jarvis.audio.microphone.sr')
    @patch('jarvis.audio.tts.pyttsx3')
    def test_listen_and_speak_integration(self, mock_pyttsx3, mock_sr, speech_manager):
        """Test integration between listening and speaking."""
        # Setup mocks
        mock_recognizer = Mock()
        mock_microphone = Mock()
        mock_audio_data = Mock()
        
        mock_sr.Recognizer.return_value = mock_recognizer
        mock_sr.Microphone.return_value = mock_microphone
        mock_microphone.__enter__ = Mock(return_value=mock_microphone)
        mock_microphone.__exit__ = Mock(return_value=None)
        mock_recognizer.listen.return_value = mock_audio_data
        mock_recognizer.recognize_google.return_value = "Hello Jarvis"
        
        mock_engine = Mock()
        mock_pyttsx3.init.return_value = mock_engine
        mock_engine.getProperty.return_value = []
        
        # Initialize
        speech_manager.initialize()
        
        # Test listen -> speak cycle
        text = speech_manager.listen_for_speech(timeout=1.0)
        assert text == "Hello Jarvis"
        
        # Test speaking the recognized text
        speech_manager.speak_text(f"I heard: {text}")
        
        # Verify TTS was called
        mock_engine.say.assert_called()
        mock_engine.runAndWait.assert_called()
    
    @patch('jarvis.audio.microphone.sr')
    @patch('jarvis.audio.tts.pyttsx3')
    def test_conversation_mode_integration(self, mock_pyttsx3, mock_sr, speech_manager):
        """Test conversation mode with optimized settings."""
        # Setup mocks
        mock_recognizer = Mock()
        mock_microphone = Mock()
        mock_audio_data = Mock()
        
        mock_sr.Recognizer.return_value = mock_recognizer
        mock_sr.Microphone.return_value = mock_microphone
        mock_microphone.__enter__ = Mock(return_value=mock_microphone)
        mock_microphone.__exit__ = Mock(return_value=None)
        mock_recognizer.listen.return_value = mock_audio_data
        mock_recognizer.recognize_google.return_value = "Test command"
        
        mock_engine = Mock()
        mock_pyttsx3.init.return_value = mock_engine
        mock_engine.getProperty.return_value = []
        
        # Initialize
        speech_manager.initialize()
        
        # Test conversation mode
        original_timeout = speech_manager.config.timeout
        original_phrase_limit = speech_manager.config.phrase_time_limit
        
        with speech_manager.conversation_mode():
            # Settings should be optimized for conversation
            assert speech_manager.config.timeout == 5.0
            assert speech_manager.config.phrase_time_limit == 8.0
            
            # Test listening in conversation mode
            text = speech_manager.listen_for_speech()
            assert text == "Test command"
        
        # Settings should be restored
        assert speech_manager.config.timeout == original_timeout
        assert speech_manager.config.phrase_time_limit == original_phrase_limit
    
    @patch('jarvis.audio.microphone.sr')
    @patch('jarvis.audio.tts.pyttsx3')
    def test_audio_enhancement_integration(self, mock_pyttsx3, mock_sr, speech_manager):
        """Test audio enhancement integration."""
        # Setup mocks
        mock_recognizer = Mock()
        mock_microphone = Mock()
        mock_audio_data = Mock()
        mock_audio_data.get_raw_data.return_value = b'\x00\x01' * 500
        mock_audio_data.sample_rate = 16000
        mock_audio_data.sample_width = 2
        
        mock_sr.Recognizer.return_value = mock_recognizer
        mock_sr.Microphone.return_value = mock_microphone
        mock_microphone.__enter__ = Mock(return_value=mock_microphone)
        mock_microphone.__exit__ = Mock(return_value=None)
        mock_recognizer.listen.return_value = mock_audio_data
        mock_recognizer.recognize_google.return_value = "Enhanced audio test"
        
        mock_engine = Mock()
        mock_pyttsx3.init.return_value = mock_engine
        mock_engine.getProperty.return_value = []
        
        # Initialize
        speech_manager.initialize()
        
        # Test with audio enhancement
        text = speech_manager.listen_for_speech(enhance_audio=True)
        assert text == "Enhanced audio test"
        
        # Verify audio processing was involved
        mock_recognizer.recognize_google.assert_called()
    
    @patch('jarvis.audio.microphone.sr')
    @patch('jarvis.audio.tts.pyttsx3')
    def test_error_handling_integration(self, mock_pyttsx3, mock_sr, speech_manager):
        """Test error handling across speech components."""
        # Setup mocks
        mock_recognizer = Mock()
        mock_microphone = Mock()
        
        mock_sr.Recognizer.return_value = mock_recognizer
        mock_sr.Microphone.return_value = mock_microphone
        mock_microphone.__enter__ = Mock(return_value=mock_microphone)
        mock_microphone.__exit__ = Mock(return_value=None)
        mock_sr.WaitTimeoutError = Exception
        mock_recognizer.listen.side_effect = mock_sr.WaitTimeoutError("Timeout")
        
        mock_engine = Mock()
        mock_pyttsx3.init.return_value = mock_engine
        mock_engine.getProperty.return_value = []
        
        # Initialize
        speech_manager.initialize()
        
        # Test timeout handling
        text = speech_manager.listen_for_speech(timeout=0.1)
        assert text is None  # Should return None on timeout
        
        # Test TTS error handling
        mock_engine.say.side_effect = Exception("TTS Error")
        
        with pytest.raises(TextToSpeechError):
            speech_manager.speak_text("Test error handling")
    
    @patch('jarvis.audio.microphone.sr')
    @patch('jarvis.audio.tts.pyttsx3')
    def test_system_info_integration(self, mock_pyttsx3, mock_sr, speech_manager):
        """Test system information integration."""
        # Setup mocks
        mock_recognizer = Mock()
        mock_microphone = Mock()
        mock_sr.Recognizer.return_value = mock_recognizer
        mock_sr.Microphone.return_value = mock_microphone
        mock_sr.Microphone.list_microphone_names.return_value = ["Test Mic 1", "Test Mic 2"]
        mock_microphone.__enter__ = Mock(return_value=mock_microphone)
        mock_microphone.__exit__ = Mock(return_value=None)
        
        mock_engine = Mock()
        mock_voice = Mock()
        mock_voice.id = "test_voice_id"
        mock_voice.name = "Test Voice"
        mock_pyttsx3.init.return_value = mock_engine
        mock_engine.getProperty.return_value = [mock_voice]
        
        # Initialize
        speech_manager.initialize()
        
        # Test system info
        info = speech_manager.get_system_info()
        
        assert info["is_initialized"] is True
        assert info["microphone_initialized"] is True
        assert info["tts_initialized"] is True
        assert "available_microphones" in info
        assert "available_voices" in info
        assert "config" in info
    
    @patch('jarvis.audio.microphone.sr')
    @patch('jarvis.audio.tts.pyttsx3')
    def test_cleanup_integration(self, mock_pyttsx3, mock_sr, speech_manager):
        """Test cleanup integration across components."""
        # Setup mocks
        mock_recognizer = Mock()
        mock_microphone = Mock()
        mock_sr.Recognizer.return_value = mock_recognizer
        mock_sr.Microphone.return_value = mock_microphone
        mock_microphone.__enter__ = Mock(return_value=mock_microphone)
        mock_microphone.__exit__ = Mock(return_value=None)
        
        mock_engine = Mock()
        mock_pyttsx3.init.return_value = mock_engine
        mock_engine.getProperty.return_value = []
        
        # Initialize
        speech_manager.initialize()
        assert speech_manager.is_initialized()
        
        # Cleanup
        speech_manager.cleanup()
        
        # Verify cleanup
        assert not speech_manager.is_initialized()
        mock_engine.stop.assert_called()


class TestAudioProcessorIntegration:
    """Test AudioProcessor integration with other components."""
    
    def test_audio_enhancement_pipeline(self, mock_audio_data):
        """Test complete audio enhancement pipeline."""
        processor = AudioProcessor()
        
        # Test enhancement pipeline
        enhanced_audio = processor.enhance_audio_for_recognition(
            mock_audio_data,
            noise_reduction=True,
            normalize=True
        )
        
        assert enhanced_audio is not None
        assert enhanced_audio.sample_rate == mock_audio_data.sample_rate
        assert enhanced_audio.sample_width == mock_audio_data.sample_width
    
    def test_audio_quality_analysis(self, mock_audio_data):
        """Test audio quality analysis."""
        processor = AudioProcessor()
        
        quality_metrics = processor.analyze_audio_quality(mock_audio_data)
        
        assert "rms_level" in quality_metrics
        assert "peak_level" in quality_metrics
        assert "snr_estimate" in quality_metrics
        assert "dynamic_range" in quality_metrics
        assert "zero_crossing_rate" in quality_metrics
        assert "sample_rate" in quality_metrics
        assert "duration" in quality_metrics
        assert "clipping_detected" in quality_metrics
    
    def test_speech_activity_detection(self, mock_audio_data):
        """Test speech activity detection."""
        processor = AudioProcessor()
        
        # Test with mock audio data
        has_speech = processor.detect_speech_activity(mock_audio_data)
        
        # Should return a boolean
        assert isinstance(has_speech, bool)
    
    def test_silence_trimming(self, mock_audio_data):
        """Test silence trimming functionality."""
        processor = AudioProcessor()
        
        trimmed_audio = processor.trim_silence(mock_audio_data)
        
        assert trimmed_audio is not None
        assert trimmed_audio.sample_rate == mock_audio_data.sample_rate
        assert trimmed_audio.sample_width == mock_audio_data.sample_width


class TestMicrophoneTTSIntegration:
    """Test integration between microphone and TTS components."""
    
    @patch('jarvis.audio.microphone.sr')
    @patch('jarvis.audio.tts.pyttsx3')
    def test_microphone_tts_coordination(self, mock_pyttsx3, mock_sr, audio_config):
        """Test coordination between microphone and TTS."""
        # Setup mocks
        mock_recognizer = Mock()
        mock_microphone = Mock()
        mock_audio_data = Mock()
        
        mock_sr.Recognizer.return_value = mock_recognizer
        mock_sr.Microphone.return_value = mock_microphone
        mock_microphone.__enter__ = Mock(return_value=mock_microphone)
        mock_microphone.__exit__ = Mock(return_value=None)
        mock_recognizer.listen.return_value = mock_audio_data
        mock_recognizer.recognize_google.return_value = "Test speech"
        
        mock_engine = Mock()
        mock_pyttsx3.init.return_value = mock_engine
        mock_engine.getProperty.return_value = []
        
        # Create components
        mic_manager = MicrophoneManager(audio_config)
        tts_manager = TextToSpeechManager(audio_config)
        
        # Initialize
        mic_manager.initialize()
        tts_manager.initialize()
        
        # Test coordination: listen then speak
        text = mic_manager.listen_for_speech()
        assert text == "Test speech"
        
        tts_manager.speak(f"I heard: {text}")
        
        # Verify both components were used
        mock_recognizer.recognize_google.assert_called()
        mock_engine.say.assert_called()
    
    @patch('jarvis.audio.microphone.sr')
    @patch('jarvis.audio.tts.pyttsx3')
    def test_simultaneous_operations_handling(self, mock_pyttsx3, mock_sr, audio_config):
        """Test handling of simultaneous microphone and TTS operations."""
        # Setup mocks
        mock_recognizer = Mock()
        mock_microphone = Mock()
        mock_sr.Recognizer.return_value = mock_recognizer
        mock_sr.Microphone.return_value = mock_microphone
        mock_microphone.__enter__ = Mock(return_value=mock_microphone)
        mock_microphone.__exit__ = Mock(return_value=None)
        
        mock_engine = Mock()
        mock_pyttsx3.init.return_value = mock_engine
        mock_engine.getProperty.return_value = []
        
        # Create components
        mic_manager = MicrophoneManager(audio_config)
        tts_manager = TextToSpeechManager(audio_config)
        
        # Initialize
        mic_manager.initialize()
        tts_manager.initialize()
        
        # Test stopping TTS before listening (common pattern)
        tts_manager.stop_speaking()
        
        # Should be able to listen after stopping TTS
        mock_recognizer.listen.return_value = Mock()
        mock_recognizer.recognize_google.return_value = "After TTS stop"
        
        text = mic_manager.listen_for_speech()
        assert text == "After TTS stop"
