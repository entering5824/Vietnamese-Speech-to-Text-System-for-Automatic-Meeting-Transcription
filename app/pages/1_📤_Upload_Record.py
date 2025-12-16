"""
Upload & Record Page
"""
import streamlit as st
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.audio.audio_processor import load_audio, get_audio_info, validate_audio_format
from app.components.sidebar import render_sidebar
from app.components.layout import apply_custom_css

# Apply custom CSS
apply_custom_css()

# Render sidebar with logo
render_sidebar()

# Initialize session state if not exists
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
if 'audio_sr' not in st.session_state:
    st.session_state.audio_sr = None
if 'audio_info' not in st.session_state:
    st.session_state.audio_info = None

st.header("📤 Upload & Record Audio")
# Upload file
uploaded_file = st.file_uploader(
    "Chọn file audio (WAV, MP3, FLAC)",
    type=['wav', 'mp3', 'flac', 'm4a', 'ogg'],
    help="Hỗ trợ các định dạng: WAV, MP3, FLAC, M4A, OGG"
)

if uploaded_file is not None:
    # Validate format before loading
    file_extension = uploaded_file.name.split('.')[-1].lower() if hasattr(uploaded_file, 'name') else 'unknown'
    is_valid, format_msg = validate_audio_format(file_extension)
    
    if not is_valid:
        st.warning(f"⚠️ {format_msg}")
    
    # Load audio
    with st.spinner("Đang tải audio..."):
        audio_data, sr = load_audio(uploaded_file)
        
        if audio_data is not None:
            st.session_state.audio_data = audio_data
            st.session_state.audio_sr = sr
            st.session_state.audio_info = get_audio_info(audio_data, sr)
            
            st.success(f"✅ Đã tải audio thành công!")
            
            # Hiển thị thông tin audio
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Độ dài", f"{st.session_state.audio_info['duration']:.2f} giây")
            with col2:
                st.metric("Sample Rate", f"{sr} Hz")
            with col3:
                st.metric("Số mẫu", f"{len(audio_data):,}")
            
            # Play audio
            st.audio(uploaded_file, format='audio/wav')
        else:
            st.error("❌ Không thể load audio file!")

# Recording section
st.markdown("---")
st.subheader("🎙️ Ghi âm trực tiếp")

st.info("💡 Tính năng này cho phép bạn upload file audio đã ghi âm sẵn để transcribe ngay lập tức.")
st.warning("⚠️ Để ghi âm trực tiếp, vui lòng sử dụng ứng dụng ghi âm trên máy tính hoặc điện thoại, sau đó upload file tại đây.")

# Audio upload cho recording
audio_file = st.file_uploader(
    "Upload file audio đã ghi âm:",
    type=['wav', 'mp3', 'flac', 'm4a', 'ogg'],
    key="recording_upload"
)

if audio_file:
    # Validate format before loading
    file_extension = audio_file.name.split('.')[-1].lower() if hasattr(audio_file, 'name') else 'unknown'
    is_valid, format_msg = validate_audio_format(file_extension)
    
    if is_valid:
        st.success("✅ Đã tải file audio thành công!")
    else:
        st.warning(f"⚠️ {format_msg}")
    
    # Play audio
    st.audio(audio_file, format='audio/wav')
    
    # Load audio từ file
    with st.spinner("Đang xử lý audio..."):
        audio_data, sr = load_audio(audio_file)
        
        if audio_data is not None:
            st.session_state.audio_data = audio_data
            st.session_state.audio_sr = sr
            st.session_state.audio_info = get_audio_info(audio_data, sr)
            
            # Hiển thị thông tin
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Độ dài", f"{st.session_state.audio_info['duration']:.2f} giây")
            with col2:
                st.metric("Sample Rate", f"{sr} Hz")

