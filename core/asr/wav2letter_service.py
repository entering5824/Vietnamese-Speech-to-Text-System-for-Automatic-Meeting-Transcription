"""
Wav2Letter++ Service
Facebook Wav2Letter++ CNN model
"""
import streamlit as st
from typing import Optional, Dict
import numpy as np

def check_wav2letter_available():
    """Kiểm tra xem Wav2Letter++ có available không"""
    # Wav2Letter++ thường cần build từ source hoặc Docker
    # Khó tích hợp trực tiếp, nên sẽ là placeholder
    return False

@st.cache_resource
def load_wav2letter_model(model_path=None):
    """
    Load Wav2Letter++ model
    
    Lưu ý: Wav2Letter++ cần build từ source hoặc Docker.
    Service này là placeholder với hướng dẫn cài đặt.
    """
    if not check_wav2letter_available():
        st.warning("""
        ⚠️ Wav2Letter++ chưa được tích hợp.
        
        **Lý do:** Wav2Letter++ cần build từ source code hoặc sử dụng Docker container.
        
        **Hướng dẫn cài đặt:**
        1. Clone repository: https://github.com/facebookresearch/wav2letter
        2. Build từ source theo hướng dẫn
        3. Hoặc sử dụng Docker: docker pull wav2letter/wav2letter:latest
        
        **Lưu ý:** Cần model acoustic và language model cho tiếng Việt.
        """)
        return None
    
    # Placeholder - sẽ implement nếu có Wav2Letter++ installed
    return None

def transcribe_wav2letter(model, audio_path_or_array, sr=16000, language="vi"):
    """
    Transcribe audio sử dụng Wav2Letter++
    
    Placeholder function
    """
    st.error("Wav2Letter++ chưa được tích hợp. Vui lòng xem hướng dẫn cài đặt.")
    return None

# Tái sử dụng format functions
from .transcription_service import format_transcript, format_time, get_transcript_statistics

