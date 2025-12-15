"""
QuartzNet Service
NVIDIA NeMo QuartzNet model
"""
import streamlit as st
from typing import Optional, Dict
import numpy as np
import librosa
import soundfile as sf
import tempfile
import os

def check_nemo_available():
    """Kiểm tra xem NeMo có available không"""
    try:
        import nemo.collections.asr as nemo_asr
        return True
    except ImportError:
        return False

@st.cache_resource
def load_quartznet_model(model_name="QuartzNet15x5Base-En"):
    """
    Load QuartzNet model từ NeMo
    
    Args:
        model_name: Model name từ NeMo (e.g., "QuartzNet15x5Base-En")
    
    Returns:
        Model object hoặc None
    """
    if not check_nemo_available():
        st.warning("""
        ⚠️ NeMo toolkit chưa được cài đặt.
        
        Cài đặt: pip install nemo-toolkit[asr]
        
        **Lưu ý:** NeMo QuartzNet models chủ yếu cho tiếng Anh.
        Cần model fine-tuned cho tiếng Việt.
        """)
        return None
    
    try:
        import nemo.collections.asr as nemo_asr
        
        # Load model
        model = nemo_asr.models.EncDecCTCModel.from_pretrained(model_name=model_name)
        return model
    except Exception as e:
        st.error(f"Lỗi khi load QuartzNet model: {str(e)}")
        st.info(f"💡 Có thể model '{model_name}' không tồn tại. Thử model khác hoặc cần model tiếng Việt.")
        return None

def transcribe_quartznet(model, audio_path_or_array, sr=16000, language="vi"):
    """
    Transcribe audio sử dụng QuartzNet
    
    Args:
        model: QuartzNet model
        audio_path_or_array: Đường dẫn file hoặc numpy array
        sr: Sample rate
        language: Ngôn ngữ
    
    Returns:
        Dict: Kết quả transcription
    """
    try:
        if model is None:
            return None
        
        # Xử lý input
        is_temp = False
        if isinstance(audio_path_or_array, str):
            audio_path = audio_path_or_array
        else:
            # Lưu vào temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                sf.write(tmp_file.name, audio_path_or_array, sr)
                audio_path = tmp_file.name
                is_temp = True
        
        # Transcribe với NeMo
        # NeMo yêu cầu file path hoặc list of file paths
        transcriptions = model.transcribe(paths2audio_files=[audio_path])
        
        # Clean up
        if is_temp and os.path.exists(audio_path):
            os.unlink(audio_path)
        
        text = transcriptions[0] if transcriptions else ""
        
        # Format output
        if isinstance(audio_path_or_array, str):
            duration = librosa.get_duration(path=audio_path_or_array)
        else:
            duration = len(audio_path_or_array) / sr
        
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
        st.error(f"Lỗi khi transcribe với QuartzNet: {str(e)}")
        # Clean up temp file nếu có
        if 'is_temp' in locals() and is_temp and os.path.exists(audio_path):
            try:
                os.unlink(audio_path)
            except:
                pass
        return None

# Tái sử dụng format functions
from .transcription_service import format_transcript, format_time, get_transcript_statistics

