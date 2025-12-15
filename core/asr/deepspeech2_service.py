"""
DeepSpeech 2 Service
Mozilla DeepSpeech CTC model
"""
import streamlit as st
from typing import Optional, Dict
import numpy as np
import librosa
import soundfile as sf
import tempfile
import os

def check_deepspeech_available():
    """Kiểm tra xem DeepSpeech có available không"""
    try:
        import deepspeech
        return True
    except ImportError:
        return False

@st.cache_resource
def load_deepspeech2_model(model_path=None):
    """
    Load DeepSpeech 2 model
    
    Args:
        model_path: Đường dẫn đến model file (.pbmm hoặc .tflite)
                   Nếu None, sẽ cố gắng tải từ default location
    
    Returns:
        Model object hoặc None
    """
    if not check_deepspeech_available():
        st.warning("⚠️ DeepSpeech chưa được cài đặt. Vui lòng cài: pip install deepspeech")
        return None
    
    try:
        import deepspeech
        
        # Nếu không có model_path, hướng dẫn user
        if model_path is None:
            st.info("""
            **DeepSpeech 2 Setup:**
            
            DeepSpeech cần model file (.pbmm hoặc .tflite). 
            Vui lòng tải model từ: https://github.com/mozilla/DeepSpeech/releases
            
            **Lưu ý:** DeepSpeech không có model tiếng Việt mặc định.
            Bạn cần train hoặc tìm model tiếng Việt.
            """)
            return None
        
        if not os.path.exists(model_path):
            st.error(f"❌ Không tìm thấy model file: {model_path}")
            return None
        
        # Load model
        model = deepspeech.Model(model_path)
        return model
    except Exception as e:
        st.error(f"Lỗi khi load DeepSpeech model: {str(e)}")
        return None

def transcribe_deepspeech2(model, audio_path_or_array, sr=16000, language="vi"):
    """
    Transcribe audio sử dụng DeepSpeech 2
    
    Args:
        model: DeepSpeech model
        audio_path_or_array: Đường dẫn file hoặc numpy array
        sr: Sample rate
        language: Ngôn ngữ (not used, but kept for compatibility)
    
    Returns:
        Dict: Kết quả transcription
    """
    try:
        if model is None:
            return None
        
        # Xử lý input
        if isinstance(audio_path_or_array, str):
            # Load audio, DeepSpeech yêu cầu 16kHz mono
            audio, sr_loaded = librosa.load(audio_path_or_array, sr=16000, mono=True)
        else:
            # Numpy array
            audio = audio_path_or_array
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)  # Convert to mono
            if sr != 16000:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
            sr_loaded = 16000
        
        # Convert to int16 (DeepSpeech requirement)
        audio_int16 = (audio * 32767).astype(np.int16)
        
        # Transcribe
        text = model.stt(audio_int16)
        
        # Format output
        duration = len(audio) / sr_loaded
        output = {
            "text": text.strip(),
            "segments": [{
                "start": 0.0,
                "end": duration,
                "text": text.strip()
            }]
        }
        
        return output
    except Exception as e:
        st.error(f"Lỗi khi transcribe với DeepSpeech 2: {str(e)}")
        return None

# Tái sử dụng format functions
from .transcription_service import format_transcript, format_time, get_transcript_statistics

