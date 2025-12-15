"""
Shared Sidebar Component
Hiển thị logo và navigation cho tất cả pages
"""
import streamlit as st
import os

def render_sidebar(logo_width=110):
    """
    Render sidebar với logo và title
    
    Args:
        logo_width: Chiều rộng logo (default: 110)
    """
    # Get project root (2 levels up from app/components/)
    base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    img_path = os.path.join(base, "assets", "logo.webp")
    
    # Display logo
    if os.path.exists(img_path):
        st.sidebar.image(img_path, width=logo_width)
    else:
        # Fallback nếu không có logo
        st.sidebar.markdown("### 🎤")
    
    st.sidebar.title("🎤 Vietnamese Speech to Text")
    st.sidebar.markdown("---")
    
    # Quick navigation
    st.sidebar.markdown("#### 🚀 Điều hướng nhanh")
    st.sidebar.page_link("app/main.py", label="🏠 Home")
    st.sidebar.page_link("app/pages/1_📤_Upload_Record.py", label="📤 Upload & Record")
    st.sidebar.page_link("app/pages/2_🎧_Preprocessing.py", label="🎧 Preprocessing")
    st.sidebar.page_link("app/pages/3_📝_Transcription.py", label="📝 Transcription")
    st.sidebar.page_link("app/pages/4_👥_Speaker_Diarization.py", label="👥 Speaker Diarization")
    st.sidebar.page_link("app/pages/5_📊_Export_Statistics.py", label="📊 Export & Statistics")
    st.sidebar.page_link("app/pages/6_🔬_ASR_Benchmark.py", label="🔬 ASR Benchmark")
    st.sidebar.page_link("app/pages/Analysis.py", label="📊 Analysis (Single-file)")
    st.sidebar.page_link("app/pages/Training_Info.py", label="📚 Training Info")
    st.sidebar.page_link("app/pages/Streaming.py", label="📡 Streaming")
    st.sidebar.page_link("app/pages/API_Docs.py", label="🧩 API Docs")

    st.sidebar.markdown("""
    <div style="font-size: 0.9em; color: #666; padding: 10px 0;">
    Hệ thống ASR đa mô hình cho tiếng Việt (Whisper, PhoWhisper, Vosk/DeepSpeech, API)
    </div>
    """, unsafe_allow_html=True)
