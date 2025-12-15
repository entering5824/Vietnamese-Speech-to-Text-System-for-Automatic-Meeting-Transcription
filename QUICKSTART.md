# Hướng dẫn nhanh

## Cài đặt nhanh

1. **Cài đặt Python packages** (FFmpeg sẽ tự động tải):
```bash
pip install -r requirements.txt
```

3. **Chạy ứng dụng**:
```bash
streamlit run app/main.py
```

## Sử dụng

1. Mở trình duyệt tại `http://localhost:8501`
2. Chọn tab "📤 Upload & Transcribe"
3. Upload file audio (WAV, MP3, FLAC)
4. **Chọn loại model**: 
   - **PhoWhisper** (🌟 khuyến nghị cho tiếng Việt) - chọn "medium"
   - **Whisper** (đa ngôn ngữ) - chọn "base"
5. Bấm "🚀 Bắt đầu Transcription"
6. Xem kết quả và export nếu cần

## Lưu ý

- Lần đầu chạy sẽ mất thời gian để tải model:
  - Whisper: Model "base" (~150MB) cân bằng tốt giữa tốc độ và độ chính xác
  - PhoWhisper: Model "medium" được tải từ HuggingFace (có thể mất vài phút)
- **PhoWhisper-medium** được khuyến nghị cho audio tiếng Việt (độ chính xác cao hơn Whisper)
- Audio dài sẽ mất nhiều thời gian để xử lý
- GPU sẽ tự động được sử dụng nếu có sẵn

