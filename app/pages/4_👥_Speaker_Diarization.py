"""
Speaker Diarization Page
"""
import streamlit as st
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.diarization.speaker_diarization import (
    simple_speaker_segmentation, format_with_speakers
)
from core.asr.transcription_service import format_transcript
from app.components.sidebar import render_sidebar
from app.components.layout import apply_custom_css

# Apply custom CSS
apply_custom_css()

# Render sidebar with logo
render_sidebar()

st.header("👥 Speaker Diarization")
if st.session_state.audio_data is None:
    st.warning("⚠️ Vui lòng upload audio file trước tại trang 'Upload & Record'")
elif st.session_state.transcript_result is None:
    st.warning("⚠️ Vui lòng transcribe audio trước tại trang 'Transcription'")
else:
    st.info("💡 Speaker diarization phân biệt các người nói khác nhau trong audio.")
    
    if st.button("🔍 Phân tích Speaker", type="primary"):
        if 'segments' in st.session_state.transcript_result and st.session_state.transcript_result['segments']:
            with st.spinner("Đang phân tích speaker..."):
                speaker_segments = simple_speaker_segmentation(
                    st.session_state.audio_data,
                    st.session_state.audio_sr,
                    st.session_state.transcript_result['segments']
                )
                
                if speaker_segments:
                    st.session_state.transcript_text = format_with_speakers(speaker_segments)
                    st.success("✅ Đã phân tích speaker thành công!")
                    st.rerun()
                else:
                    st.warning("⚠️ Không thể phân tích speaker. Có thể do audio không có segments chi tiết.")
        else:
            st.warning("⚠️ Transcript không có segments chi tiết. Speaker diarization yêu cầu timestamps.")
    
    # Hiển thị diarized transcript
    if st.session_state.transcript_text and any("Speaker" in line for line in st.session_state.transcript_text.split('\n')):
        st.subheader("📝 Diarized Transcript")
        st.text_area(
            "Transcript với speaker labels:",
            st.session_state.transcript_text,
            height=500,
            key="diarized_transcript"
        )
        
        # Speaker statistics
        st.subheader("📊 Speaker Statistics")
        lines = st.session_state.transcript_text.split('\n')
        speakers = {}
        for line in lines:
            if "Speaker" in line:
                speaker = line.split(":")[0].split("]")[-1].strip()
                if speaker not in speakers:
                    speakers[speaker] = 0
                speakers[speaker] += len(line.split())
        
        if speakers:
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Số lượng speaker:**", len(speakers))
            with col2:
                st.write("**Tổng số từ:**", sum(speakers.values()))
            
            st.write("**Phân bố từ theo speaker:**")
            for speaker, word_count in speakers.items():
                st.write(f"- {speaker}: {word_count} từ")

