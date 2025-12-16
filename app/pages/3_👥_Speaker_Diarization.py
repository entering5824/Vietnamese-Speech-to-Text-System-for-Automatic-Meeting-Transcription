"""
Speaker Diarization Page
Detect speaker turns và hiển thị timeline
"""
import streamlit as st
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.components.layout import apply_custom_css
from app.components.diarization_timeline import render_diarization_timeline
from core.diarization.speaker_diarization import (
    simple_speaker_segmentation, format_with_speakers, format_time
)
from core.utils.export import export_docx, export_txt, format_duration
from core.audio.ffmpeg_setup import ensure_ffmpeg

# Setup FFmpeg
ensure_ffmpeg(silent=True)

# Apply custom CSS
apply_custom_css()

# Page config
st.set_page_config(
    page_title="Speaker Diarization - Vietnamese Speech to Text",
    page_icon="👥",
    layout="wide"
)

# Initialize session state
for key, default in (
    ("audio_data", None),
    ("audio_sr", None),
    ("audio_info", None),
    ("transcript_result", None),
    ("transcript_segments", []),
    ("speaker_segments", []),
):
    st.session_state.setdefault(key, default)

st.header("👥 Speaker Diarization")

# Check prerequisites
if st.session_state.audio_data is None:
    st.warning("⚠️ Vui lòng upload audio file trước tại trang 'Audio Input'")
    if st.button("🎤 Go to Audio Input", type="primary"):
        st.switch_page("pages/1_🎤_Audio_Input.py")
elif not st.session_state.transcript_segments:
    st.warning("⚠️ Vui lòng chạy transcription trước tại trang 'Transcription'")
    if st.button("📝 Go to Transcription", type="primary"):
        st.switch_page("pages/2_📝_Transcription.py")
else:
    st.info("✅ Audio và transcript đã sẵn sàng cho diarization")
    
    # Settings
    st.subheader("⚙️ Diarization Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        max_speakers = st.number_input(
            "Số lượng người nói tối đa",
            min_value=1,
            max_value=10,
            value=4,
            help="Số lượng người nói dự kiến trong audio"
        )
        min_silence_duration = st.slider(
            "Độ dài khoảng lặng tối thiểu (giây)",
            min_value=0.1,
            max_value=2.0,
            value=0.5,
            step=0.1,
            help="Khoảng lặng tối thiểu để phân tách speaker"
        )
    
    with col2:
        use_advanced = st.checkbox("Sử dụng diarization nâng cao", value=False, 
                                  help="Sử dụng pyannote.audio nếu có (cần cài đặt)")
        backend = st.selectbox(
            "Diarization Backend",
            ["Simple (Energy-based)", "Pyannote (Advanced)"],
            index=0,
            disabled=not use_advanced
        )
    
    # Run diarization
    if st.button("🚀 Chạy Speaker Diarization", type="primary", use_container_width=True):
        with st.spinner("Đang phân tích speaker..."):
            try:
                # Use simple segmentation for now
                speaker_segments = simple_speaker_segmentation(
                    st.session_state.audio_data,
                    st.session_state.audio_sr,
                    st.session_state.transcript_segments,
                    min_silence_duration=min_silence_duration
                )
                
                if speaker_segments:
                    st.session_state.speaker_segments = speaker_segments
                    st.success(f"✅ Đã phát hiện {len(set(seg.get('speaker') for seg in speaker_segments))} người nói!")
                else:
                    st.warning("⚠️ Không thể phân biệt speaker. Có thể do audio quá ngắn hoặc chỉ có 1 người nói.")
            except Exception as e:
                st.error(f"❌ Lỗi khi chạy diarization: {str(e)}")
                import traceback
                with st.expander("🔍 Chi tiết lỗi"):
                    st.code(traceback.format_exc())
    
    # Display results
    if st.session_state.speaker_segments:
        st.markdown("---")
        st.subheader("📊 Diarization Results")
        
        # Timeline visualization
        duration = st.session_state.audio_info.get('duration', 0)
        render_diarization_timeline(st.session_state.speaker_segments, duration)
        
        # Transcript with speakers
        st.subheader("📝 Transcript với Speaker Labels")
        formatted_transcript = format_with_speakers(st.session_state.speaker_segments)
        st.text_area(
            "Transcript:",
            formatted_transcript,
            height=400,
            key="diarized_transcript"
        )
        
        # Statistics
        st.subheader("📊 Statistics")
        speakers = set(seg.get('speaker') for seg in st.session_state.speaker_segments)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Số người nói", len(speakers))
        
        with col2:
            total_duration = sum(seg.get('end', 0) - seg.get('start', 0) for seg in st.session_state.speaker_segments)
            st.metric("Tổng thời gian nói", f"{total_duration:.2f}s")
        
        with col3:
            st.metric("Số segments", len(st.session_state.speaker_segments))
        
        # Export
        st.markdown("---")
        st.subheader("📤 Export")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            txt_data, txt_filename = export_txt(formatted_transcript, "transcript_with_speakers.txt")
            st.download_button(
                "⬇️ Download TXT",
                data=txt_data,
                file_name=txt_filename,
                mime="text/plain"
            )
        
        with col2:
            metadata = {
                "duration": duration,
                "speakers": len(speakers),
                "segments": len(st.session_state.speaker_segments)
            }
            docx_data, docx_filename = export_docx(formatted_transcript, metadata, "transcript_with_speakers.docx")
            st.download_button(
                "⬇️ Download DOCX",
                data=docx_data,
                file_name=docx_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        
        with col3:
            import json
            json_data = json.dumps({
                "speakers": list(speakers),
                "segments": st.session_state.speaker_segments,
                "metadata": metadata
            }, ensure_ascii=False, indent=2)
            st.download_button(
                "⬇️ Download JSON",
                data=json_data.encode('utf-8'),
                file_name="transcript_with_speakers.json",
                mime="application/json"
            )

