"""
Post-processing / AI Enhancement Page
Grammar correction, keyword extraction, summarization
"""
import streamlit as st
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.components.layout import apply_custom_css
from core.nlp.post_processing import format_text, correct_punctuation, capitalize_sentences
from core.nlp.keyword_extraction import extract_keywords, simple_summarize

# Apply custom CSS
apply_custom_css()

# Page config
st.set_page_config(
    page_title="Post-Processing - Vietnamese Speech to Text",
    page_icon="✨",
    layout="wide"
)

# Initialize session state
for key, default in (
    ("transcript_text", ""),
    ("transcript_enhanced", ""),
):
    st.session_state.setdefault(key, default)

st.header("✨ Post-Processing & AI Enhancement")

# Check if transcript is available
if not st.session_state.transcript_text:
    st.warning("⚠️ Vui lòng chạy transcription trước tại trang 'Transcription'")
    if st.button("📝 Go to Transcription", type="primary"):
        st.switch_page("pages/2_📝_Transcription.py")
else:
    st.info("✅ Transcript đã sẵn sàng cho post-processing")
    
    # Display original transcript
    st.subheader("📝 Original Transcript")
    st.text_area(
        "Original:",
        st.session_state.transcript_text,
        height=200,
        key="original_transcript",
        disabled=True
    )
    
    # Post-processing options
    st.subheader("🔧 Post-Processing Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        auto_punctuation = st.checkbox("Tự động sửa dấu câu", value=True)
        capitalize_sent = st.checkbox("Viết hoa đầu câu", value=True)
        remove_spaces = st.checkbox("Loại bỏ khoảng trắng thừa", value=True)
    
    with col2:
        extract_keywords_enabled = st.checkbox("Extract keywords", value=False)
        summarize_enabled = st.checkbox("Tạo summary", value=False)
        num_keywords = st.number_input("Số keywords", min_value=5, max_value=50, value=10, 
                                       disabled=not extract_keywords_enabled)
        num_sentences = st.number_input("Số câu trong summary", min_value=1, max_value=10, value=3,
                                       disabled=not summarize_enabled)
    
    # Apply post-processing
    if st.button("✨ Apply Post-Processing", type="primary", use_container_width=True):
        with st.spinner("Đang xử lý..."):
            # Format text
            formatting_options = {
                "punctuation": auto_punctuation,
                "capitalize": capitalize_sent,
                "remove_extra_spaces": remove_spaces
            }
            
            enhanced_text = format_text(st.session_state.transcript_text, formatting_options)
            st.session_state.transcript_enhanced = enhanced_text
            
            st.success("✅ Đã xử lý thành công!")
            st.rerun()
    
    # Display enhanced transcript
    if st.session_state.transcript_enhanced:
        st.markdown("---")
        st.subheader("✨ Enhanced Transcript")
        
        enhanced_text = st.text_area(
            "Enhanced:",
            st.session_state.transcript_enhanced,
            height=300,
            key="enhanced_transcript"
        )
        
        if st.button("💾 Lưu Enhanced Transcript", type="primary"):
            st.session_state.transcript_text = enhanced_text
            st.session_state.transcript_enhanced = ""
            st.success("✅ Đã lưu enhanced transcript!")
            st.rerun()
        
        # Keywords
        if extract_keywords_enabled:
            st.markdown("---")
            st.subheader("🔑 Keywords")
            keywords = extract_keywords(enhanced_text, top_k=num_keywords)
            if keywords:
                st.write(", ".join([f"**{kw}**" for kw in keywords]))
            else:
                st.info("Không tìm thấy keywords")
        
        # Summary
        if summarize_enabled:
            st.markdown("---")
            st.subheader("📄 Summary")
            summary = simple_summarize(enhanced_text, max_sentences=num_sentences)
            if summary:
                st.info(summary)
            else:
                st.info("Không thể tạo summary")
    
    # Next step
    st.markdown("---")
    if st.button("📊 Go to Export & Reporting", type="primary", use_container_width=True):
        st.switch_page("pages/5_📊_Export_Reporting.py")

