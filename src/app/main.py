import streamlit as st
from pathlib import Path
from page1 import page1
from page2 import page2

# Page configuration
st.set_page_config(
    page_title="Study Sensei",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
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
            <h1 class="landing-title">Study Sensei</h1>
            <p class="landing-subtitle">
                Your intelligent study companion. <br>
                Private, local, and powerful.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Create centered columns for buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        # Create two columns for side-by-side buttons with better spacing
        btn_col1, btn_col2 = st.columns(2, gap="medium")
        
        with btn_col1:
            if st.button("Generic Chat", use_container_width=True, key="nav_generic"):
                st.session_state.current_page = "generic"
                st.rerun()
        
        with btn_col2:
            if st.button("PDF Chat", use_container_width=True, key="nav_rag"):
                st.session_state.current_page = "rag"
                st.rerun()

def main():
    # Back to home button (shown on chatbot pages)
    if st.session_state.current_page != "landing":
        if st.button("← Back to Home", key="back_home"):
            st.session_state.current_page = "landing"
            st.rerun()
    
    # Route to appropriate page
    if st.session_state.current_page == "landing":
        show_landing()
    elif st.session_state.current_page == "generic":
        st.title("")
        st.caption("")
        page1()
    elif st.session_state.current_page == "rag":
        st.title("📄 PDF Chat")
        st.caption("Upload PDFs and chat with your documents")
        page2()

if __name__ == "__main__":
    main()