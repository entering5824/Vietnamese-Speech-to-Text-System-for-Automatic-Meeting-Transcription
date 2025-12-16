"""
Audio Input & Preprocessing Page
Upload audio, record, visualize, và preprocessing
"""
import streamlit as st
import os
import sys
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.components.layout import apply_custom_css
from app.components.audio_visualizer import render_audio_visualization
from core.audio.audio_processor import (
    load_audio, get_audio_info, preprocess_audio, 
    validate_audio_format, normalize_audio_to_wav
)
from core.audio.ffmpeg_setup import ensure_ffmpeg

# Setup FFmpeg
ensure_ffmpeg(silent=True)

# Apply custom CSS
apply_custom_css()

# Page config
st.set_page_config(
    page_title="Audio Input - Vietnamese Speech to Text",
    page_icon="🎤",
    layout="wide"
)

# Initialize session state
for key, default in (
    ("audio_data", None),
    ("audio_sr", None),
    ("audio_info", None),
    ("audio_processed", None),
):
    st.session_state.setdefault(key, default)

st.header("🎤 Audio Input & Preprocessing")

# Tabs
tab1, tab2 = st.tabs(["📤 Upload Audio", "🎙️ Record Audio"])

with tab1:
    st.subheader("Upload Audio File")
    
    uploaded_file = st.file_uploader(
        "Chọn file audio (WAV, MP3, FLAC, M4A, OGG)",
        type=['wav', 'mp3', 'flac', 'm4a', 'ogg'],
        help="Hỗ trợ các định dạng: WAV, MP3, FLAC, M4A, OGG"
    )
    
    if uploaded_file is not None:
        # Validate format
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
                
                st.success("✅ Đã tải audio thành công!")
                
                # Display audio info
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Độ dài", f"{st.session_state.audio_info['duration']:.2f}s")
                with col2:
                    st.metric("Sample Rate", f"{sr} Hz")
                with col3:
                    st.metric("Channels", f"{st.session_state.audio_info.get('channels', 1)}")
                with col4:
                    st.metric("Samples", f"{len(audio_data):,}")
                
                # Play audio
                st.audio(uploaded_file, format='audio/wav')
            else:
                st.error("❌ Không thể load audio file!")

with tab2:
    st.subheader("Record Audio")
    
    st.info("💡 Tính năng này cho phép bạn upload file audio đã ghi âm sẵn để transcribe ngay lập tức.")
    st.warning("⚠️ Để ghi âm trực tiếp, vui lòng sử dụng ứng dụng ghi âm trên máy tính hoặc điện thoại, sau đó upload file tại tab 'Upload Audio'.")
    
    # Alternative: audio recorder component (if available)
    try:
        from audio_recorder_streamlit import audio_recorder
        audio_bytes = audio_recorder()
        
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            
            # Save to temp file and load
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name
            
            try:
                audio_data, sr = load_audio(tmp_path)
                if audio_data is not None:
                    st.session_state.audio_data = audio_data
                    st.session_state.audio_sr = sr
                    st.session_state.audio_info = get_audio_info(audio_data, sr)
                    st.success("✅ Đã ghi âm và load audio thành công!")
            finally:
                try:
                    os.unlink(tmp_path)
                except:
                    pass
    except ImportError:
        st.info("💡 Để sử dụng tính năng ghi âm trực tiếp, cài đặt: `pip install audio-recorder-streamlit`")

# Visualization
if st.session_state.audio_data is not None:
    st.markdown("---")
    st.subheader("📊 Audio Visualization")
    render_audio_visualization(st.session_state.audio_data, st.session_state.audio_sr)
    
    # Preprocessing options
    st.markdown("---")
    st.subheader("🔧 Preprocessing Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        normalize = st.checkbox("Normalize audio", value=True, help="Chuẩn hóa amplitude về [-1, 1]")
        remove_noise = st.checkbox("Noise reduction", value=False, help="Giảm nhiễu tần số thấp")
    
    with col2:
        trim_silence = st.checkbox("Trim silence", value=False, help="Loại bỏ khoảng lặng ở đầu và cuối")
        target_sr = st.selectbox("Target Sample Rate", [16000, 22050, 44100], index=0, help="Resample audio")
    
    if st.button("🔄 Apply Preprocessing", type="primary"):
        with st.spinner("Đang xử lý audio..."):
            processed_audio = preprocess_audio(
                st.session_state.audio_data,
                st.session_state.audio_sr,
                normalize=normalize,
                remove_noise=remove_noise
            )
            
            if processed_audio is not None:
                # Resample if needed
                if target_sr != st.session_state.audio_sr:
                    import librosa
                    processed_audio = librosa.resample(processed_audio, orig_sr=st.session_state.audio_sr, target_sr=target_sr)
                    st.session_state.audio_sr = target_sr
                
                # Trim silence if needed
                if trim_silence:
                    import librosa
                    processed_audio, _ = librosa.effects.trim(processed_audio)
                
                st.session_state.audio_data = processed_audio
                st.session_state.audio_info = get_audio_info(processed_audio, st.session_state.audio_sr)
                st.session_state.audio_processed = True
                
                st.success("✅ Đã xử lý audio thành công!")
                st.rerun()
    
    # Next step
    st.markdown("---")
    st.info("💡 Audio đã sẵn sàng! Chuyển sang trang **Transcription** để chạy ASR.")
    
    if st.button("➡️ Go to Transcription", type="primary", use_container_width=True):
        st.switch_page("pages/2_📝_Transcription.py")
else:
    st.info("👆 Vui lòng upload hoặc ghi âm audio để bắt đầu")

