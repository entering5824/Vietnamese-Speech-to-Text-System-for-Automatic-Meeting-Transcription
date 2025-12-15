"""
Shared Sidebar Component
Hiển thị logo và navigation cho tất cả pages
"""
import streamlit as st
import os

def render_sidebar(logo_width=110):
    """
    Render sidebar với logo và title
    
    Args:
        logo_width: Chiều rộng logo (default: 110)
    """
    # Get project root (2 levels up from app/components/)
    base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    img_path = os.path.join(base, "assets", "logo.webp")
    
    # Display logo
    if os.path.exists(img_path):
        st.sidebar.image(img_path, width=logo_width)
    else:
        # Fallback nếu không có logo
        st.sidebar.markdown("### 🎤")
    
    st.sidebar.title("🎤 Vietnamese Speech to Text")
    st.sidebar.markdown("---")
    
    # Navigation hint (manual radio in main.py)
    st.sidebar.markdown("""
    <div style="font-size: 0.9em; color: #666; padding: 10px 0;">
    Dùng menu radio trong sidebar để điều hướng các trang.
    </div>
    """, unsafe_allow_html=True)
