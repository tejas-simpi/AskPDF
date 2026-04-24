import streamlit as st
from pathlib import Path
from generic_chat import generic_chat
from pdf_chat import pdf_chat

# Page configuration
st.set_page_config(
    page_title="AskPDF",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom CSS
def load_css():
    css_path = Path(__file__).parent / "styles.css"
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize session state
if "current_page" not in st.session_state:
    st.session_state.current_page = "landing"

def show_landing():
    """Display the landing page"""
    st.markdown("""
        <div class="landing-container">
            <div class="landing-accent"></div>
            <h1 class="landing-title">AskPDF</h1>
            <p class="landing-subtitle">
                Your intelligent document companion.<br>
                Private, local, and powerful.
            </p>
            <div class="landing-badge">
                🔒 Powered by Ollama &bull; 100% Local
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Feature cards as navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        btn_col1, btn_col2 = st.columns(2, gap="medium")
        
        with btn_col1:
            st.markdown("""
                <div class="feature-card-visual">
                    <span class="feature-card-icon">💬</span>
                    <div class="feature-card-title">Context-Free Chat</div>
                    <div class="feature-card-desc">Chat with your locally available LLM without any document context</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Open Chat →", use_container_width=True, key="nav_generic"):
                st.session_state.current_page = "generic"
                st.rerun()
        
        with btn_col2:
            st.markdown("""
                <div class="feature-card-visual">
                    <span class="feature-card-icon">📄</span>
                    <div class="feature-card-title">PDF-Powered Chat</div>
                    <div class="feature-card-desc">Upload PDFs and ask questions with RAG-powered answers</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Open PDF Chat →", use_container_width=True, key="nav_rag"):
                st.session_state.current_page = "rag"
                st.rerun()

def main():
    # Back to home button (shown on chatbot pages)
    if st.session_state.current_page != "landing":
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("← Home", key="back_home"):
            st.session_state.current_page = "landing"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Route to appropriate page
    if st.session_state.current_page == "landing":
        show_landing()
    elif st.session_state.current_page == "generic":
        st.markdown("""
            <div class="page-header">
                <h2>💬 Context-Free Chat</h2>
                <p>Chat with your locally downloaded LLM without any document context</p>
                <div class="page-header-accent"></div>
            </div>
        """, unsafe_allow_html=True)
        generic_chat()
    elif st.session_state.current_page == "rag":
        st.markdown("""
            <div class="page-header">
                <h2>📄 PDF Chat</h2>
                <p>Upload PDFs and chat with your documents using RAG</p>
                <div class="page-header-accent"></div>
            </div>
        """, unsafe_allow_html=True)
        pdf_chat()

if __name__ == "__main__":
    main()
