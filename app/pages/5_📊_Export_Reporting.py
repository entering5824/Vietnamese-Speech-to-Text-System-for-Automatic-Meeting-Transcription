"""
Export & Reporting Page
Xuất transcript và hiển thị statistics
"""
import streamlit as st
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.components.layout import apply_custom_css
from app.components.statistics_display import calculate_statistics, render_statistics
from core.utils.export import export_txt, export_docx, export_pdf

# Apply custom CSS
apply_custom_css()

# Page config
st.set_page_config(
    page_title="Export & Reporting - Vietnamese Speech to Text",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
for key, default in (
    ("transcript_text", ""),
    ("transcript_result", None),
    ("audio_info", None),
    ("speaker_segments", []),
):
    st.session_state.setdefault(key, default)

st.header("📊 Export & Reporting")

# Check if transcript is available
if not st.session_state.transcript_text:
    st.warning("⚠️ Vui lòng chạy transcription trước tại trang 'Transcription'")
    if st.button("📝 Go to Transcription", type="primary"):
        st.switch_page("pages/2_📝_Transcription.py")
else:
    # Calculate statistics
    duration = st.session_state.audio_info.get('duration', 0) if st.session_state.audio_info else 0
    stats = calculate_statistics(
        st.session_state.transcript_text,
        duration,
        st.session_state.speaker_segments if st.session_state.speaker_segments else None
    )
    
    # Display statistics
    render_statistics(stats)
    
    # Export section
    st.markdown("---")
    st.subheader("📤 Export Transcript")
    
    # Prepare metadata
    metadata = {
        "duration": duration,
        "word_count": stats["word_count"],
        "sentence_count": stats["sentence_count"],
        "words_per_minute": stats["words_per_minute"],
        "timestamp": st.session_state.transcript_result.get("timestamp") if st.session_state.transcript_result else None
    }
    
    if st.session_state.speaker_segments:
        metadata["speakers"] = stats["speakers"]
        metadata["speaker_stats"] = stats["speaker_stats"]
    
    # Export options
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # TXT export
        txt_data, txt_filename = export_txt(st.session_state.transcript_text, "transcript.txt")
        st.download_button(
            "⬇️ Download TXT",
            data=txt_data,
            file_name=txt_filename,
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        # DOCX export
        docx_data, docx_filename = export_docx(st.session_state.transcript_text, metadata, "transcript.docx")
        st.download_button(
            "⬇️ Download DOCX",
            data=docx_data,
            file_name=docx_filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
    
    with col3:
        # PDF export
        pdf_data, pdf_filename = export_pdf(st.session_state.transcript_text, metadata, "transcript.pdf")
        st.download_button(
            "⬇️ Download PDF",
            data=pdf_data,
            file_name=pdf_filename,
            mime="application/pdf",
            use_container_width=True
        )
    
    with col4:
        # JSON export
        json_data = {
            "transcript": st.session_state.transcript_text,
            "metadata": metadata,
            "statistics": stats
        }
        if st.session_state.speaker_segments:
            json_data["speaker_segments"] = st.session_state.speaker_segments
        
        json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
        st.download_button(
            "⬇️ Download JSON",
            data=json_str.encode('utf-8'),
            file_name="transcript.json",
            mime="application/json",
            use_container_width=True
        )
    
    # Preview transcript
    st.markdown("---")
    st.subheader("📝 Transcript Preview")
    st.text_area(
        "Transcript:",
        st.session_state.transcript_text,
        height=300,
        key="export_preview"
    )

