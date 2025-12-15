"""
Preprocessing Page
"""
import streamlit as st
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.audio.audio_processor import (
    preprocess_audio, plot_waveform, plot_spectrogram, get_audio_info
)
from app.components.sidebar import render_sidebar
from app.components.layout import apply_custom_css

# Apply custom CSS
apply_custom_css()

# Render sidebar with logo
render_sidebar()

st.header("🎧 Audio Preprocessing & Visualization")
if st.session_state.audio_data is None:
    st.warning("⚠️ Vui lòng upload audio file trước tại trang 'Upload & Record'")
else:
    # Display audio info
    if st.session_state.audio_info:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Độ dài", f"{st.session_state.audio_info['duration']:.2f} giây")
        with col2:
            st.metric("Sample Rate", f"{st.session_state.audio_sr} Hz")
        with col3:
            st.metric("Số mẫu", f"{len(st.session_state.audio_data):,}")
    
    # Preprocessing options
    st.subheader("⚙️ Tiền xử lý Audio")
    col1, col2 = st.columns(2)
    with col1:
        normalize = st.checkbox("Normalize audio", value=True)
    with col2:
        remove_noise = st.checkbox("Loại bỏ noise", value=False)
    
    if st.button("Áp dụng tiền xử lý", type="primary"):
        if st.session_state.audio_data is not None:
            with st.spinner("Đang xử lý..."):
                st.session_state.audio_data = preprocess_audio(
                    st.session_state.audio_data, 
                    st.session_state.audio_sr,
                    normalize=normalize,
                    remove_noise=remove_noise
                )
                # Update audio info
                st.session_state.audio_info = get_audio_info(
                    st.session_state.audio_data, 
                    st.session_state.audio_sr
                )
            st.success("✅ Đã áp dụng tiền xử lý!")
            st.rerun()
    
    # Visualization
    st.subheader("📊 Visualization")
    viz_option = st.radio(
        "Chọn loại visualization:",
        ["Waveform", "Spectrogram", "Cả hai"],
        horizontal=True
    )
    
    if st.session_state.audio_data is not None:
        if viz_option in ["Waveform", "Cả hai"]:
            fig_wave = plot_waveform(st.session_state.audio_data, st.session_state.audio_sr)
            st.pyplot(fig_wave)
        
        if viz_option in ["Spectrogram", "Cả hai"]:
            fig_spec = plot_spectrogram(st.session_state.audio_data, st.session_state.audio_sr)
            st.pyplot(fig_spec)

