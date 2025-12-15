| Nhóm                                  | Mô hình          | Loại                | Phù hợp để học             |
| ------------------------------------- | ---------------- | ------------------- | -------------------------- |
| **Truyền thống**                      | Kaldi (HMM-GMM)  | HMM                 | Hiểu nền tảng ASR          |
| **End-to-end CTC cơ bản**             | DeepSpeech 2     | CTC                 | Hiểu CTC & decoding        |
| **Conv-based**                        | Wav2Letter++     | CNN                 | Tốc độ, kiến trúc đơn giản |
|                                       | QuartzNet (NeMo) | CNN                 | Mạnh & nhẹ nhất trong CNN  |
| **Transformer-based self-supervised** | Wav2Vec 2.0      | SSL                 | Hiện đại, accuracy cao     |
| **Nhiều ngôn ngữ SOTA**               | Whisper          | Transformer seq2seq | Benchmark chuẩn            |
| **Tiếng Việt chuyên biệt**            | PhoWhisper       | Whisper fine-tune   | Accuracy tiếng Việt cao    |
