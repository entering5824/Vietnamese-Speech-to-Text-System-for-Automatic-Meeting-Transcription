"""
Sidebar Component với Logo và Role-based Navigation
Hiển thị logo và navigation dựa trên user role
"""
import streamlit as st
import os
from pathlib import Path

# Import auth system
import sys
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
from core.auth.roles import get_user_role, UserRole
from core.auth.session import get_current_user

def render_sidebar():
    """Render sidebar với logo và role-based navigation"""
    # Get logo path
    logo_path = BASE_DIR / "assets" / "logo.webp"
    
    # Get user info
    user = get_current_user()
    user_role = get_user_role()
    
    with st.sidebar:
        # Logo
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        else:
            st.markdown("### 🎤 Vietnamese STT")
        
        st.markdown("---")
        
        # User info
        st.markdown(f"""
        <div style='text-align: center; padding: 10px;'>
            <h3 style='margin: 0; color: #1f4e79;'>Vietnamese Speech to Text</h3>
            <p style='margin: 5px 0; font-size: 0.9em; color: #666;'>Automatic Meeting Transcription</p>
            <p style='margin: 5px 0; font-size: 0.8em; color: #888;'>{user['user_name']}</p>
            <p style='margin: 0; font-size: 0.75em; color: #aaa;'>{user_role.value.upper()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Role-based navigation
        if user_role == UserRole.USER:
            render_user_navigation()
        elif user_role == UserRole.AI_SPECIALIST:
            render_ai_specialist_navigation()
        elif user_role in [UserRole.ADMIN, UserRole.MANAGER]:
            render_admin_navigation()
        
        st.markdown("---")
        
        # Role switcher (for demo - remove in production)
        if os.getenv("DEVELOPMENT_MODE", "false").lower() == "true":
            st.markdown("### 🔧 Dev Tools")
            new_role = st.selectbox(
                "Switch Role (Dev Only)",
                [r.value for r in UserRole],
                index=list(UserRole).index(user_role),
                key="role_switcher"
            )
            if new_role != user_role.value:
                st.session_state.user_role = new_role
                st.rerun()

def render_user_navigation():
    """Navigation menu for regular users"""
    st.markdown("### 📋 User Menu")
    
    st.markdown("""
    - 🏠 [Home / Dashboard](?page=Home)
    - 📤 [Upload & Record](?page=1_📤_Upload_Record)
    - 🎧 [Preprocessing](?page=2_🎧_Preprocessing)
    - 📝 [Transcription](?page=3_📝_Transcription)
    - 👥 [Speaker Diarization](?page=4_👥_Speaker_Diarization)
    - 📊 [Export & Statistics](?page=5_📊_Export_Statistics)
    - 📚 [History / Projects](?page=History)
    - ❓ [Help & Tutorials](?page=Help)
    """)

def render_ai_specialist_navigation():
    """Navigation menu for AI specialists"""
    st.markdown("### 🔬 AI Specialist Menu")
    
    st.markdown("""
    **User Features:**
    - 🏠 [Home / Dashboard](?page=Home)
    - 📤 [Upload & Record](?page=1_📤_Upload_Record)
    - 📝 [Transcription](?page=3_📝_Transcription)
    - 📊 [Export & Statistics](?page=5_📊_Export_Statistics)
    
    **AI Tools:**
    - 🤖 [Model Management](?page=AI_Models)
    - ⚙️ [Model Settings](?page=AI_Model_Settings)
    - 📈 [Evaluation & Metrics](?page=AI_Evaluation)
    - 🔬 [ASR Benchmark](?page=6_🔬_ASR_Benchmark)
    - 📊 [Inference Logs](?page=AI_Logs)
    - 📚 [Datasets](?page=AI_Datasets)
    """)

def render_admin_navigation():
    """Navigation menu for admins"""
    st.markdown("### 👑 Admin Menu")
    
    st.markdown("""
    **User Features:**
    - 🏠 [Home / Dashboard](?page=Home)
    - 📤 [Upload & Record](?page=1_📤_Upload_Record)
    - 📝 [Transcription](?page=3_📝_Transcription)
    
    **AI Tools:**
    - 🤖 [Model Management](?page=AI_Models)
    - 📈 [Evaluation & Metrics](?page=AI_Evaluation)
    
    **Admin Tools:**
    - 📊 [Admin Dashboard](?page=Admin_Dashboard)
    - 👥 [User Management](?page=Admin_Users)
    - 💰 [Billing & Costs](?page=Admin_Billing)
    - 📋 [Audit Logs](?page=Admin_Logs)
    - ⚙️ [System Settings](?page=Admin_Settings)
    - 🏥 [System Health](?page=Admin_Health)
    """)
