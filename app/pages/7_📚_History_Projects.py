"""
History / Projects Page
Quản lý lịch sử transcripts và projects
"""
import streamlit as st
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.auth.session import init_session, get_current_user
from core.auth.roles import get_user_role
from app.components.sidebar import render_sidebar
from app.components.layout import apply_custom_css
from core.utils.export import export_txt, export_docx, export_pdf

# Initialize session
init_session()

# Apply CSS
apply_custom_css()

# Render sidebar
render_sidebar()

st.header("📚 History / Projects")

user = get_current_user()
user_role = get_user_role()

# Filter options
col1, col2, col3 = st.columns(3)

with col1:
    filter_date = st.date_input("📅 Filter by Date", value=None)

with col2:
    filter_model = st.selectbox(
        "🤖 Filter by Model",
        ["All", "Whisper", "PhoWhisper"],
        index=0
    )

with col3:
    search_query = st.text_input("🔍 Search", placeholder="Search transcripts...")

st.markdown("---")

# Transcripts list
transcripts_history = st.session_state.get("transcripts_history", [])

if not transcripts_history:
    st.info("💡 Chưa có transcript nào trong lịch sử. Hãy bắt đầu transcribe audio!")
else:
    # Apply filters
    filtered_transcripts = transcripts_history
    
    if filter_date:
        filtered_transcripts = [
            t for t in filtered_transcripts
            if datetime.fromisoformat(t.get('timestamp', '')).date() == filter_date
        ]
    
    if filter_model != "All":
        filtered_transcripts = [
            t for t in filtered_transcripts
            if filter_model.lower() in t.get('model', '').lower()
        ]
    
    if search_query:
        filtered_transcripts = [
            t for t in filtered_transcripts
            if search_query.lower() in t.get('text', '').lower() or 
               search_query.lower() in t.get('name', '').lower()
        ]
    
    st.subheader(f"📋 Transcripts ({len(filtered_transcripts)}/{len(transcripts_history)})")
    
    # Bulk actions
    if len(filtered_transcripts) > 0:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🗑️ Delete Selected", type="secondary"):
                st.warning("🚧 Bulk delete feature đang được phát triển...")
        with col2:
            if st.button("📦 Export Selected", type="secondary"):
                st.warning("🚧 Bulk export feature đang được phát triển...")
        with col3:
            if st.button("📊 View Statistics", type="secondary"):
                st.info("🚧 Statistics view đang được phát triển...")
    
    st.markdown("---")
    
    # Display transcripts
    for idx, transcript in enumerate(reversed(filtered_transcripts)):
        with st.expander(
            f"📄 {transcript.get('name', f'Transcript #{transcript.get('id', idx)}')} - "
            f"{datetime.fromisoformat(transcript.get('timestamp', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M')}",
            expanded=False
        ):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Metadata
                metadata_cols = st.columns(4)
                with metadata_cols[0]:
                    st.metric("Duration", f"{transcript.get('duration', 0):.1f}s")
                with metadata_cols[1]:
                    st.metric("Words", transcript.get('word_count', 0))
                with metadata_cols[2]:
                    st.metric("Model", transcript.get('model', 'N/A'))
                with metadata_cols[3]:
                    st.metric("Status", "✅ Complete")
                
                # Preview
                if transcript.get('text'):
                    preview = transcript['text'][:300] + "..." if len(transcript.get('text', '')) > 300 else transcript.get('text', '')
                    st.text_area("Preview", preview, height=100, key=f"preview_{idx}", disabled=True)
            
            with col2:
                st.write("**Actions**")
                if st.button("📝 Load", key=f"load_{idx}", use_container_width=True):
                    st.session_state.transcript_text = transcript.get('text', '')
                    st.session_state.transcript_result = transcript.get('result', {})
                    st.session_state.audio_info = transcript.get('audio_info', {})
                    st.success("✅ Transcript đã được load!")
                    st.rerun()
                
                if st.button("⬇️ Export TXT", key=f"export_txt_{idx}", use_container_width=True):
                    try:
                        txt_bytes, txt_name = export_txt(
                            transcript.get('text', ''),
                            f"transcript_{transcript.get('id', idx)}_{datetime.now().strftime('%Y%m%d')}.txt"
                        )
                        st.download_button(
                            "⬇️ Download",
                            data=txt_bytes,
                            file_name=txt_name,
                            mime="text/plain",
                            key=f"dl_txt_{idx}"
                        )
                    except Exception as e:
                        st.error(f"❌ Lỗi: {str(e)}")
                
                if st.button("🗑️ Delete", key=f"delete_{idx}", use_container_width=True):
                    # Remove from history
                    transcript_id = transcript.get('id')
                    if transcript_id is not None:
                        st.session_state.transcripts_history = [
                            t for t in st.session_state.transcripts_history
                            if t.get('id') != transcript_id
                        ]
                        st.success("✅ Đã xóa transcript!")
                        st.rerun()

# Add current session to history button
st.markdown("---")
if st.session_state.get("transcript_text") and st.session_state.get("transcript_result"):
    st.subheader("💾 Save Current Session")
    
    transcript_name = st.text_input(
        "Project Name",
        value=f"Transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        key="save_transcript_name"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save to History", type="primary", use_container_width=True):
            from core.auth.session import add_to_history
            
            transcript_data = {
                "name": transcript_name,
                "text": st.session_state.transcript_text,
                "result": st.session_state.transcript_result,
                "audio_info": st.session_state.get("audio_info", {}),
                "model": st.session_state.get("current_model", "Unknown"),
                "duration": st.session_state.get("audio_info", {}).get("duration", 0),
                "word_count": len(st.session_state.transcript_text.split()),
            }
            
            add_to_history(transcript_data)
            st.success("✅ Đã lưu vào lịch sử!")
            st.rerun()
    
    with col2:
        if st.button("📤 Export & Save", use_container_width=True):
            st.switch_page("pages/5_📊_Export_Statistics.py")




