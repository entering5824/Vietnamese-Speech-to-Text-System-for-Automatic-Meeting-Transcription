"""
Wav2Vec 2.0 Service
Self-supervised learning model từ Facebook
"""
import torch
import streamlit as st
from typing import Optional, Dict
import numpy as np
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import librosa
import soundfile as sf
import tempfile
import os

@st.cache_resource
def load_wav2vec2_model(model_name="facebook/wav2vec2-base-960h"):
    """
    Load Wav2Vec 2.0 model từ HuggingFace
    
    Args:
        model_name: Model name từ HuggingFace
    
    Returns:
        (processor, model) hoặc (None, None) nếu lỗi
    """
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        processor = Wav2Vec2Processor.from_pretrained(model_name)
        model = Wav2Vec2ForCTC.from_pretrained(model_name).to(device)
        
        return processor, model
    except Exception as e:
        st.error(f"Lỗi khi load Wav2Vec 2.0 model: {str(e)}")
        return None, None

def transcribe_wav2vec2(processor, model, audio_path_or_array, sr=16000, language="vi"):
    """
    Transcribe audio sử dụng Wav2Vec 2.0
    
    Args:
        processor: Wav2Vec2Processor
        model: Wav2Vec2ForCTC model
        audio_path_or_array: Đường dẫn file hoặc numpy array
        sr: Sample rate
        language: Ngôn ngữ (not used for Wav2Vec2, but kept for compatibility)
    
    Returns:
        Dict: Kết quả transcription với format tương thích Whisper
    """
    try:
        if processor is None or model is None:
            return None
        
        device = next(model.parameters()).device
        
        # Xử lý input
        is_temp = False
        if isinstance(audio_path_or_array, str):
            audio_path = audio_path_or_array
            # Load audio
            audio, sr_loaded = librosa.load(audio_path, sr=16000)
        else:
            # Là numpy array
            audio = audio_path_or_array
            if sr != 16000:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
            sr_loaded = 16000
        
        # Process audio
        inputs = processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Inference
        with torch.no_grad():
            logits = model(**inputs).logits
        
        # Decode
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)[0]
        
        # Format output tương thích
        duration = len(audio) / sr_loaded
        output = {
            "text": transcription.strip(),
            "segments": [{
                "start": 0.0,
                "end": duration,
                "text": transcription.strip()
            }]
        }
        
        return output
    except Exception as e:
        st.error(f"Lỗi khi transcribe với Wav2Vec 2.0: {str(e)}")
        return None

# Tái sử dụng format functions từ transcription_service
from .transcription_service import format_transcript, format_time, get_transcript_statistics

