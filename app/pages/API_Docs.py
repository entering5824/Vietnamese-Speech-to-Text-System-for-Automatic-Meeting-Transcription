"""
API Docs Page - mô tả FastAPI endpoint
"""
import streamlit as st
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.components.sidebar import render_sidebar
from app.components.layout import apply_custom_css

apply_custom_css()
render_sidebar()

st.header("🧩 API Docs (FastAPI)")
st.markdown(
    """
Hỗ trợ endpoint `/transcribe` cho upload audio và trả transcript JSON.

**Chạy server (local):**
```bash
uvicorn core.api.server:app --host 0.0.0.0 --port 8000
```

**Request:**
- Method: `POST /transcribe`
- Form data: `file` (UploadFile), optional `diarization` (bool)

**Response (JSON):**
```json
{
  "text": "...",
  "language": "vi",
  "segments": [...],
  "diarization": null
}
```

**Ví dụ curl:**
```bash
curl -X POST \
  -F "file=@sample.wav" \
  http://localhost:8000/transcribe
```

**Health check:** `GET /health`

Ghi chú: Diarization trong API hiện ở dạng stub; có thể tích hợp pyannote nếu có model.
    """
)
