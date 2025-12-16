# Hướng dẫn Deployment

Hướng dẫn chi tiết để triển khai Vietnamese Speech-to-Text System lên cloud và chạy local.

## Mục lục

1. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
2. [Docker Deployment](#docker-deployment)
3. [Local Development](#local-development)
4. [FastAPI Server](#fastapi-server)
5. [Troubleshooting](#troubleshooting)

---

## Streamlit Cloud Deployment

### Yêu cầu

- GitHub repository (public hoặc private với Streamlit Cloud Team plan)
- Tài khoản Streamlit Cloud (miễn phí)

### Các bước triển khai

1. **Push code lên GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Deploy trên Streamlit Cloud**
   - Truy cập [share.streamlit.io](https://share.streamlit.io)
   - Đăng nhập với GitHub account
   - Click "New app"
   - Chọn repository và branch
   - **Main file path**: `main.py`
   - Click "Deploy"

3. **Cấu hình (Optional)**
   - Vào Settings của app trên Streamlit Cloud
   - Có thể cấu hình:
     - Secrets (environment variables)
     - Resource limits
     - Custom domain

### Lưu ý cho Streamlit Cloud

- **FFmpeg**: Tự động được setup qua `imageio-ffmpeg`, không cần cấu hình thêm
- **Model caching**: Models sẽ được cache tự động trong `/root/.cache`
- **Memory limits**: 
  - Free tier: ~1GB RAM (chỉ dùng Whisper tiny/base)
  - Team tier: Có thể dùng model lớn hơn
- **File upload**: Giới hạn 200MB mặc định (có thể điều chỉnh trong `.streamlit/config.toml`)

### Environment Variables (Secrets)

Trong Streamlit Cloud Settings > Secrets, có thể thêm:

```toml
[secrets]
DEFAULT_WHISPER_MODEL = "base"
DEFAULT_PHOWHISPER_MODEL = "medium"
HF_TOKEN = "your_huggingface_token"  # Nếu cần private models
```

---

## Docker Deployment

### Build và chạy với Docker

1. **Build image**
   ```bash
   docker build -t vietnamese-stt:latest .
   ```

2. **Chạy container**
   ```bash
   docker run -d \
     -p 8501:8501 \
     --name vietnamese-stt \
     -v $(pwd)/models:/app/models \
     vietnamese-stt:latest
   ```

3. **Truy cập app**
   - Mở browser tại `http://localhost:8501`

### Docker Compose (Khuyến nghị cho local development)

1. **Chạy với docker-compose**
   ```bash
   docker-compose up -d
   ```

2. **Xem logs**
   ```bash
   docker-compose logs -f streamlit-app
   ```

3. **Dừng services**
   ```bash
   docker-compose down
   ```

### Deploy Docker lên Cloud Platforms

#### Railway

1. Tạo account trên [Railway](https://railway.app)
2. New Project > Deploy from GitHub
3. Chọn repository
4. Railway sẽ tự động detect Dockerfile
5. Deploy!

#### Render

1. Tạo account trên [Render](https://render.com)
2. New > Web Service
3. Connect GitHub repository
4. Settings:
   - **Build Command**: `docker build -t app .`
   - **Start Command**: `docker run -p $PORT:8501 app`
   - **Environment**: Add any needed env vars

#### AWS/GCP/Azure

Sử dụng container services:
- **AWS**: ECS, EKS, or App Runner
- **GCP**: Cloud Run, GKE
- **Azure**: Container Instances, AKS

---

## Local Development

### Option 1: Sử dụng Scripts (Khuyến nghị)

#### Linux/Mac
```bash
chmod +x scripts/run_local.sh
./scripts/run_local.sh
```

#### Windows
```cmd
scripts\run_local.bat
```

### Option 2: Manual Setup

1. **Tạo virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Cài đặt dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Tạo .env file (optional)**
   ```bash
   # Linux/Mac
   cp env.example .env
   
   # Windows
   copy env.example .env
   
   # Chỉnh sửa .env với các giá trị phù hợp
   ```

4. **Chạy Streamlit app**
   ```bash
   streamlit run app/main.py
   ```

5. **Truy cập app**
   - Mở browser tại `http://localhost:8501`

### Development với Hot Reload

Streamlit tự động reload khi code thay đổi. Để tắt:
- Sửa `.streamlit/config.toml`: `runOnSave = false`

---

## FastAPI Server

### Chạy API Server Local

```bash
# Với uvicorn
uvicorn core.api.server:app --host 0.0.0.0 --port 8000 --reload

# Hoặc với Python
python -m core.api.server
```

### API Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Transcribe Audio
```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@audio.wav" \
  -F "language=vi" \
  -F "diarization=false"
```

#### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Deploy API Server

Có thể deploy FastAPI server riêng biệt:

1. **Với Docker**
   ```bash
   docker run -d \
     -p 8000:8000 \
     --name stt-api \
     vietnamese-stt:latest \
     uvicorn core.api.server:app --host 0.0.0.0 --port 8000
   ```

2. **Với Gunicorn (Production)**
   ```bash
   pip install gunicorn
   gunicorn core.api.server:app \
     --workers 4 \
     --worker-class uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:8000
   ```

---

## Troubleshooting

### Lỗi FFmpeg

**Triệu chứng**: `FFmpeg not found` hoặc audio processing fails

**Giải pháp**:
- FFmpeg được tự động setup qua `imageio-ffmpeg`
- Nếu vẫn lỗi, kiểm tra:
  ```python
  from core.audio.ffmpeg_setup import ensure_ffmpeg
  ensure_ffmpeg(silent=False)  # Xem thông báo
  ```

### Lỗi Model Loading

**Triệu chứng**: Model không load được, timeout

**Giải pháp**:
- Kiểm tra kết nối internet (lần đầu cần tải model)
- Kiểm tra disk space (models có thể lớn)
- Thử model nhỏ hơn (tiny/base thay vì large)
- Kiểm tra memory (PhoWhisper-medium cần ~4-6GB RAM)

### Lỗi Memory trên Cloud

**Triệu chứng**: App crash, out of memory

**Giải pháp**:
- Sử dụng model nhỏ hơn
- Giảm `MAX_UPLOAD_SIZE` trong config
- Upgrade plan (nếu dùng Streamlit Cloud Team)

### Lỗi Port đã được sử dụng

**Triệu chứng**: `Address already in use`

**Giải pháp**:
```bash
# Tìm process đang dùng port
# Linux/Mac
lsof -i :8501

# Windows
netstat -ano | findstr :8501

# Kill process hoặc đổi port trong config
```

### Lỗi Docker Build

**Triệu chứng**: Build fails, dependencies errors

**Giải pháp**:
- Kiểm tra Python version (cần 3.11+)
- Kiểm tra `requirements.txt` có đầy đủ
- Thử build lại với `--no-cache`:
  ```bash
  docker build --no-cache -t vietnamese-stt:latest .
  ```

### Lỗi Import Module

**Triệu chứng**: `ModuleNotFoundError`

**Giải pháp**:
- Đảm bảo đã cài đặt tất cả dependencies: `pip install -r requirements.txt`
- Kiểm tra PYTHONPATH
- Với Docker, đảm bảo code được copy đúng trong Dockerfile

### Performance Issues

**Triệu chứng**: Transcription chậm

**Giải pháp**:
- Sử dụng GPU nếu có (tự động detect)
- Sử dụng model nhỏ hơn cho development
- Giảm audio duration hoặc chunk size
- Kiểm tra CPU/RAM usage

---

## Best Practices

1. **Environment Variables**: Luôn sử dụng `.env` cho local, secrets cho cloud
2. **Model Caching**: Models được cache tự động, không cần tải lại mỗi lần
3. **Resource Monitoring**: Monitor memory và CPU usage trên cloud
4. **Error Handling**: App có error handling, nhưng nên monitor logs
5. **Backup**: Backup models cache nếu cần (có thể lớn)

---

## Support

Nếu gặp vấn đề:
1. Kiểm tra logs (Streamlit Cloud có logs trong dashboard)
2. Kiểm tra [Troubleshooting](#troubleshooting) section
3. Xem documentation trong `docs/` folder
4. Tạo issue trên GitHub repository

