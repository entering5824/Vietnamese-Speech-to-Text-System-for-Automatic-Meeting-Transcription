"""
Module transcription sử dụng Whisper
"""
import whisper
import torch
import streamlit as st
from typing import Optional, Dict, List
import numpy as np

@st.cache_resource
def load_whisper_model(model_size="base"):
    """Load Whisper model với cache"""
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = whisper.load_model(model_size, device=device)
        return model, device
    except Exception as e:
        error_msg = str(e)
        # Kiểm tra lỗi network
        if "getaddrinfo failed" in error_msg or "urlopen error" in error_msg.lower():
            st.error(f"❌ Lỗi kết nối mạng khi tải Whisper model. Vui lòng kiểm tra kết nối internet hoặc thử lại sau.")
            st.info("💡 Whisper cần tải model từ internet lần đầu tiên. Model sẽ được cache sau khi tải thành công.")
        else:
            st.error(f"Lỗi khi load Whisper model: {error_msg}")
        return None, None

def transcribe_audio(model, audio_path_or_array, sr=16000, language="vi", 
                     task="transcribe", verbose=False):
    """
    Transcribe audio sử dụng Whisper
    
    Args:
        model: Whisper model
        audio_path_or_array: Đường dẫn file hoặc numpy array
        sr: Sample rate
        language: Ngôn ngữ (vi cho tiếng Việt)
        task: "transcribe" hoặc "translate"
        verbose: Hiển thị thông tin chi tiết
    """
    try:
        if model is None:
            return None
        
        # Transcribe
        result = model.transcribe(
            audio_path_or_array,
            language=language,
            task=task,
            verbose=verbose,
            fp16=False  # Sử dụng fp32 để tránh lỗi trên CPU
        )
        
        return result
    except Exception as e:
        st.error(f"Lỗi khi transcribe: {str(e)}")
        return None

def format_transcript(result: Dict, with_timestamps: bool = True) -> str:
    """Format transcript từ kết quả Whisper"""
    if result is None:
        return ""
    
    text = result.get("text", "")
    segments = result.get("segments", [])
    
    if not with_timestamps or not segments:
        return text
    
    # Format với timestamps
    formatted_lines = []
    for segment in segments:
        start = segment.get("start", 0)
        end = segment.get("end", 0)
        segment_text = segment.get("text", "").strip()
        
        if segment_text:
            formatted_lines.append(f"[{format_time(start)} - {format_time(end)}] {segment_text}")
    
    return "\n".join(formatted_lines)

def format_time(seconds: float) -> str:
    """Format thời gian từ seconds sang HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    else:
        return f"{minutes:02d}:{secs:02d}.{millis:03d}"

def get_transcript_statistics(result: Dict, duration: float) -> Dict:
    """Tính toán thống kê transcript"""
    if result is None:
        return {}
    
    text = result.get("text", "")
    words = text.split()
    
    return {
        'word_count': len(words),
        'character_count': len(text),
        'duration': duration,
        'words_per_minute': (len(words) / duration * 60) if duration > 0 else 0,
        'segments_count': len(result.get("segments", []))
    }

