"""
Home / Dashboard Page
Trang chính với giới thiệu, trạng thái hệ thống, và shortcuts
"""
import streamlit as st
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.components.layout import apply_custom_css
from app.components.status_display import render_status_display
from app.components.footer import render_footer

# Apply custom CSS
apply_custom_css()

# Page config
st.set_page_config(
    page_title="Dashboard - Vietnamese Speech to Text",
    page_icon="🏠",
    layout="wide"
)

# Header
st.markdown(
    '<div class="main-header">🎤 Vietnamese Speech to Text System</div>',
    unsafe_allow_html=True
)

st.markdown("### Hệ thống chuyển đổi giọng nói tiếng Việt thành văn bản tự động")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    #### 📋 Giới thiệu
    
    Hệ thống này cung cấp giải pháp chuyển đổi giọng nói tiếng Việt thành văn bản một cách tự động và chính xác, 
    đặc biệt tối ưu cho việc ghi chép cuộc họp.
    
    **Tính năng chính:**
    - 🎤 Nhận diện giọng nói tiếng Việt với độ chính xác cao
    - 👥 Phân biệt người nói (Speaker Diarization)
    - ✨ Xử lý hậu kỳ với AI (grammar, punctuation)
    - 📊 Thống kê và báo cáo chi tiết
    - 📤 Xuất nhiều định dạng (TXT, DOCX, PDF, JSON)
    
    #### 🚀 Bắt đầu nhanh
    
    1. **Upload Audio**: Chọn file audio hoặc ghi âm trực tiếp
    2. **Transcribe**: Chọn model và chạy nhận diện giọng nói
    3. **Enhance**: Cải thiện chất lượng văn bản với AI
    4. **Export**: Xuất kết quả theo định dạng mong muốn
    """)

with col2:
    st.markdown("#### 🎯 Shortcuts")
    
    if st.button("🎤 Audio Input", use_container_width=True, type="primary"):
        st.switch_page("pages/1_🎤_Audio_Input.py")
    
    if st.button("📝 Transcription", use_container_width=True):
        st.switch_page("pages/2_📝_Transcription.py")
    
    if st.button("👥 Speaker Diarization", use_container_width=True):
        st.switch_page("pages/3_👥_Speaker_Diarization.py")
    
    if st.button("✨ Post-Processing", use_container_width=True):
        st.switch_page("pages/4_✨_Post_Processing.py")
    
    if st.button("📊 Export & Reporting", use_container_width=True):
        st.switch_page("pages/5_📊_Export_Reporting.py")
    
    if st.button("⚙️ Settings", use_container_width=True):
        st.switch_page("pages/6_⚙️_Settings.py")

# System Status
st.markdown("---")
render_status_display()

# Tips & News
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    with st.expander("💡 Tips & Best Practices"):
        st.markdown("""
        - **Chất lượng audio**: Sử dụng microphone chất lượng tốt, giảm tiếng ồn nền
        - **Độ dài file**: Hệ thống hỗ trợ audio dài, tự động chia nhỏ để xử lý
        - **Model selection**: PhoWhisper-medium được khuyến nghị cho tiếng Việt
        - **Speaker diarization**: Hoạt động tốt nhất với 2-4 người nói
        - **Export**: Sử dụng DOCX cho báo cáo chính thức, JSON cho tích hợp API
        """)

with col2:
    with st.expander("🔒 Privacy & Security"):
        st.markdown("""
        - **Xử lý local**: Audio được xử lý trên server, không gửi đến bên thứ ba
        - **Tự động xóa**: File tạm được tự động xóa sau khi xử lý
        - **Bảo mật**: Không lưu trữ audio hoặc transcript trừ khi bạn export
        - **API Keys**: Chỉ sử dụng khi cần tải model từ HuggingFace
        """)

# Footer
render_footer()
