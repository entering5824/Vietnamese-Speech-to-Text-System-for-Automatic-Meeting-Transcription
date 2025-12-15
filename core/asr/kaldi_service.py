"""
Kaldi Service
Kaldi HMM-GMM toolkit
"""
import streamlit as st
from typing import Optional, Dict
import subprocess
import os

def check_kaldi_available():
    """Kiểm tra xem Kaldi có installed không"""
    try:
        # Kiểm tra Kaldi commands
        result = subprocess.run(
            ['which', 'online2-wav-nnet3-latgen-faster'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        # Trên Windows, kiểm tra khác
        kaldi_root = os.environ.get('KALDI_ROOT')
        return kaldi_root is not None and os.path.exists(kaldi_root)

@st.cache_resource
def load_kaldi_model(model_dir=None):
    """
    Load Kaldi model
    
    Lưu ý: Kaldi rất phức tạc, cần:
    - Kaldi toolkit cài đặt
    - Acoustic model
    - Language model
    - Decoding graph
    
    Service này là placeholder với hướng dẫn.
    """
    if not check_kaldi_available():
        st.warning("""
        ⚠️ Kaldi toolkit chưa được cài đặt.
        
        **Kaldi là toolkit phức tạc, cần cài đặt thủ công:**
        
        1. **Cài đặt Kaldi:**
           - Clone: https://github.com/kaldi-asr/kaldi
           - Build theo hướng dẫn trong INSTALL file
           - Set environment variable: KALDI_ROOT
        
        2. **Cần có models:**
           - Acoustic model (HMM-GMM hoặc DNN)
           - Language model (FST format)
           - Decoding graph (HCLG.fst)
        
        3. **Cho tiếng Việt:**
           - Cần train hoặc tìm acoustic model tiếng Việt
           - Cần language model tiếng Việt
        
        **Khuyến nghị:** Sử dụng các mô hình khác (Whisper, PhoWhisper) dễ tích hợp hơn.
        """)
        return None
    
    # Placeholder - sẽ implement wrapper nếu có Kaldi
    st.info("💡 Kaldi đã được phát hiện, nhưng cần cấu hình model paths.")
    return None

def transcribe_kaldi(model, audio_path_or_array, sr=16000, language="vi"):
    """
    Transcribe audio sử dụng Kaldi
    
    Placeholder function
    """
    st.error("Kaldi chưa được tích hợp đầy đủ. Cần cấu hình models và decoding pipeline.")
    return None

# Tái sử dụng format functions
from .transcription_service import format_transcript, format_time, get_transcript_statistics

