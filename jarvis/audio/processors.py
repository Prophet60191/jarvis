"""
Audio processing utilities for Jarvis Voice Assistant.

This module provides audio processing functionality including noise reduction,
audio enhancement, and signal processing utilities.
"""

import logging
import numpy as np
from typing import Optional, Tuple, Any
import speech_recognition as sr

from ..exceptions import AudioError


logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Handles audio processing operations for the Jarvis voice assistant.
    
    This class provides utilities for audio enhancement, noise reduction,
    and signal processing to improve speech recognition accuracy.
    """
    
    def __init__(self):
        """Initialize the audio processor."""
        logger.info("AudioProcessor initialized")
    
    @staticmethod
    def enhance_audio_for_recognition(audio_data: sr.AudioData, 
                                    noise_reduction: bool = True,
                                    normalize: bool = True) -> sr.AudioData:
        """
        Enhance audio data for better speech recognition.
        
        Args:
            audio_data: Raw audio data from microphone
            noise_reduction: Whether to apply noise reduction
            normalize: Whether to normalize audio levels
            
        Returns:
            Enhanced audio data
            
        Raises:
            AudioError: If audio processing fails
        """
        try:
            logger.debug("Enhancing audio for speech recognition")
            
            # Convert audio data to numpy array for processing
            audio_array = np.frombuffer(audio_data.get_raw_data(), dtype=np.int16)
            
            # Apply noise reduction if requested
            if noise_reduction:
                audio_array = AudioProcessor._apply_noise_reduction(audio_array)
            
            # Normalize audio levels if requested
            if normalize:
                audio_array = AudioProcessor._normalize_audio(audio_array)
            
            # Convert back to AudioData
            enhanced_raw_data = audio_array.astype(np.int16).tobytes()
            enhanced_audio = sr.AudioData(
                enhanced_raw_data,
                audio_data.sample_rate,
                audio_data.sample_width
            )
            
            logger.debug("Audio enhancement completed")
            return enhanced_audio
            
        except Exception as e:
            error_msg = f"Failed to enhance audio: {str(e)}"
            logger.error(error_msg)
            raise AudioError(error_msg) from e
    
    @staticmethod
    def _apply_noise_reduction(audio_array: np.ndarray) -> np.ndarray:
        """
        Apply basic noise reduction to audio array.
        
        Args:
            audio_array: Input audio as numpy array
            
        Returns:
            Noise-reduced audio array
        """
        try:
            # Simple noise gate - remove very quiet sounds
            threshold = np.max(np.abs(audio_array)) * 0.05  # 5% of max amplitude
            audio_array = np.where(np.abs(audio_array) < threshold, 0, audio_array)
            
            # Apply simple high-pass filter to remove low-frequency noise
            # This is a very basic implementation - more sophisticated methods
            # would use proper digital signal processing libraries
            if len(audio_array) > 1:
                # Simple difference filter (high-pass)
                filtered = np.diff(audio_array, prepend=audio_array[0])
                audio_array = filtered * 0.7 + audio_array * 0.3
            
            logger.debug("Noise reduction applied")
            return audio_array
            
        except Exception as e:
            logger.warning(f"Noise reduction failed, using original audio: {str(e)}")
            return audio_array
    
    @staticmethod
    def _normalize_audio(audio_array: np.ndarray) -> np.ndarray:
        """
        Normalize audio levels to improve consistency.
        
        Args:
            audio_array: Input audio as numpy array
            
        Returns:
            Normalized audio array
        """
        try:
            # Avoid division by zero
            max_val = np.max(np.abs(audio_array))
            if max_val == 0:
                return audio_array
            
            # Normalize to use 80% of the dynamic range
            target_max = np.iinfo(np.int16).max * 0.8
            normalized = audio_array * (target_max / max_val)
            
            # Ensure we don't exceed int16 range
            normalized = np.clip(normalized, np.iinfo(np.int16).min, np.iinfo(np.int16).max)
            
            logger.debug("Audio normalization applied")
            return normalized.astype(np.int16)
            
        except Exception as e:
            logger.warning(f"Audio normalization failed, using original audio: {str(e)}")
            return audio_array
    
    @staticmethod
    def analyze_audio_quality(audio_data: sr.AudioData) -> dict:
        """
        Analyze audio quality metrics.
        
        Args:
            audio_data: Audio data to analyze
            
        Returns:
            Dictionary containing quality metrics
        """
        try:
            audio_array = np.frombuffer(audio_data.get_raw_data(), dtype=np.int16)
            
            # Calculate basic quality metrics
            rms = np.sqrt(np.mean(audio_array.astype(np.float64) ** 2))
            peak = np.max(np.abs(audio_array))
            snr_estimate = 20 * np.log10(rms / (np.std(audio_array) + 1e-10))
            
            # Dynamic range
            dynamic_range = peak - np.min(np.abs(audio_array[audio_array != 0]))
            
            # Zero crossing rate (indicator of speech vs noise)
            zero_crossings = np.sum(np.diff(np.sign(audio_array)) != 0)
            zcr = zero_crossings / len(audio_array)
            
            quality_metrics = {
                "rms_level": float(rms),
                "peak_level": float(peak),
                "snr_estimate": float(snr_estimate),
                "dynamic_range": float(dynamic_range),
                "zero_crossing_rate": float(zcr),
                "sample_rate": audio_data.sample_rate,
                "duration": len(audio_array) / audio_data.sample_rate,
                "clipping_detected": peak >= np.iinfo(np.int16).max * 0.95
            }
            
            logger.debug(f"Audio quality analysis: {quality_metrics}")
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Audio quality analysis failed: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def detect_speech_activity(audio_data: sr.AudioData, 
                             threshold_ratio: float = 0.1) -> bool:
        """
        Detect if audio contains speech activity.
        
        Args:
            audio_data: Audio data to analyze
            threshold_ratio: Ratio of peak level to consider as speech
            
        Returns:
            True if speech activity detected, False otherwise
        """
        try:
            audio_array = np.frombuffer(audio_data.get_raw_data(), dtype=np.int16)
            
            # Calculate energy level
            energy = np.sum(audio_array.astype(np.float64) ** 2)
            peak = np.max(np.abs(audio_array))
            
            # Simple voice activity detection based on energy and peak
            threshold = np.iinfo(np.int16).max * threshold_ratio
            has_speech = peak > threshold and energy > (threshold ** 2) * len(audio_array) * 0.1
            
            logger.debug(f"Speech activity detection: {has_speech} (peak={peak}, threshold={threshold})")
            return has_speech
            
        except Exception as e:
            logger.error(f"Speech activity detection failed: {str(e)}")
            return False
    
    @staticmethod
    def trim_silence(audio_data: sr.AudioData, 
                    silence_threshold: float = 0.05) -> sr.AudioData:
        """
        Trim silence from the beginning and end of audio.
        
        Args:
            audio_data: Audio data to trim
            silence_threshold: Threshold for silence detection (0-1)
            
        Returns:
            Trimmed audio data
        """
        try:
            audio_array = np.frombuffer(audio_data.get_raw_data(), dtype=np.int16)
            
            # Calculate threshold based on peak level
            peak = np.max(np.abs(audio_array))
            threshold = peak * silence_threshold
            
            # Find first and last non-silent samples
            non_silent = np.abs(audio_array) > threshold
            if not np.any(non_silent):
                # All silence, return original
                return audio_data
            
            first_sound = np.argmax(non_silent)
            last_sound = len(audio_array) - np.argmax(non_silent[::-1]) - 1
            
            # Trim the audio
            trimmed_array = audio_array[first_sound:last_sound + 1]
            
            # Convert back to AudioData
            trimmed_raw_data = trimmed_array.astype(np.int16).tobytes()
            trimmed_audio = sr.AudioData(
                trimmed_raw_data,
                audio_data.sample_rate,
                audio_data.sample_width
            )
            
            logger.debug(f"Audio trimmed: {len(audio_array)} -> {len(trimmed_array)} samples")
            return trimmed_audio
            
        except Exception as e:
            logger.warning(f"Audio trimming failed, using original: {str(e)}")
            return audio_data
    
    @staticmethod
    def convert_sample_rate(audio_data: sr.AudioData, 
                          target_rate: int) -> sr.AudioData:
        """
        Convert audio to a different sample rate.
        
        Args:
            audio_data: Audio data to convert
            target_rate: Target sample rate in Hz
            
        Returns:
            Audio data with new sample rate
            
        Note:
            This is a basic implementation. For production use,
            consider using proper resampling libraries like librosa.
        """
        try:
            if audio_data.sample_rate == target_rate:
                return audio_data
            
            logger.debug(f"Converting sample rate: {audio_data.sample_rate} -> {target_rate}")
            
            # Simple linear interpolation resampling
            # Note: This is not ideal for audio quality, but works for basic needs
            audio_array = np.frombuffer(audio_data.get_raw_data(), dtype=np.int16)
            
            # Calculate resampling ratio
            ratio = target_rate / audio_data.sample_rate
            new_length = int(len(audio_array) * ratio)
            
            # Create new time indices
            old_indices = np.arange(len(audio_array))
            new_indices = np.linspace(0, len(audio_array) - 1, new_length)
            
            # Interpolate
            resampled = np.interp(new_indices, old_indices, audio_array)
            resampled = resampled.astype(np.int16)
            
            # Create new AudioData
            resampled_raw_data = resampled.tobytes()
            resampled_audio = sr.AudioData(
                resampled_raw_data,
                target_rate,
                audio_data.sample_width
            )
            
            logger.debug("Sample rate conversion completed")
            return resampled_audio
            
        except Exception as e:
            logger.error(f"Sample rate conversion failed: {str(e)}")
            raise AudioError(f"Failed to convert sample rate: {str(e)}") from e
