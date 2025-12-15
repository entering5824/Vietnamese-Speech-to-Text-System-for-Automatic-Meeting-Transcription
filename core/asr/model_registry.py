"""
Model Registry
Quản lý tất cả ASR models và metadata
"""
from typing import Dict, List, Optional

MODELS: Dict[str, Dict] = {
    "whisper": {
        "name": "Whisper",
        "type": "Transformer seq2seq",
        "category": "Nhiều ngôn ngữ SOTA",
        "service": "transcription_service",
        "sizes": ["tiny", "base", "small", "medium", "large"],
        "default_size": "base",
        "description": "Mô hình đa ngôn ngữ từ OpenAI, benchmark chuẩn cho ASR",
        "recommended": False,
        "vietnamese_support": True,
        "dependencies": ["openai-whisper", "torch"]
    },
    "phowhisper": {
        "name": "PhoWhisper",
        "type": "Whisper fine-tune",
        "category": "Tiếng Việt chuyên biệt",
        "service": "phowhisper_service",
        "sizes": ["small", "medium", "base"],
        "default_size": "medium",
        "description": "Whisper được fine-tune đặc biệt cho tiếng Việt, độ chính xác cao",
        "recommended": True,
        "vietnamese_support": True,
        "dependencies": ["transformers", "torch"]
    },
    "wav2vec2": {
        "name": "Wav2Vec 2.0",
        "type": "Transformer-based self-supervised",
        "category": "Transformer-based self-supervised",
        "service": "wav2vec2_service",
        "sizes": ["base", "large"],
        "default_size": "base",
        "description": "Mô hình self-supervised learning, hiện đại và accuracy cao",
        "recommended": False,
        "vietnamese_support": False,  # Cần fine-tuned model
        "dependencies": ["transformers", "torch"]  # Không cần datasets
    },
    "deepspeech2": {
        "name": "DeepSpeech 2",
        "type": "CTC",
        "category": "End-to-end CTC cơ bản",
        "service": "deepspeech2_service",
        "sizes": ["default"],
        "default_size": "default",
        "description": "Mô hình CTC cơ bản, dễ hiểu về CTC và decoding",
        "recommended": False,
        "vietnamese_support": False,  # Cần model tiếng Việt
        "dependencies": ["deepspeech"]  # hoặc mozilla-deepspeech
    },
    "quartznet": {
        "name": "QuartzNet",
        "type": "CNN",
        "category": "Conv-based",
        "service": "quartznet_service",
        "sizes": ["15x5", "5x5"],
        "default_size": "15x5",
        "description": "Mô hình CNN mạnh và nhẹ nhất trong các CNN-based models",
        "recommended": False,
        "vietnamese_support": False,  # Cần model tiếng Việt
        "dependencies": ["nemo-toolkit[asr]"]
    },
    "wav2letter": {
        "name": "Wav2Letter++",
        "type": "CNN",
        "category": "Conv-based",
        "service": "wav2letter_service",
        "sizes": ["default"],
        "default_size": "default",
        "description": "Mô hình CNN, tốc độ nhanh, kiến trúc đơn giản",
        "recommended": False,
        "vietnamese_support": False,  # Cần model tiếng Việt
        "dependencies": []  # Cần build từ source hoặc Docker
    },
    "kaldi": {
        "name": "Kaldi",
        "type": "HMM-GMM",
        "category": "Truyền thống",
        "service": "kaldi_service",
        "sizes": ["default"],
        "default_size": "default",
        "description": "HMM-GMM truyền thống, hiểu nền tảng ASR",
        "recommended": False,
        "vietnamese_support": False,  # Cần acoustic và language model
        "dependencies": []  # Cần cài đặt thủ công Kaldi toolkit
    }
}

def get_model_info(model_id: str) -> Optional[Dict]:
    """Lấy thông tin model theo ID"""
    return MODELS.get(model_id)

def get_all_models() -> Dict[str, Dict]:
    """Lấy tất cả models"""
    return MODELS

def get_available_models() -> List[str]:
    """Lấy danh sách model IDs"""
    return list(MODELS.keys())

def get_recommended_models() -> List[str]:
    """Lấy danh sách models được khuyến nghị"""
    return [model_id for model_id, info in MODELS.items() if info.get("recommended", False)]

def get_models_by_category() -> Dict[str, List[str]]:
    """Nhóm models theo category"""
    categories = {}
    for model_id, info in MODELS.items():
        category = info.get("category", "Other")
        if category not in categories:
            categories[category] = []
        categories[category].append(model_id)
    return categories

def check_model_dependencies(model_id: str):
    """
    Kiểm tra dependencies của model
    
    Returns:
        (is_available, missing_dependencies)
    """
    model_info = get_model_info(model_id)
    if not model_info:
        return False, []
    
    dependencies = model_info.get("dependencies", [])
    missing = []
    
    for dep in dependencies:
        try:
            if dep == "openai-whisper":
                import whisper
            elif dep == "transformers":
                import transformers
            elif dep == "torch":
                import torch
            elif dep == "deepspeech":
                import deepspeech
            elif dep == "nemo-toolkit[asr]":
                import nemo
            # datasets đã được loại bỏ khỏi dependencies vì không cần thiết
            # và có thể gây lỗi với Python 3.13
            # Add more dependency checks as needed
        except (ImportError, SyntaxError, IndentationError, AttributeError, Exception) as e:
            # Bắt tất cả exception để tránh crash khi check dependencies
            missing.append(dep)
    
    return len(missing) == 0, missing

