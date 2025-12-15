"""
Streaming Transcription Page
Hỗ trợ demo ghi âm liên tục (nếu audio_recorder_streamlit khả dụng) và hiển thị kết quả.
"""
import streamlit as st
import os
import sys
import tempfile
import soundfile as sf

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.components.sidebar import render_sidebar
from app.components.layout import apply_custom_css
from core.asr.transcription_service import load_whisper_model, transcribe_audio
from core.audio.audio_processor import format_timestamp

# Apply CSS & sidebar
apply_custom_css()
render_sidebar()

st.header("📡 Streaming Transcription")
st.info("Demo ghi âm liên tục phụ thuộc vào thư viện audio_recorder_streamlit. Nếu chưa cài, hãy dùng upload/record ở trang Upload & Record.")

# Try load recorder widget
recorder_available = False
try:
    from audio_recorder_streamlit import audio_recorder  # type: ignore
    recorder_available = True
except Exception:
    recorder_available = False

if not recorder_available:
    st.warning("Thư viện audio_recorder_streamlit chưa cài. Cài: pip install audio-recorder-streamlit")
else:
    model, device = load_whisper_model("base")
    if model is None:
        st.error("Không thể load Whisper model")
    else:
        audio_bytes = audio_recorder(text="Nhấn ghi để nói...", pause_threshold=1.0)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            with st.spinner("Đang nhận dạng..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(audio_bytes)
                    tmp.flush()
                    result = transcribe_audio(model, tmp.name, sr=16000, language="vi")
                try:
                    os.unlink(tmp.name)
                except:
                    pass
            if result and result.get("text"):
                text = result.get("text", "").strip()
                st.success("Kết quả:")
                st.write(text)
                st.session_state.transcript_text = (st.session_state.get("transcript_text", "") + "\n" + text).strip()
                st.text_area("Transcript tích luỹ", st.session_state.transcript_text, height=200)
            else:
                st.warning("Không nhận được kết quả. Hãy thử lại.")

st.markdown("---")
st.write("Nếu không dùng streaming, hãy quay lại trang Upload & Record để tải file âm thanh và transcribe.")
