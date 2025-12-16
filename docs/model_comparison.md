# Model Comparison & Selection Guide

## Model Overview

| Nhóm                                  | Mô hình          | Loại                | Phù hợp để học             |
| ------------------------------------- | ---------------- | ------------------- | -------------------------- |
| **Truyền thống**                      | Kaldi (HMM-GMM)  | HMM                 | Hiểu nền tảng ASR          |
| **End-to-end CTC cơ bản**             | DeepSpeech 2     | CTC                 | Hiểu CTC & decoding        |
| **Conv-based**                        | Wav2Letter++     | CNN                 | Tốc độ, kiến trúc đơn giản |
|                                       | QuartzNet (NeMo) | CNN                 | Mạnh & nhẹ nhất trong CNN  |
| **Transformer-based self-supervised** | Wav2Vec 2.0      | SSL                 | Hiện đại, accuracy cao     |
| **Nhiều ngôn ngữ SOTA**               | Whisper          | Transformer seq2seq | Benchmark chuẩn            |
| **Tiếng Việt chuyên biệt**            | PhoWhisper       | Whisper fine-tune   | Accuracy tiếng Việt cao    |

## So sánh Whisper vs PhoWhisper

### Thông tin đánh giá

- **Số file test**: 0
- **Device**: cpu/cuda
- **Whisper model**: large
- **PhoWhisper model**: medium

## Kết quả tổng hợp

| Model | WER (Mean ± Std) | CER (Mean ± Std) |
|-------|------------------|------------------|
| Whisper-large | N/A | N/A |
| PhoWhisper-medium | N/A | N/A |

## Kết quả chi tiết từng file

| File | Whisper WER | Whisper CER | PhoWhisper WER | PhoWhisper CER |
|------|-------------|-------------|----------------|----------------|

## Hướng dẫn chạy đánh giá

Để tạo báo cáo đánh giá, chạy script:

```bash
python evaluate_models.py --test_dir test_audio --whisper_model large --phowhisper_model medium
```

**Yêu cầu:**
- Tạo thư mục `test_audio/` và thêm các file audio test (.wav, .mp3, etc.)
- Mỗi file audio cần có file `.txt` tương ứng chứa reference text (ground truth)
- Ví dụ: `audio1.wav` cần có `audio1.txt`

**Ví dụ cấu trúc thư mục:**
```
test_audio/
├── audio1.wav
├── audio1.txt
├── audio2.wav
├── audio2.txt
└── ...
```

## Kết luận

Báo cáo này sẽ được cập nhật tự động sau khi chạy script đánh giá.

### Khuyến nghị

- Sử dụng **PhoWhisper** cho audio tiếng Việt để đạt độ chính xác tốt nhất
- Sử dụng **Whisper** nếu cần hỗ trợ đa ngôn ngữ

