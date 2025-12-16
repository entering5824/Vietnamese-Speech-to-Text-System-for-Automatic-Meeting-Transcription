"""
Home / Dashboard Page
Tổng quan cho người dùng với recent transcripts và quick actions
"""
import streamlit as st
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Setup FFmpeg
from core.audio.ffmpeg_setup import ensure_ffmpeg
ensure_ffmpeg(silent=True)

from core.auth.session import init_session, get_current_user, add_to_history
from core.auth.roles import get_user_role, UserRole
from app.components.sidebar import render_sidebar
from app.components.layout import apply_custom_css

# Initialize session
init_session()

# Apply CSS
apply_custom_css()

# Render sidebar
render_sidebar()

# Get user info
user = get_current_user()
user_role = get_user_role()

st.header("🏠 Home / Dashboard")

# Welcome message
st.markdown(f"""
### Chào mừng, {user['user_name']}!

Bạn đang sử dụng hệ thống **Vietnamese Speech to Text** với quyền **{user_role.value.upper()}**.
""")

# Quick stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_transcripts = len(st.session_state.get("transcripts_history", []))
    st.metric("📝 Total Transcripts", total_transcripts)

with col2:
    if st.session_state.get("audio_info"):
        duration = st.session_state.audio_info.get("duration", 0)
        st.metric("⏱️ Current Audio", f"{duration:.1f}s" if duration else "None")
    else:
        st.metric("⏱️ Current Audio", "None")

with col3:
    if st.session_state.get("transcript_text"):
        word_count = len(st.session_state.transcript_text.split())
        st.metric("📊 Words", word_count)
    else:
        st.metric("📊 Words", "0")

with col4:
    # Session duration
    if st.session_state.get("session_start_time"):
        session_duration = (datetime.now() - st.session_state.session_start_time).total_seconds() / 60
        st.metric("⏰ Session", f"{session_duration:.1f}m")

st.markdown("---")

# Quick Actions
st.subheader("🚀 Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📤 Upload Audio", use_container_width=True, type="primary"):
        st.switch_page("pages/1_📤_Upload_Record.py")

with col2:
    if st.button("📝 Start Transcription", use_container_width=True):
        if st.session_state.get("audio_data") is None:
            st.warning("⚠️ Vui lòng upload audio trước!")
        else:
            st.switch_page("pages/3_📝_Transcription.py")

with col3:
    if st.button("📊 View Statistics", use_container_width=True):
        if st.session_state.get("transcript_text"):
            st.switch_page("pages/5_📊_Export_Statistics.py")
        else:
            st.warning("⚠️ Chưa có transcript để xem!")

st.markdown("---")

# Recent Transcripts
st.subheader("📚 Recent Transcripts")

transcripts_history = st.session_state.get("transcripts_history", [])

if transcripts_history:
    # Show last 5 transcripts
    for transcript in reversed(transcripts_history[-5:]):
        with st.expander(f"📄 {transcript.get('name', 'Untitled')} - {transcript.get('timestamp', 'Unknown time')[:10]}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Duration:** {transcript.get('duration', 'N/A')}s")
                st.write(f"**Model:** {transcript.get('model', 'N/A')}")
                if transcript.get('text'):
                    preview = transcript['text'][:200] + "..." if len(transcript.get('text', '')) > 200 else transcript.get('text', '')
                    st.write(f"**Preview:** {preview}")
            with col2:
                if st.button("📝 View", key=f"view_{transcript.get('id')}"):
                    # Load transcript into session state
                    st.session_state.transcript_text = transcript.get('text', '')
                    st.session_state.transcript_result = transcript.get('result', {})
                    st.rerun()
                if st.button("⬇️ Export", key=f"export_{transcript.get('id')}"):
                    st.switch_page("pages/5_📊_Export_Statistics.py")
else:
    st.info("💡 Chưa có transcript nào. Hãy bắt đầu bằng cách upload audio và transcribe!")

st.markdown("---")

# Current Session Status
st.subheader("📋 Current Session Status")

if st.session_state.get("audio_data") is not None:
    st.success("✅ Audio đã được load")
    if st.session_state.get("audio_info"):
        info = st.session_state.audio_info
        st.write(f"- **Duration:** {info.get('duration', 0):.2f} seconds")
        st.write(f"- **Sample Rate:** {info.get('sample_rate', 0)} Hz")
        st.write(f"- **Channels:** {info.get('channels', 1)}")
else:
    st.info("ℹ️ Chưa có audio. Hãy upload audio để bắt đầu!")

if st.session_state.get("transcript_text"):
    st.success("✅ Transcript đã sẵn sàng")
    st.write(f"- **Length:** {len(st.session_state.transcript_text)} characters")
    st.write(f"- **Words:** {len(st.session_state.transcript_text.split())} words")
else:
    st.info("ℹ️ Chưa có transcript. Hãy transcribe audio!")

# Role-specific sections
if user_role in [UserRole.AI_SPECIALIST, UserRole.ADMIN]:
    st.markdown("---")
    st.subheader("🔬 AI Specialist Tools")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🤖 Model Management", use_container_width=True):
            st.info("🚧 Model Management page đang được phát triển...")
    with col2:
        if st.button("📈 Evaluation", use_container_width=True):
            st.switch_page("pages/6_🔬_ASR_Benchmark.py")

if user_role == UserRole.ADMIN:
    st.markdown("---")
    st.subheader("👑 Admin Tools")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 Admin Dashboard", use_container_width=True):
            st.info("🚧 Admin Dashboard đang được phát triển...")
    with col2:
        if st.button("👥 User Management", use_container_width=True):
            st.info("🚧 User Management đang được phát triển...")
    with col3:
        if st.button("💰 Billing", use_container_width=True):
            st.info("🚧 Billing page đang được phát triển...")




