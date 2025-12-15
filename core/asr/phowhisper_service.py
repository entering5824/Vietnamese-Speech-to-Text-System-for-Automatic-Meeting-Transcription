"""
Module transcription sử dụng PhoWhisper (HuggingFace)
PhoWhisper là mô hình ASR tối ưu cho tiếng Việt từ VinAI Research
"""
import torch
import streamlit as st
from typing import Optional, Dict, List
import numpy as np
from transformers import pipeline
import librosa
import soundfile as sf
import tempfile
import os

@st.cache_resource
def load_phowhisper_model(model_size="small"):
    """
    Load PhoWhisper model từ HuggingFace với cache
    
    Args:
        model_size: "small", "medium", hoặc "base"
    
    Returns:
        pipeline: Transformers pipeline object hoặc None nếu lỗi
    """
    try:
        device = 0 if torch.cuda.is_available() else -1
        model_name = f"vinai/PhoWhisper-{model_size}"
        
        # Load pipeline
        transcriber = pipeline(
            "automatic-speech-recognition",
            model=model_name,
            device=device
        )
        
        return transcriber
    except Exception as e:
        st.error(f"Lỗi khi load PhoWhisper model: {str(e)}")
        return None

def transcribe_phowhisper(model, audio_path_or_array, sr=16000, language="vi"):
    """
    Transcribe audio sử dụng PhoWhisper
    
    Args:
        model: PhoWhisper pipeline model
        audio_path_or_array: Đường dẫn file hoặc numpy array
        sr: Sample rate (PhoWhisper yêu cầu 16kHz)
        language: Ngôn ngữ (vi cho tiếng Việt)
    
    Returns:
        Dict: Kết quả transcription với format tương thích Whisper
        {
            "text": str,
            "segments": List[Dict] (có thể rỗng nếu không có timestamps)
        }
    """
    try:
        if model is None:
            return None
        
        # Xử lý input: có thể là file path hoặc numpy array
        is_temp = False
        if isinstance(audio_path_or_array, str):
            # Đã là file path
            audio_path = audio_path_or_array
        else:
            # Là numpy array, cần lưu vào temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                sf.write(tmp_file.name, audio_path_or_array, sr)
                audio_path = tmp_file.name
                is_temp = True
        
        # Transcribe với PhoWhisper
        result = model(audio_path, return_timestamps=True)
        
        # Clean up temp file nếu có
        if is_temp and os.path.exists(audio_path):
            os.unlink(audio_path)
        
        # Format kết quả để tương thích với Whisper format
        output = {
            "text": result.get("text", ""),
            "segments": []
        }
        
        # PhoWhisper có thể trả về chunks với timestamps
        if "chunks" in result:
            for chunk in result["chunks"]:
                if "timestamp" in chunk:
                    timestamp = chunk["timestamp"]
                    output["segments"].append({
                        "start": timestamp[0] if isinstance(timestamp, (list, tuple)) else timestamp,
                        "end": timestamp[1] if isinstance(timestamp, (list, tuple)) and len(timestamp) > 1 else timestamp,
                        "text": chunk.get("text", "").strip()
                    })
        
        # Nếu không có chunks, tạo một segment duy nhất
        if not output["segments"] and output["text"]:
            # Ước tính duration từ audio file
            try:
                if isinstance(audio_path_or_array, str):
                    duration = librosa.get_duration(path=audio_path_or_array)
                else:
                    duration = len(audio_path_or_array) / sr
            except:
                duration = 0
            
            output["segments"] = [{
                "start": 0.0,
                "end": duration,
                "text": output["text"]
            }]
        
        return output
    except Exception as e:
        st.error(f"Lỗi khi transcribe với PhoWhisper: {str(e)}")
        # Clean up temp file nếu có
        if 'is_temp' in locals() and is_temp and os.path.exists(audio_path):
            try:
                os.unlink(audio_path)
            except:
                pass
        return None

# Tái sử dụng các hàm format từ transcription_service
from .transcription_service import format_transcript, format_time, get_transcript_statistics

