"""
Analysis Page - Phân tích Audio & Speech-to-Text
Tích hợp chunking logic và normalization workflow từ reference
"""
import streamlit as st
import os
import sys
import numpy as np
import tempfile
import librosa
import librosa.display
import matplotlib.pyplot as plt
import soundfile as sf

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.audio.audio_processor import plot_waveform, get_audio_info
from core.asr.transcription_service import load_whisper_model, transcribe_audio, format_time
from core.asr.phowhisper_service import load_phowhisper_model, transcribe_phowhisper
from app.components.sidebar import render_sidebar
from app.components.layout import apply_custom_css
from app.components.footer import render_footer

# Apply custom CSS
apply_custom_css()

# Render sidebar with logo
render_sidebar()

st.header("📊 Analysis – Phân tích Audio & Speech-to-Text")

# Mục tiêu section
st.markdown("""
<div class="card">
<h4 style="color: #1f4e79; margin-top: 0;">Mục tiêu</h4>
<ul style="margin: 10px 0 0 18px; line-height: 1.8;">
    <li>Upload audio (WAV / MP3 / FLAC)</li>
    <li>Chuẩn hoá về <strong>mono – 16kHz – WAV</strong></li>
    <li>Speech-to-Text bằng <strong>Whisper</strong> hoặc <strong>PhoWhisper</strong></li>
    <li>Xử lý audio dài bằng <strong>chunking</strong></li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ==========================
# Helper Functions
# ==========================
def normalize_audio_to_wav(audio_path: str, target_sr: int = 16000):
    """Load audio -> mono 16kHz WAV PCM16"""
    y, sr = librosa.load(audio_path, sr=target_sr, mono=True)
    
    # Normalize peak
    peak = float(np.max(np.abs(y))) if y.size else 0.0
    if peak > 0:
        y = y / peak
    
    # Save to temporary WAV file
    out_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    out_wav.close()
    sf.write(out_wav.name, y, target_sr, subtype="PCM_16")
    
    return out_wav.name, target_sr, y

def chunk_signal(y: np.ndarray, sr: int, chunk_seconds: int):
    """Chia audio thành các chunks"""
    total_samples = len(y)
    chunk_len = int(chunk_seconds * sr)
    
    if chunk_len <= 0 or total_samples == 0:
        return [(0, total_samples)]
    
    ranges = []
    for start in range(0, total_samples, chunk_len):
        end = min(start + chunk_len, total_samples)
        ranges.append((start, end))
    
    return ranges

def format_timestamp(seconds: float) -> str:
    """Format timestamp từ seconds sang MM:SS"""
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"

# ==========================
# Upload audio
# ==========================
audio_file = st.file_uploader(
    "📤 Upload audio",
    type=["wav", "mp3", "flac", "m4a", "ogg"],
)

if audio_file is None:
    st.info("Vui lòng upload file audio để bắt đầu.")
    render_footer()
    st.stop()

# Save uploaded file to temporary location
suffix = "." + audio_file.name.split(".")[-1].lower()
with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
    tmp.write(audio_file.read())
    raw_path = tmp.name

# ==========================
# Options
# ==========================
st.subheader("⚙️ Tuỳ chọn")

col1, col2, col3 = st.columns(3)

with col1:
    model_type = st.selectbox(
        "Mô hình ASR",
        ["Whisper", "PhoWhisper"],
        index=0,
    )

with col2:
    lang_mode = st.selectbox(
        "Ngôn ngữ",
        ["Auto-detect", "Vietnamese (vi)", "English (en)"],
        index=0,
    )

with col3:
    chunk_seconds = st.selectbox(
        "Độ dài mỗi đoạn (giây)",
        [15, 30, 45, 60],
        index=1,
    )

# Model size selection
if model_type == "Whisper":
    model_size = st.selectbox(
        "Kích thước mô hình Whisper",
        ["tiny", "base", "small", "medium", "large"],
        index=1,
    )
else:  # PhoWhisper
    model_size = st.selectbox(
        "Kích thước mô hình PhoWhisper",
        ["small", "medium", "base"],
        index=1,
    )

# ==========================
# Normalize
# ==========================
st.subheader("🧼 Chuẩn hoá audio")
with st.spinner("Đang chuẩn hoá audio..."):
    norm_path, sr, y = normalize_audio_to_wav(raw_path)

duration = librosa.get_duration(y=y, sr=sr)
st.success(f"✅ Chuẩn hoá xong | Duration: {duration:.2f}s | Sample Rate: {sr} Hz")

# Display audio player
st.audio(open(norm_path, "rb").read(), format='audio/wav')

# Audio info
audio_info = get_audio_info(y, sr)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Độ dài", f"{audio_info['duration']:.2f} giây")
with col2:
    st.metric("Sample Rate", f"{sr} Hz")
with col3:
    st.metric("Số mẫu", f"{len(y):,}")

# ==========================
# Visualization
# ==========================
st.subheader("📈 Waveform")
fig = plot_waveform(y, sr, title="Waveform")
st.pyplot(fig)

# ==========================
# Speech-to-Text
# ==========================
st.markdown("---")
st.subheader("🧠 Speech-to-Text")

lang_param = None
if lang_mode == "Vietnamese (vi)":
    lang_param = "vi"
elif lang_mode == "English (en)":
    lang_param = "en"

ranges = chunk_signal(y, sr, int(chunk_seconds))
st.write(f"🔹 Số đoạn: **{len(ranges)}**")

if st.button("▶️ Thực hiện Speech-to-Text", type="primary"):
    progress_bar = st.progress(0.0)
    status_text = st.empty()
    
    transcripts = []
    detected_lang = None
    
    # Load model
    if model_type == "Whisper":
        model, device = load_whisper_model(model_size)
        if model is None:
            st.error("❌ Không thể load Whisper model!")
            st.stop()
    else:  # PhoWhisper
        model = load_phowhisper_model(model_size)
        if model is None:
            st.error("❌ Không thể load PhoWhisper model!")
            st.stop()
    
    # Process each chunk
    for i, (s0, s1) in enumerate(ranges, start=1):
        chunk_y = y[s0:s1]
        
        # Save chunk to temporary file
        tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp_wav.close()
        sf.write(tmp_wav.name, chunk_y, sr, subtype="PCM_16")
        
        status_text.text(f"Đang xử lý đoạn {i}/{len(ranges)}...")
        
        # Transcribe chunk
        text = ""
        if model_type == "Whisper":
            result = transcribe_audio(
                model, 
                tmp_wav.name, 
                sr=sr, 
                language=lang_param if lang_param else None,
                verbose=False
            )
            if result:
                text = result.get("text", "").strip()
                if detected_lang is None:
                    detected_lang = result.get("language")
        else:  # PhoWhisper
            result = transcribe_phowhisper(model, tmp_wav.name, sr=sr)
            if result and result.get("text"):
                text = result.get("text", "").strip()
                detected_lang = "vi"  # PhoWhisper is Vietnamese-specific
        
        if text:
            header = f"[{format_timestamp(s0/sr)} - {format_timestamp(s1/sr)}]"
            transcripts.append(f"{header} {text}")
        
        progress_bar.progress(i / len(ranges))
        
        # Clean up temporary file
        try:
            os.unlink(tmp_wav.name)
        except:
            pass
    
    # Clean up normalized file
    try:
        os.unlink(norm_path)
        os.unlink(raw_path)
    except:
        pass
    
    if lang_mode == "Auto-detect" and detected_lang:
        st.info(f"🌍 Ngôn ngữ phát hiện: **{detected_lang}**")
    
    full_text = "\n".join(transcripts)
    
    if full_text:
        st.success("✅ Hoàn thành Speech-to-Text")
        
        edited_text = st.text_area(
            "📝 Transcript",
            value=full_text,
            height=300,
        )
        
        st.download_button(
            "⬇️ Tải transcript (.txt)",
            data=edited_text,
            file_name="transcript.txt",
            mime="text/plain",
        )
        
        # Statistics
        word_count = len(edited_text.split())
        char_count = len(edited_text)
        st.info(f"📊 Thống kê: **{word_count}** từ, **{char_count}** ký tự")
    else:
        st.warning("⚠️ Không có transcript được tạo ra. Vui lòng thử lại.")

st.markdown("---")

# Footer
render_footer()
