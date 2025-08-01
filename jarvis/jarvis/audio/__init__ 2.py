"""
Audio management package for Jarvis Voice Assistant.

This package handles all audio-related functionality including microphone management,
text-to-speech, and audio processing.
"""

from .microphone import MicrophoneManager
from .tts import TextToSpeechManager
from .processors import AudioProcessor

__all__ = ['MicrophoneManager', 'TextToSpeechManager', 'AudioProcessor']