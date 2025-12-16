"""
Module setup FFmpeg sử dụng imageio-ffmpeg
Tự động tải và cấu hình portable FFmpeg cho Streamlit Cloud
Sử dụng imageio-ffmpeg: portable FFmpeg binary không cần system installation
Chỉ cần ffmpeg cho whisper, không cần ffprobe (pipeline không dùng pydub)
"""
import os
import sys
import subprocess
import shutil
from typing import Optional, Tuple

def get_ffmpeg_path() -> Optional[str]:
    """
    Lấy đường dẫn FFmpeg executable
    Ưu tiên: system FFmpeg (từ packages.txt trên Streamlit Cloud) > imageio-ffmpeg
    
    Returns:
        Đường dẫn FFmpeg hoặc None nếu không tìm thấy
    """
    # First, check if ffmpeg is available in system PATH (important for Streamlit Cloud)
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        # Verify it works
        try:
            result = subprocess.run(
                [system_ffmpeg, '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return system_ffmpeg
        except:
            pass
    
    # Fallback to imageio-ffmpeg (portable version)
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return None

def verify_ffmpeg(ffmpeg_path: str) -> Tuple[bool, str]:
    """
    Verify FFmpeg có hoạt động không
    
    Args:
        ffmpeg_path: Đường dẫn đến FFmpeg executable
    
    Returns:
        Tuple (success: bool, message: str)
    """
    try:
        result = subprocess.run(
            [ffmpeg_path, '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0] if result.stdout else "Unknown version"
            return True, f"FFmpeg hoạt động: {version_line}"
        else:
            return False, f"FFmpeg không hoạt động (return code: {result.returncode})"
    except subprocess.TimeoutExpired:
        return False, "FFmpeg timeout khi kiểm tra"
    except FileNotFoundError:
        return False, f"Không tìm thấy FFmpeg tại: {ffmpeg_path}"
    except Exception as e:
        return False, f"Lỗi khi kiểm tra FFmpeg: {str(e)}"

def check_ffmpeg_in_path() -> Tuple[bool, Optional[str]]:
    """
    Kiểm tra xem FFmpeg có trong PATH không
    Sử dụng shutil.which() để tìm FFmpeg trên hệ thống (hoạt động tốt trên cả Windows và Linux)
    
    Returns:
        Tuple (found: bool, path: Optional[str])
    """
    # First, try shutil.which() - cross-platform and reliable
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        # Verify it actually works
        try:
            result = subprocess.run(
                [ffmpeg_path, '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, ffmpeg_path
        except:
            pass
    
    # Fallback: try running ffmpeg directly (for cases where shutil.which doesn't find it but it's still in PATH)
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Try to find the actual path
            which_result = shutil.which("ffmpeg")
            if which_result:
                return True, which_result
            # Last resort: use platform-specific which/where
            try:
                which_cmd = 'where' if sys.platform == 'win32' else 'which'
                which_result = subprocess.run(
                    [which_cmd, 'ffmpeg'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if which_result.returncode == 0:
                    return True, which_result.stdout.strip()
            except:
                pass
    except:
        pass
    
    return False, None

def setup_ffmpeg(silent=False, verbose=False) -> Tuple[bool, dict]:
    """
    Setup FFmpeg từ imageio-ffmpeg
    
    Args:
        silent: Nếu True, không hiển thị thông báo
        verbose: Nếu True, trả về thông tin chi tiết
    
    Returns:
        Tuple (success: bool, info: dict)
    """
    info = {
        "ffmpeg_path": None,
        "ffmpeg_dir": None,
        "in_path": False,
        "verified": False,
        "error": None,
        "env_vars_set": False
    }
    
    try:
        # First, try to get system FFmpeg (from packages.txt on Streamlit Cloud)
        system_ffmpeg = shutil.which("ffmpeg")
        if system_ffmpeg:
            # Verify system FFmpeg works
            verified_system, verify_msg_system = verify_ffmpeg(system_ffmpeg)
            if verified_system:
                ffmpeg_path = system_ffmpeg
                info["ffmpeg_path"] = ffmpeg_path
                info["ffmpeg_dir"] = os.path.dirname(ffmpeg_path)
                info["source"] = "system"
            else:
                # System FFmpeg found but doesn't work, fallback to imageio-ffmpeg
                system_ffmpeg = None
        else:
            system_ffmpeg = None
        
        # If system FFmpeg not available, use imageio-ffmpeg
        if not system_ffmpeg:
            import imageio_ffmpeg
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            info["ffmpeg_path"] = ffmpeg_path
            info["ffmpeg_dir"] = os.path.dirname(ffmpeg_path)
            info["source"] = "imageio-ffmpeg"
        
        # Verify FFmpeg
        verified, verify_msg = verify_ffmpeg(ffmpeg_path)
        info["verified"] = verified
        if not verified:
            info["error"] = verify_msg
        
        # Set environment variables
        os.environ["FFMPEG_BINARY"] = ffmpeg_path
        os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_path
        os.environ["LIBROSA_FFMPEG_BINARY"] = ffmpeg_path
        info["env_vars_set"] = True
        
        # Thêm vào PATH
        ffmpeg_dir = os.path.dirname(ffmpeg_path)
        current_path = os.environ.get("PATH", "")
        if ffmpeg_dir not in current_path:
            os.environ["PATH"] = current_path + os.pathsep + ffmpeg_dir
        
        # Kiểm tra xem có trong PATH không
        in_path, path_location = check_ffmpeg_in_path()
        info["in_path"] = in_path
        if path_location:
            info["path_location"] = path_location
        
        if not silent:
            if verified:
                try:
                    import streamlit as st
                    st.success("✅ FFmpeg đã được cấu hình thành công!")
                    if verbose:
                        st.info(f"📍 Path: {ffmpeg_path}")
                except:
                    print("✅ FFmpeg đã được cấu hình thành công!")
            else:
                try:
                    import streamlit as st
                    st.warning(f"⚠️ FFmpeg được setup nhưng: {verify_msg}")
                except:
                    print(f"⚠️ FFmpeg được setup nhưng: {verify_msg}")
        
        return verified, info
            
    except ImportError:
        error_msg = "Không tìm thấy imageio-ffmpeg"
        info["error"] = error_msg
        if not silent:
            try:
                import streamlit as st
                st.error(f"❌ {error_msg}. Vui lòng cài đặt: pip install imageio-ffmpeg")
            except:
                print(f"❌ {error_msg}. Vui lòng cài đặt: pip install imageio-ffmpeg")
        return False, info
    except Exception as e:
        error_msg = f"Không thể setup FFmpeg: {str(e)}"
        info["error"] = error_msg
        if not silent:
            try:
                import streamlit as st
                st.warning(f"⚠️ {error_msg}")
            except:
                print(f"⚠️ {error_msg}")
        return False, info

# Tự động setup khi import
_ffmpeg_setup_done = False
_ffmpeg_info = None

def ensure_ffmpeg(silent=True, verbose=False) -> Tuple[bool, dict]:
    """
    Đảm bảo FFmpeg đã được setup
    
    Args:
        silent: Nếu True, không hiển thị thông báo khi setup
        verbose: Nếu True, trả về thông tin chi tiết
    
    Returns:
        Tuple (success: bool, info: dict)
    """
    global _ffmpeg_setup_done, _ffmpeg_info
    
    if not _ffmpeg_setup_done:
        success, info = setup_ffmpeg(silent=silent, verbose=verbose)
        _ffmpeg_setup_done = True
        _ffmpeg_info = info
        return success, info
    else:
        return _ffmpeg_info.get("verified", False) if _ffmpeg_info else False, _ffmpeg_info or {}

def get_ffmpeg_info() -> dict:
    """Lấy thông tin FFmpeg hiện tại"""
    global _ffmpeg_info
    if _ffmpeg_info:
        return _ffmpeg_info.copy()
    
    # Nếu chưa setup, setup ngay
    ensure_ffmpeg(silent=True)
    return _ffmpeg_info or {}
