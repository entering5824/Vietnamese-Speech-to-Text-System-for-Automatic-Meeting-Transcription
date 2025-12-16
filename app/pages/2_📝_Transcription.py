"""
Transcription Page
Chạy ASR (speech to text) với model selection và transcript editor
"""
import streamlit as st
import os
import sys
import tempfile
import soundfile as sf
import numpy as np
import re

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.components.layout import apply_custom_css
from app.components.transcript_editor import render_transcript_editor
from core.asr.model_registry import (
    get_all_models, get_model_info, check_model_dependencies, get_recommended_models
)
from core.asr.transcription_service import (
    load_whisper_model, transcribe_audio, format_transcript, get_transcript_statistics
)
from core.asr.phowhisper_service import (
    load_phowhisper_model, transcribe_phowhisper
)
from core.audio.audio_processor import chunk_signal, format_timestamp
from core.audio.ffmpeg_setup import ensure_ffmpeg

# Setup FFmpeg
ensure_ffmpeg(silent=True)

# Apply custom CSS
apply_custom_css()

# Page config
st.set_page_config(
    page_title="Transcription - Vietnamese Speech to Text",
    page_icon="📝",
    layout="wide"
)

# Initialize session state
for key, default in (
    ("audio_data", None),
    ("audio_sr", None),
    ("audio_info", None),
    ("transcript_result", None),
    ("transcript_text", ""),
    ("transcript_segments", []),
):
    st.session_state.setdefault(key, default)

st.header("📝 Transcription")

# Check if audio is available
if st.session_state.audio_data is None:
    st.warning("⚠️ Vui lòng upload audio file trước tại trang 'Audio Input'")
    if st.button("🎤 Go to Audio Input", type="primary"):
        st.switch_page("pages/1_🎤_Audio_Input.py")
else:
    # Display audio info
    st.info(f"📊 Audio: {st.session_state.audio_info.get('duration', 0):.2f}s | "
            f"Sample Rate: {st.session_state.audio_sr}Hz")
    
    # Model selection
    st.subheader("🎯 Model Selection")
    
    all_models = get_all_models()
    recommended = get_recommended_models()
    
    # Group models by category
    model_options = []
    for model_id, info in all_models.items():
        name = info["name"]
        is_recommended = info.get("recommended", False)
        is_available, _ = check_model_dependencies(model_id)
        
        display_name = name
        if is_recommended:
            display_name += " 🌟"
        if not is_available:
            display_name += " ⚠️"
        
        model_options.append((model_id, display_name))
    
    # Model selection dropdown
    selected_model_id = st.selectbox(
        "Chọn mô hình ASR:",
        options=[opt[0] for opt in model_options],
        format_func=lambda x: next(opt[1] for opt in model_options if opt[0] == x),
        help="Chọn mô hình để transcribe audio"
    )
    
    # Display model info
    model_info = get_model_info(selected_model_id)
    if model_info:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Loại:** {model_info['type']}")
            st.markdown(f"**Category:** {model_info['category']}")
        with col2:
            if model_info.get("recommended"):
                st.success("🌟 Khuyến nghị cho tiếng Việt")
            if not model_info.get("vietnamese_support"):
                st.warning("⚠️ Chủ yếu cho tiếng Anh")
        
        st.info(f"💡 {model_info.get('description', '')}")
        
        # Check dependencies
        is_available, missing_deps = check_model_dependencies(selected_model_id)
        if not is_available:
            st.error(f"❌ Model chưa sẵn sàng. Thiếu dependencies: {', '.join(missing_deps)}")
    
    # Model size selection
    model_size = None
    if model_info and model_info.get("sizes"):
        default_idx = 0
        if model_info.get("default_size"):
            try:
                default_idx = model_info["sizes"].index(model_info["default_size"])
            except:
                pass
        
        model_size = st.selectbox(
            f"Chọn kích thước {model_info['name']}:",
            model_info["sizes"],
            index=default_idx,
            help="Model lớn hơn thường chính xác hơn nhưng chậm hơn"
        )
    
    # Advanced options (collapsed)
    with st.expander("⚙️ Advanced Options"):
        enable_chunk = st.checkbox("Xử lý audio dài bằng chunking", value=True)
        chunk_seconds = st.selectbox(
            "Độ dài mỗi chunk (giây)",
            [15, 30, 45, 60, 90, 120],
            index=2,
            help="Chia audio dài thành các đoạn nhỏ để tránh hết bộ nhớ"
        )
        with_timestamps = st.checkbox("Hiển thị timestamps", value=True)
    
    # Transcribe button
    if st.button("🚀 Bắt đầu Transcription", type="primary", use_container_width=True):
        if not is_available:
            st.error("❌ Model chưa sẵn sàng. Vui lòng cài đặt dependencies trước.")
        else:
            with st.spinner(f"Đang transcribe với {model_info['name']}... (có thể mất vài phút)"):
                result = None
                model_obj = None
                transcripts = []
                temp_files = []
                
                try:
                    def transcribe_chunked_with_whisper(model_obj, language):
                        ranges = chunk_signal(
                            st.session_state.audio_data, 
                            st.session_state.audio_sr, 
                            int(chunk_seconds)
                        ) if enable_chunk else [(0, len(st.session_state.audio_data))]
                        
                        progress = st.progress(0.0)
                        temp_files = []
                        
                        try:
                            for idx, (s0, s1) in enumerate(ranges, start=1):
                                chunk_y = st.session_state.audio_data[s0:s1]
                                
                                # Create temp file - Windows-safe: create, close, then write
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                                    tmp_name = tmp_file.name
                                temp_files.append(tmp_name)
                                
                                # Write audio data
                                sf.write(tmp_name, chunk_y, st.session_state.audio_sr)
                                
                                # CRITICAL: Verify file exists and is readable before transcribe
                                if not os.path.exists(tmp_name):
                                    st.error(f"❌ Temp file không tồn tại: {tmp_name}")
                                    continue
                                
                                # Verify file is readable (Windows file lock check)
                                try:
                                    with open(tmp_name, 'rb') as test_file:
                                        test_file.read(1)  # Try to read 1 byte
                                except Exception as file_err:
                                    st.error(f"❌ Không thể đọc temp file: {tmp_name}. Lỗi: {file_err}")
                                    import time
                                    time.sleep(0.1)  # Wait a bit and retry once
                                    try:
                                        with open(tmp_name, 'rb') as test_file2:
                                            test_file2.read(1)
                                    except:
                                        st.error(f"❌ Vẫn không đọc được file sau retry. Có thể do Windows file lock.")
                                        continue
                                
                                # Now safe to transcribe
                                chunk_res = transcribe_audio(
                                    model_obj, tmp_name, sr=st.session_state.audio_sr,
                                    language=language, task="transcribe"
                                )
                                
                                # Clean up immediately after use
                                try:
                                    if os.path.exists(tmp_name):
                                        os.unlink(tmp_name)
                                        if tmp_name in temp_files:
                                            temp_files.remove(tmp_name)
                                except Exception as cleanup_err:
                                    # File might still be in use, will cleanup in finally
                                    pass
                                
                                if chunk_res and chunk_res.get("text"):
                                    start_ts = format_timestamp(s0 / st.session_state.audio_sr)
                                    end_ts = format_timestamp(s1 / st.session_state.audio_sr)
                                    transcripts.append(f"[{start_ts} - {end_ts}] {chunk_res.get('text','').strip()}")
                                
                                progress.progress(idx / len(ranges))
                            
                            return {"text": "\n".join(transcripts), "segments": []}
                        finally:
                            # Cleanup remaining temp files (with retry for Windows)
                            import time
                            for tmp_name in temp_files:
                                for retry in range(3):
                                    try:
                                        if os.path.exists(tmp_name):
                                            os.unlink(tmp_name)
                                        break
                                    except Exception:
                                        if retry < 2:
                                            time.sleep(0.2)
                                        else:
                                            st.warning(f"⚠️ Không thể xóa temp file: {tmp_name}")
                    
                    def transcribe_chunked_with_phowhisper(model_obj):
                        ranges = chunk_signal(
                            st.session_state.audio_data,
                            st.session_state.audio_sr,
                            int(chunk_seconds)
                        ) if enable_chunk else [(0, len(st.session_state.audio_data))]
                        
                        progress = st.progress(0.0)
                        temp_files = []
                        
                        try:
                            for idx, (s0, s1) in enumerate(ranges, start=1):
                                chunk_y = st.session_state.audio_data[s0:s1]
                                
                                # Create temp file - Windows-safe: create, close, then write
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                                    tmp_name = tmp_file.name
                                temp_files.append(tmp_name)
                                
                                # Write audio data
                                sf.write(tmp_name, chunk_y, st.session_state.audio_sr)
                                
                                # CRITICAL: Verify file exists and is readable before transcribe
                                if not os.path.exists(tmp_name):
                                    st.error(f"❌ Temp file không tồn tại: {tmp_name}")
                                    continue
                                
                                # Verify file is readable (Windows file lock check)
                                try:
                                    with open(tmp_name, 'rb') as test_file:
                                        test_file.read(1)  # Try to read 1 byte
                                except Exception as file_err:
                                    st.error(f"❌ Không thể đọc temp file: {tmp_name}. Lỗi: {file_err}")
                                    import time
                                    time.sleep(0.1)  # Wait a bit and retry once
                                    try:
                                        with open(tmp_name, 'rb') as test_file2:
                                            test_file2.read(1)
                                    except:
                                        st.error(f"❌ Vẫn không đọc được file sau retry. Có thể do Windows file lock.")
                                        continue
                                
                                # Now safe to transcribe
                                chunk_res = transcribe_phowhisper(
                                    model_obj, tmp_name, sr=st.session_state.audio_sr, language="vi"
                                )
                                
                                # Clean up immediately after use
                                try:
                                    if os.path.exists(tmp_name):
                                        os.unlink(tmp_name)
                                        if tmp_name in temp_files:
                                            temp_files.remove(tmp_name)
                                except Exception as cleanup_err:
                                    # File might still be in use, will cleanup in finally
                                    pass
                                
                                if chunk_res and chunk_res.get("text"):
                                    start_ts = format_timestamp(s0 / st.session_state.audio_sr)
                                    end_ts = format_timestamp(s1 / st.session_state.audio_sr)
                                    transcripts.append(f"[{start_ts} - {end_ts}] {chunk_res.get('text','').strip()}")
                                
                                progress.progress(idx / len(ranges))
                            
                            return {"text": "\n".join(transcripts), "segments": []}
                        finally:
                            # Cleanup remaining temp files (with retry for Windows)
                            import time
                            for tmp_name in temp_files:
                                for retry in range(3):
                                    try:
                                        if os.path.exists(tmp_name):
                                            os.unlink(tmp_name)
                                        break
                                    except Exception:
                                        if retry < 2:
                                            time.sleep(0.2)
                                        else:
                                            st.warning(f"⚠️ Không thể xóa temp file: {tmp_name}")
                    
                    # Load and transcribe
                    if selected_model_id == "whisper":
                        model_obj, device = load_whisper_model(model_size)
                        if model_obj:
                            result = transcribe_chunked_with_whisper(model_obj, language="vi")
                        else:
                            st.error("❌ Không thể load Whisper model!")
                    
                    elif selected_model_id == "phowhisper":
                        model_obj = load_phowhisper_model(model_size)
                        if model_obj:
                            result = transcribe_chunked_with_phowhisper(model_obj)
                        else:
                            st.error("❌ Không thể load PhoWhisper model!")
                    
                    if result:
                        st.session_state.transcript_result = result
                        text_out = result.get("text", "") if isinstance(result, dict) else ""
                        
                        if with_timestamps:
                            st.session_state.transcript_text = text_out or format_transcript(
                                result, with_timestamps=True
                            )
                        else:
                            # Remove timestamps
                            text_out = re.sub(r'\[.*?\]\s*', '', text_out)
                            st.session_state.transcript_text = text_out
                        
                        st.session_state.transcript_segments = result.get("segments", [])
                        
                        st.success("✅ Transcription hoàn tất!")
                        st.rerun()
                    elif model_obj is None:
                        st.error("❌ Không thể load model!")
                
                except OSError as os_err:
                    # WinError 2 - File not found
                    error_msg = str(os_err)
                    if getattr(os_err, 'winerror', None) == 2 or os_err.errno == 2 or 'cannot find the file' in error_msg.lower():
                        st.error("🔴 WINERROR 2: File không tìm thấy!")
                        st.error(f"❌ {error_msg}")
                        st.warning("""
                        **Nguyên nhân thường gặp trên Windows:**
                        1. **File tạm bị xóa trước khi model đọc** - Đã được xử lý trong code
                        2. **FFmpeg không tìm thấy** - Kiểm tra FFmpeg setup
                        3. **File path có ký tự đặc biệt** - Đã dùng temp file an toàn
                        4. **Windows file lock** - Đã thêm retry mechanism
                        
                        **Khắc phục:**
                        - Kiểm tra FFmpeg: Đảm bảo `imageio-ffmpeg` đã được cài
                        - Restart ứng dụng
                        - Thử với file audio khác
                        """)
                        with st.expander("🔍 Debug Info"):
                            st.write("**FFmpeg Status:**")
                            try:
                                from core.audio.ffmpeg_setup import get_ffmpeg_info
                                st.json(get_ffmpeg_info())
                            except:
                                st.write("Không thể lấy FFmpeg info")
                            st.write("**Python Version:**", sys.version)
                            st.write("**Platform:**", sys.platform)
                    else:
                        st.error(f"❌ Lỗi OS: {error_msg}")
                        import traceback
                        with st.expander("🔍 Chi tiết lỗi"):
                            st.code(traceback.format_exc())
                except Exception as e:
                    error_msg = str(e)
                    st.error(f"❌ Lỗi khi transcribe: {error_msg}")
                    
                    # Check for common Windows errors
                    if "WinError 2" in error_msg or "cannot find the file" in error_msg.lower():
                        st.error("🔴 WINERROR 2 PHÁT HIỆN!")
                        st.warning("""
                        **Đây là lỗi Windows phổ biến. Các nguyên nhân:**
                        1. File không tồn tại hoặc đã bị xóa
                        2. FFmpeg không tìm thấy
                        3. Path có vấn đề
                        
                        **Đã thử:**
                        - Tạo temp file an toàn
                        - Kiểm tra file tồn tại trước khi transcribe
                        - Retry mechanism cho file lock
                        """)
                    
                    import traceback
                    with st.expander("🔍 Chi tiết lỗi"):
                        st.code(traceback.format_exc())
    
    # Display transcript
    if st.session_state.transcript_text:
        st.markdown("---")
        st.subheader("📝 Transcript")
        
        # Display transcript
        st.text_area(
            "Kết quả transcription:",
            st.session_state.transcript_text,
            height=300,
            key="transcript_display",
            disabled=True
        )
        
        # Editor
        edited_text, formatting_options = render_transcript_editor(
            st.session_state.transcript_text,
            key_prefix="transcript"
        )
        
        if st.button("💾 Lưu thay đổi", type="primary"):
            st.session_state.transcript_text = edited_text
            st.success("✅ Đã lưu thay đổi!")
            st.rerun()
        
        # Next steps
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("👥 Go to Speaker Diarization", use_container_width=True):
                st.switch_page("pages/3_👥_Speaker_Diarization.py")
        
        with col2:
            if st.button("✨ Go to Post-Processing", use_container_width=True):
                st.switch_page("pages/4_✨_Post_Processing.py")

