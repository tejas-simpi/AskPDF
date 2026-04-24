"""Sidebar component for the Streamlit app."""
import streamlit as st
import ollama

def render_sidebar_brand():
    """Render the sidebar brand header."""
    st.markdown("""
        <div class="sidebar-brand">
            <span class="sidebar-brand-icon">📚</span>
            <span class="sidebar-brand-text">AskPDF</span>
        </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar with model selection and controls."""
    with st.sidebar:
        render_sidebar_brand()
        
        st.markdown('<div class="sidebar-section-label">Model</div>', unsafe_allow_html=True)
        
        # Get available models
        try:
            models_info = ollama.list()
            if hasattr(models_info, "models"):
                available_models = tuple(model.model for model in models_info.models)
            else:
                available_models = tuple()
            
            # Model selection
            selected_model = st.selectbox(
                "Select Model",
                available_models,
                index=0 if available_models else None,
                help="Choose a local Ollama model",
                label_visibility="collapsed"
            )
            
            return selected_model
            
        except Exception as e:
            st.error(f"Error loading models: {e}")
            return None