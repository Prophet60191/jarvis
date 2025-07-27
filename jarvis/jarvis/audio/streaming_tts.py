"""
Streaming TTS implementation for Jarvis Voice Assistant.

This module provides real-time streaming text-to-speech capabilities
using Coqui TTS with chunked processing and audio streaming.
"""

import logging
import threading
import queue
import time
import tempfile
import os
from typing import Optional, Generator, Callable, Any, List, Union
from dataclasses import dataclass
from pathlib import Path

try:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
except ImportError:
    sd = None
    sf = None
    np = None

from ..config import AudioConfig
from ..exceptions import TextToSpeechError
from .coqui_tts import CoquiTTSManager


logger = logging.getLogger(__name__)


@dataclass
class StreamingConfig:
    """Configuration for streaming TTS."""
    chunk_size: int = 512  # Audio chunk size for streaming
    buffer_size: int = 3  # Number of chunks to buffer
    sentence_split: bool = True  # Split text by sentences
    min_chunk_length: int = 10  # Minimum characters per chunk
    max_chunk_length: int = 200  # Maximum characters per chunk
    overlap_words: int = 2  # Words to overlap between chunks
    stream_threshold: float = 0.5  # Start streaming after this many seconds of audio


class StreamingTTSManager:
    """
    Manages streaming text-to-speech operations.
    
    This class provides real-time TTS streaming with chunked processing,
    allowing for faster response times and better user experience.
    """
    
    def __init__(self, config: AudioConfig, streaming_config: Optional[StreamingConfig] = None):
        """
        Initialize the streaming TTS manager.
        
        Args:
            config: Audio configuration settings
            streaming_config: Streaming-specific configuration
        """
        self.config = config
        self.streaming_config = streaming_config or StreamingConfig()
        
        # Initialize base TTS manager
        self.tts_manager = CoquiTTSManager(config)
        
        # Streaming state
        self._is_streaming = False
        self._stream_thread: Optional[threading.Thread] = None
        self._audio_queue: queue.Queue = queue.Queue()
        self._stop_event = threading.Event()
        
        # Audio streaming
        self.audio_available = sd is not None and sf is not None and np is not None
        if not self.audio_available:
            logger.warning("Audio streaming dependencies not available. Install sounddevice, soundfile, and numpy.")
        
        logger.info(f"StreamingTTSManager initialized with config: {streaming_config}")
    
    def initialize(self) -> None:
        """Initialize the underlying TTS engine."""
        self.tts_manager.initialize()
        logger.info("Streaming TTS manager initialized")
    
    def is_initialized(self) -> bool:
        """Check if the TTS engine is initialized."""
        return self.tts_manager.is_initialized()
    
    def set_voice_profile(self, profile_id: str) -> bool:
        """Set the voice profile for streaming TTS."""
        return self.tts_manager.set_voice_profile(profile_id)
    
    def set_voice_profile_by_name(self, name: str) -> bool:
        """Set the voice profile by name for streaming TTS."""
        return self.tts_manager.set_voice_profile_by_name(name)
    
    def _split_text_for_streaming(self, text: str) -> List[str]:
        """
        Split text into chunks suitable for streaming.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []
        
        chunks = []
        
        if self.streaming_config.sentence_split:
            # Split by sentences first
            import re
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
        else:
            sentences = [text]
        
        for sentence in sentences:
            if len(sentence) <= self.streaming_config.max_chunk_length:
                chunks.append(sentence)
            else:
                # Split long sentences into smaller chunks
                words = sentence.split()
                current_chunk = []
                current_length = 0
                
                for word in words:
                    word_length = len(word) + 1  # +1 for space
                    
                    if (current_length + word_length > self.streaming_config.max_chunk_length and 
                        current_length >= self.streaming_config.min_chunk_length):
                        
                        # Add overlap words to next chunk
                        overlap_start = max(0, len(current_chunk) - self.streaming_config.overlap_words)
                        overlap_words = current_chunk[overlap_start:]
                        
                        chunks.append(' '.join(current_chunk))
                        current_chunk = overlap_words + [word]
                        current_length = sum(len(w) + 1 for w in current_chunk)
                    else:
                        current_chunk.append(word)
                        current_length += word_length
                
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
        
        # Filter out chunks that are too short
        chunks = [chunk for chunk in chunks if len(chunk) >= self.streaming_config.min_chunk_length]
        
        logger.debug(f"Split text into {len(chunks)} chunks for streaming")
        return chunks
    
    def _generate_audio_chunks(self, text_chunks: List[str]) -> Generator[Any, None, None]:
        """
        Generate audio chunks from text chunks.
        
        Args:
            text_chunks: List of text chunks to convert
            
        Yields:
            Audio data arrays
        """
        for i, chunk in enumerate(text_chunks):
            if self._stop_event.is_set():
                break
            
            try:
                logger.debug(f"Generating audio for chunk {i+1}/{len(text_chunks)}: '{chunk[:50]}...'")
                
                # Generate audio using the base TTS manager
                with self.tts_manager._lock:
                    speaker_wav_path = self.tts_manager._get_speaker_wav_path()
                    
                    if not speaker_wav_path:
                        raise TextToSpeechError("No voice profile available for streaming TTS")
                    
                    # Generate speech
                    wav_data = self.tts_manager.tts.tts(
                        text=chunk,
                        speaker_wav=speaker_wav_path,
                        language=self.tts_manager.language,
                        temperature=self.tts_manager.temperature,
                        length_penalty=self.tts_manager.length_penalty,
                        repetition_penalty=self.tts_manager.repetition_penalty,
                        top_k=self.tts_manager.top_k,
                        top_p=self.tts_manager.top_p
                    )
                
                # Convert to numpy array if needed
                if not isinstance(wav_data, np.ndarray):
                    wav_data = np.array(wav_data, dtype=np.float32)
                
                yield wav_data
                
            except Exception as e:
                logger.error(f"Failed to generate audio for chunk {i+1}: {e}")
                # Continue with next chunk instead of failing completely
                continue
    
    def _audio_streaming_thread(self, audio_generator: Generator[Any, None, None]) -> None:
        """
        Thread function for streaming audio playback.
        
        Args:
            audio_generator: Generator yielding audio chunks
        """
        try:
            if not self.audio_available:
                logger.error("Audio streaming not available")
                return
            
            # Audio streaming parameters
            sample_rate = 22050  # XTTS-v2 sample rate
            
            # Create audio stream
            stream = sd.OutputStream(
                samplerate=sample_rate,
                channels=1,
                dtype=np.float32,
                blocksize=self.streaming_config.chunk_size
            )
            
            with stream:
                for audio_chunk in audio_generator:
                    if self._stop_event.is_set():
                        break
                    
                    # Add audio chunk to queue for streaming
                    self._audio_queue.put(audio_chunk)
                    
                    # Stream audio in smaller chunks
                    chunk_size = self.streaming_config.chunk_size
                    for i in range(0, len(audio_chunk), chunk_size):
                        if self._stop_event.is_set():
                            break
                        
                        chunk = audio_chunk[i:i + chunk_size]
                        
                        # Pad chunk if necessary
                        if len(chunk) < chunk_size:
                            chunk = np.pad(chunk, (0, chunk_size - len(chunk)), mode='constant')
                        
                        # Play chunk
                        stream.write(chunk)
                        
                        # Small delay to prevent buffer overrun
                        time.sleep(0.001)
            
            logger.debug("Audio streaming completed")
            
        except Exception as e:
            logger.error(f"Audio streaming failed: {e}")
        finally:
            self._is_streaming = False
    
    def speak_streaming(self, text: str, callback: Optional[Callable[[str], None]] = None) -> None:
        """
        Convert text to speech using streaming.
        
        Args:
            text: Text to convert to speech
            callback: Optional callback function called for each chunk
            
        Raises:
            TextToSpeechError: If streaming TTS fails
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for streaming TTS")
            return
        
        if not self.is_initialized():
            raise TextToSpeechError("Streaming TTS engine not initialized. Call initialize() first.")
        
        if self._is_streaming:
            logger.warning("Streaming TTS already in progress, stopping previous stream")
            self.stop_streaming()
        
        try:
            logger.info(f"Starting streaming TTS for text: '{text[:100]}{'...' if len(text) > 100 else ''}'")
            
            # Split text into chunks
            text_chunks = self._split_text_for_streaming(text)
            
            if not text_chunks:
                logger.warning("No valid text chunks for streaming")
                return
            
            logger.debug(f"Streaming {len(text_chunks)} text chunks")
            
            # Reset streaming state
            self._stop_event.clear()
            self._is_streaming = True
            
            # Generate audio chunks
            audio_generator = self._generate_audio_chunks(text_chunks)
            
            # Start streaming thread
            self._stream_thread = threading.Thread(
                target=self._audio_streaming_thread,
                args=(audio_generator,),
                daemon=True
            )
            self._stream_thread.start()
            
            # Call callback for each chunk if provided
            if callback:
                for chunk in text_chunks:
                    if self._stop_event.is_set():
                        break
                    callback(chunk)
            
            logger.info("Streaming TTS started successfully")
            
        except Exception as e:
            self._is_streaming = False
            error_msg = f"Streaming TTS failed: {str(e)}"
            logger.error(error_msg)
            raise TextToSpeechError(error_msg, text=text) from e
    
    def stop_streaming(self) -> None:
        """Stop any current streaming TTS."""
        if not self._is_streaming:
            return
        
        logger.info("Stopping streaming TTS")
        
        # Signal stop
        self._stop_event.set()
        
        # Wait for thread to finish
        if self._stream_thread and self._stream_thread.is_alive():
            self._stream_thread.join(timeout=2.0)
        
        # Clear queue
        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
            except queue.Empty:
                break
        
        self._is_streaming = False
        logger.info("Streaming TTS stopped")
    
    def is_streaming(self) -> bool:
        """Check if streaming TTS is currently active."""
        return self._is_streaming
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for streaming TTS to complete.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if completed, False if timed out
        """
        if not self._is_streaming or not self._stream_thread:
            return True
        
        self._stream_thread.join(timeout=timeout)
        return not self._stream_thread.is_alive()
    
    def cleanup(self) -> None:
        """Clean up streaming TTS resources."""
        self.stop_streaming()
        self.tts_manager.cleanup()
        logger.info("Streaming TTS resources cleaned up")
