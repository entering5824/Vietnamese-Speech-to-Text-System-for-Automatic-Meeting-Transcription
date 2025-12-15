"""
Module xử lý audio: upload, preprocessing, visualization
"""
import librosa
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pydub import AudioSegment
import io
import streamlit as st
import tempfile
from typing import Tuple, List

# Đảm bảo FFmpeg đã được setup (cho PyDub)
try:
    from .ffmpeg_setup import ensure_ffmpeg
    ensure_ffmpeg()
except ImportError:
    # Nếu không có ffmpeg_setup, bỏ qua (có thể đã có FFmpeg trong system)
    pass

def load_audio(file, sr=16000):
    """Load audio file và convert về format chuẩn"""
    try:
        # Đọc audio file
        if isinstance(file, bytes):
            audio_bytes = file
        else:
            audio_bytes = file.read()
        
        # Xử lý theo định dạng
        file_extension = file.name.split('.')[-1].lower() if hasattr(file, 'name') else 'wav'
        
        if file_extension in ['mp3', 'm4a', 'flac', 'ogg']:
            # Sử dụng pydub để convert
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format=file_extension)
            # Convert to WAV
            wav_io = io.BytesIO()
            audio_segment.export(wav_io, format="wav")
            wav_io.seek(0)
            y, sr_original = sf.read(wav_io)
        else:
            y, sr_original = sf.read(io.BytesIO(audio_bytes))
        
        # Resample nếu cần
        if sr_original != sr:
            y = librosa.resample(y, orig_sr=sr_original, target_sr=sr)
        
        return y, sr
    except Exception as e:
        st.error(f"Lỗi khi load audio: {str(e)}")
        return None, None

def preprocess_audio(y, sr, normalize=True, remove_noise=False):
    """Tiền xử lý audio"""
    if y is None:
        return None
    
    # Normalize
    if normalize:
        y = librosa.util.normalize(y)
    
    # Noise reduction (simple high-pass filter)
    if remove_noise:
        from scipy import signal
        # High-pass filter để loại bỏ noise tần số thấp
        sos = signal.butter(10, 80, 'hp', fs=sr, output='sos')
        y = signal.sosfilt(sos, y)
    
    return y


# === Convenience helpers ===
def normalize_audio_to_wav(audio_path: str, target_sr: int = 16000) -> Tuple[str, int, np.ndarray]:
    """
    Load audio -> mono 16kHz WAV PCM16, peak-normalized.
    Returns (normalized_wav_path, sr, samples)
    """
    y, sr = librosa.load(audio_path, sr=target_sr, mono=True)
    peak = float(np.max(np.abs(y))) if y.size else 0.0
    if peak > 0:
        y = y / peak

    out_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    out_wav.close()
    sf.write(out_wav.name, y, target_sr, subtype="PCM_16")
    return out_wav.name, target_sr, y


def apply_noise_reduction(y: np.ndarray, sr: int, cutoff: int = 80):
    """
    Simple high-pass filter to reduce low-frequency noise.
    """
    from scipy import signal
    if y is None:
        return None
    sos = signal.butter(10, cutoff, "hp", fs=sr, output="sos")
    return signal.sosfilt(sos, y)


def chunk_signal(y: np.ndarray, sr: int, chunk_seconds: int) -> List[Tuple[int, int]]:
    """
    Split signal into chunks by duration (seconds).
    """
    total_samples = len(y)
    chunk_len = int(chunk_seconds * sr)
    if chunk_len <= 0 or total_samples == 0:
        return [(0, total_samples)]
    ranges = []
    for start in range(0, total_samples, chunk_len):
        end = min(start + chunk_len, total_samples)
        ranges.append((start, end))
    return ranges


def format_timestamp(seconds: float) -> str:
    """
    Format seconds -> MM:SS
    """
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"

def plot_waveform(y, sr, title="Waveform"):
    """Vẽ waveform"""
    fig, ax = plt.subplots(figsize=(12, 4))
    time = np.linspace(0, len(y) / sr, len(y))
    ax.plot(time, y, linewidth=0.5)
    ax.set_xlabel('Thời gian (s)', fontsize=10)
    ax.set_ylabel('Amplitude', fontsize=10)
    ax.set_title(title, fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig

def plot_spectrogram(y, sr, title="Spectrogram"):
    """Vẽ spectrogram"""
    # Tính spectrogram
    D = librosa.stft(y)
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    img = librosa.display.specshow(S_db, x_axis='time', y_axis='hz', 
                                    sr=sr, ax=ax, cmap='viridis')
    ax.set_title(title, fontsize=12)
    ax.set_xlabel('Thời gian (s)', fontsize=10)
    ax.set_ylabel('Tần số (Hz)', fontsize=10)
    plt.colorbar(img, ax=ax, format='%+2.0f dB')
    plt.tight_layout()
    return fig

def get_audio_info(y, sr):
    """Lấy thông tin audio"""
    if y is None:
        return {}
    
    duration = len(y) / sr
    return {
        'duration': duration,
        'sample_rate': sr,
        'channels': 1 if len(y.shape) == 1 else y.shape[1],
        'samples': len(y)
    }

