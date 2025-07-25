"""
Voice Quality Enhancement for Jarvis Voice Assistant.

This module provides advanced voice quality enhancement features including
audio preprocessing, quality analysis, noise reduction, and voice optimization
for better TTS output quality.
"""

import logging
import numpy as np
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

try:
    import librosa
    import soundfile as sf
    from scipy import signal
    from scipy.signal import butter, filtfilt
except ImportError:
    librosa = None
    sf = None
    signal = None
    butter = None
    filtfilt = None

from ..exceptions import TextToSpeechError


logger = logging.getLogger(__name__)


class EnhancementLevel(Enum):
    """Voice enhancement levels."""
    NONE = "none"
    LIGHT = "light"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


@dataclass
class VoiceQualityMetrics:
    """Voice quality analysis metrics."""
    snr_db: float  # Signal-to-noise ratio in dB
    dynamic_range: float  # Dynamic range
    spectral_centroid: float  # Spectral centroid (brightness)
    spectral_rolloff: float  # Spectral rolloff
    zero_crossing_rate: float  # Zero crossing rate
    rms_energy: float  # RMS energy
    pitch_stability: float  # Pitch stability (0-1)
    clarity_score: float  # Overall clarity score (0-1)
    quality_score: float  # Overall quality score (0-1)


@dataclass
class EnhancementConfig:
    """Configuration for voice enhancement."""
    enhancement_level: EnhancementLevel = EnhancementLevel.MODERATE
    noise_reduction: bool = True
    normalize_audio: bool = True
    apply_eq: bool = True
    enhance_clarity: bool = True
    target_sample_rate: int = 22050
    target_bit_depth: int = 16
    
    # Noise reduction parameters
    noise_reduction_strength: float = 0.5  # 0.0 to 1.0
    
    # EQ parameters
    low_freq_boost: float = 0.0  # dB boost for low frequencies
    mid_freq_boost: float = 2.0  # dB boost for mid frequencies
    high_freq_boost: float = 1.0  # dB boost for high frequencies
    
    # Clarity enhancement
    clarity_enhancement_strength: float = 0.3  # 0.0 to 1.0


class VoiceEnhancementProcessor:
    """
    Processes and enhances voice audio for better TTS quality.
    
    This class provides comprehensive voice enhancement capabilities including
    noise reduction, audio normalization, EQ, and quality analysis.
    """
    
    def __init__(self, config: Optional[EnhancementConfig] = None):
        """
        Initialize the voice enhancement processor.
        
        Args:
            config: Enhancement configuration
        """
        self.config = config or EnhancementConfig()
        
        # Check audio processing dependencies
        self.audio_processing_available = all([
            librosa is not None,
            sf is not None,
            signal is not None,
            butter is not None,
            filtfilt is not None
        ])
        
        if not self.audio_processing_available:
            logger.warning("Audio processing dependencies not available. Install librosa, soundfile, and scipy.")
        
        logger.info(f"VoiceEnhancementProcessor initialized with level: {self.config.enhancement_level.value}")
    
    def analyze_voice_quality(self, audio: Any, sample_rate: int) -> VoiceQualityMetrics:
        """
        Analyze voice quality metrics.
        
        Args:
            audio: Audio waveform
            sample_rate: Sample rate
            
        Returns:
            VoiceQualityMetrics with analysis results
        """
        if not self.audio_processing_available:
            # Return basic metrics without advanced processing
            rms_energy = np.sqrt(np.mean(audio**2))
            return VoiceQualityMetrics(
                snr_db=20.0,  # Default values
                dynamic_range=0.5,
                spectral_centroid=1000.0,
                spectral_rolloff=2000.0,
                zero_crossing_rate=0.1,
                rms_energy=float(rms_energy),
                pitch_stability=0.7,
                clarity_score=0.6,
                quality_score=0.6
            )
        
        try:
            # Basic audio metrics
            rms_energy = np.sqrt(np.mean(audio**2))
            dynamic_range = np.max(np.abs(audio)) - np.min(np.abs(audio))
            zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(audio))
            
            # Spectral features
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(audio, sr=sample_rate))
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(audio, sr=sample_rate))
            
            # Estimate SNR
            snr_db = self._estimate_snr(audio)
            
            # Pitch stability
            pitch_stability = self._calculate_pitch_stability(audio, sample_rate)
            
            # Clarity score based on spectral features
            clarity_score = self._calculate_clarity_score(audio, sample_rate)
            
            # Overall quality score
            quality_score = self._calculate_overall_quality(
                snr_db, dynamic_range, spectral_centroid, pitch_stability, clarity_score
            )
            
            return VoiceQualityMetrics(
                snr_db=float(snr_db),
                dynamic_range=float(dynamic_range),
                spectral_centroid=float(spectral_centroid),
                spectral_rolloff=float(spectral_rolloff),
                zero_crossing_rate=float(zero_crossing_rate),
                rms_energy=float(rms_energy),
                pitch_stability=float(pitch_stability),
                clarity_score=float(clarity_score),
                quality_score=float(quality_score)
            )
            
        except Exception as e:
            logger.warning(f"Voice quality analysis failed: {e}")
            # Return default metrics
            return VoiceQualityMetrics(
                snr_db=15.0,
                dynamic_range=0.4,
                spectral_centroid=1200.0,
                spectral_rolloff=2500.0,
                zero_crossing_rate=0.08,
                rms_energy=float(rms_energy) if 'rms_energy' in locals() else 0.1,
                pitch_stability=0.6,
                clarity_score=0.5,
                quality_score=0.5
            )
    
    def enhance_voice_audio(self, audio: Any, sample_rate: int) -> Tuple[Any, int]:
        """
        Enhance voice audio quality.
        
        Args:
            audio: Input audio waveform
            sample_rate: Input sample rate
            
        Returns:
            Tuple of (enhanced_audio, output_sample_rate)
        """
        if not self.audio_processing_available:
            logger.warning("Audio enhancement not available, returning original audio")
            return audio, sample_rate
        
        if self.config.enhancement_level == EnhancementLevel.NONE:
            return audio, sample_rate
        
        try:
            enhanced_audio = audio.copy()
            
            # Resample if needed
            if sample_rate != self.config.target_sample_rate:
                enhanced_audio = librosa.resample(
                    enhanced_audio, 
                    orig_sr=sample_rate, 
                    target_sr=self.config.target_sample_rate
                )
                sample_rate = self.config.target_sample_rate
            
            # Apply enhancements based on level
            if self.config.enhancement_level in [EnhancementLevel.LIGHT, EnhancementLevel.MODERATE, EnhancementLevel.AGGRESSIVE]:
                
                # Noise reduction
                if self.config.noise_reduction:
                    enhanced_audio = self._apply_noise_reduction(enhanced_audio, sample_rate)
                
                # Normalize audio
                if self.config.normalize_audio:
                    enhanced_audio = self._normalize_audio(enhanced_audio)
                
                # Apply EQ
                if self.config.apply_eq:
                    enhanced_audio = self._apply_eq(enhanced_audio, sample_rate)
                
                # Enhance clarity
                if self.config.enhance_clarity:
                    enhanced_audio = self._enhance_clarity(enhanced_audio, sample_rate)
            
            logger.debug(f"Voice enhancement completed with level: {self.config.enhancement_level.value}")
            return enhanced_audio, sample_rate
            
        except Exception as e:
            logger.error(f"Voice enhancement failed: {e}")
            return audio, sample_rate
    
    def _estimate_snr(self, audio: np.ndarray) -> float:
        """Estimate signal-to-noise ratio."""
        try:
            # Simple SNR estimation based on signal variance
            signal_power = np.var(audio)
            
            # Estimate noise from quiet segments (bottom 10% of energy)
            frame_size = len(audio) // 100
            if frame_size < 1:
                frame_size = 1
            
            frames = [audio[i:i+frame_size] for i in range(0, len(audio), frame_size)]
            frame_energies = [np.var(frame) for frame in frames if len(frame) == frame_size]
            
            if not frame_energies:
                return 20.0  # Default SNR
            
            noise_power = np.percentile(frame_energies, 10)
            
            if noise_power <= 0:
                return 40.0  # Very high SNR
            
            snr = 10 * np.log10(signal_power / noise_power)
            return max(0.0, min(50.0, snr))  # Clamp between 0 and 50 dB
            
        except Exception:
            return 20.0  # Default SNR
    
    def _calculate_pitch_stability(self, audio: np.ndarray, sample_rate: int) -> float:
        """Calculate pitch stability score."""
        try:
            # Extract pitch using librosa
            pitches, magnitudes = librosa.piptrack(y=audio, sr=sample_rate)
            
            # Get the most prominent pitch in each frame
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:  # Valid pitch
                    pitch_values.append(pitch)
            
            if len(pitch_values) < 2:
                return 0.5  # Default stability
            
            # Calculate pitch stability as inverse of coefficient of variation
            pitch_std = np.std(pitch_values)
            pitch_mean = np.mean(pitch_values)
            
            if pitch_mean == 0:
                return 0.5
            
            cv = pitch_std / pitch_mean
            stability = 1.0 / (1.0 + cv)  # Higher stability = lower variation
            
            return max(0.0, min(1.0, stability))
            
        except Exception:
            return 0.6  # Default stability
    
    def _calculate_clarity_score(self, audio: np.ndarray, sample_rate: int) -> float:
        """Calculate voice clarity score."""
        try:
            # Calculate spectral features that correlate with clarity
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(audio, sr=sample_rate))
            spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(audio, sr=sample_rate))
            spectral_contrast = np.mean(librosa.feature.spectral_contrast(audio, sr=sample_rate))
            
            # Normalize features and combine
            centroid_score = min(1.0, spectral_centroid / 2000.0)  # Normalize to 0-1
            bandwidth_score = min(1.0, spectral_bandwidth / 1000.0)
            contrast_score = min(1.0, np.mean(spectral_contrast) / 20.0)
            
            clarity = (centroid_score + bandwidth_score + contrast_score) / 3.0
            return max(0.0, min(1.0, clarity))
            
        except Exception:
            return 0.6  # Default clarity
    
    def _calculate_overall_quality(self, snr_db: float, dynamic_range: float, 
                                 spectral_centroid: float, pitch_stability: float, 
                                 clarity_score: float) -> float:
        """Calculate overall quality score."""
        try:
            # Normalize SNR (0-40 dB -> 0-1)
            snr_score = min(1.0, max(0.0, snr_db / 40.0))
            
            # Normalize dynamic range (0-1 -> 0-1)
            dynamic_score = min(1.0, max(0.0, dynamic_range))
            
            # Normalize spectral centroid (500-3000 Hz -> 0-1)
            centroid_score = min(1.0, max(0.0, (spectral_centroid - 500) / 2500))
            
            # Weighted combination
            quality = (
                0.3 * snr_score +
                0.2 * dynamic_score +
                0.2 * centroid_score +
                0.15 * pitch_stability +
                0.15 * clarity_score
            )
            
            return max(0.0, min(1.0, quality))
            
        except Exception:
            return 0.6  # Default quality
    
    def _apply_noise_reduction(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply noise reduction to audio."""
        try:
            # Simple spectral subtraction-based noise reduction
            # This is a basic implementation - more advanced methods could be added
            
            # Apply a high-pass filter to remove low-frequency noise
            nyquist = sample_rate / 2
            low_cutoff = 80  # Hz
            high_cutoff = min(8000, nyquist * 0.95)  # Hz
            
            # Design bandpass filter
            low = low_cutoff / nyquist
            high = high_cutoff / nyquist
            
            b, a = butter(4, [low, high], btype='band')
            filtered_audio = filtfilt(b, a, audio)
            
            # Blend with original based on strength
            strength = self.config.noise_reduction_strength
            return (1 - strength) * audio + strength * filtered_audio
            
        except Exception as e:
            logger.warning(f"Noise reduction failed: {e}")
            return audio
    
    def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Normalize audio amplitude."""
        try:
            # Peak normalization
            max_val = np.max(np.abs(audio))
            if max_val > 0:
                # Normalize to 90% of maximum to prevent clipping
                return audio * (0.9 / max_val)
            return audio
            
        except Exception:
            return audio
    
    def _apply_eq(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply equalization to enhance voice frequencies."""
        try:
            # Simple 3-band EQ for voice enhancement
            nyquist = sample_rate / 2
            
            # Low band: 80-300 Hz
            low_b, low_a = butter(2, [80/nyquist, 300/nyquist], btype='band')
            low_band = filtfilt(low_b, low_a, audio)
            
            # Mid band: 300-3000 Hz (most important for speech)
            mid_b, mid_a = butter(2, [300/nyquist, 3000/nyquist], btype='band')
            mid_band = filtfilt(mid_b, mid_a, audio)
            
            # High band: 3000-8000 Hz
            high_cutoff = min(8000, nyquist * 0.95)
            high_b, high_a = butter(2, [3000/nyquist, high_cutoff/nyquist], btype='band')
            high_band = filtfilt(high_b, high_a, audio)
            
            # Apply gains (convert dB to linear)
            low_gain = 10**(self.config.low_freq_boost / 20)
            mid_gain = 10**(self.config.mid_freq_boost / 20)
            high_gain = 10**(self.config.high_freq_boost / 20)
            
            # Combine bands
            enhanced = low_gain * low_band + mid_gain * mid_band + high_gain * high_band
            
            # Normalize to prevent clipping
            max_val = np.max(np.abs(enhanced))
            if max_val > 1.0:
                enhanced = enhanced / max_val
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"EQ application failed: {e}")
            return audio
    
    def _enhance_clarity(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Enhance voice clarity."""
        try:
            # Apply subtle high-frequency emphasis for clarity
            nyquist = sample_rate / 2
            
            # High-shelf filter to boost clarity frequencies (2-8 kHz)
            shelf_freq = 2000 / nyquist
            
            # Simple high-shelf implementation
            b, a = butter(2, shelf_freq, btype='high')
            high_freq = filtfilt(b, a, audio)
            
            # Blend with original
            strength = self.config.clarity_enhancement_strength
            enhanced = (1 - strength) * audio + strength * high_freq
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"Clarity enhancement failed: {e}")
            return audio
