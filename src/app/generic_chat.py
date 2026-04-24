import streamlit as st
import sys
import os
import ollama
from pathlib import Path
from typing import Any, Tuple

# Add parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.chatbot import GenericChatbot


def extract_model_names(models_info: Any) -> Tuple[str, ...]:
    """
    Extract model names from the provided models information.
    
    Args:
        models_info: Response from ollama.list()
    
    Returns:
        Tuple[str, ...]: A tuple of model names.
    """
    try:
        # The new response format returns a list of Model objects
        if hasattr(models_info, "models"):
            # Extract model names from the Model objects
            model_names = tuple(model.model for model in models_info.models)
        else:
            # Fallback for any other format
            model_names = tuple()
        return model_names
    except Exception as e:
        st.error(f"Error extracting model names: {e}")
        return tuple()


def generic_chat():
    # Initialize session state
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chatbot_model" not in st.session_state:
        st.session_state.chatbot_model = "llama3.2"

    # ── Sidebar ──────────────────────────────────────────────
    with st.sidebar:
        # Brand
        st.markdown("""
            <div class="sidebar-brand">
                <span class="sidebar-brand-icon">📄</span>
                <span class="sidebar-brand-text">AskPDF</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Model selection section
        st.markdown('<div class="sidebar-section-label">Model</div>', unsafe_allow_html=True)
        
        try:
            models_info = ollama.list()
            available_models = extract_model_names(models_info)
        except Exception as e:
            st.error(f"Error fetching Ollama models: {e}")
            available_models = ("llama3.2",)  # Fallback to default
        
        if available_models:
            default_index = 0
            if st.session_state.chatbot_model in available_models:
                default_index = available_models.index(st.session_state.chatbot_model)
            
            selected_model = st.selectbox(
                "Select Model",
                available_models,
                index=default_index,
                help="Choose from locally available Ollama models",
                label_visibility="collapsed"
            )
        else:
            st.warning("No Ollama models found. Please install at least one model.")
            st.info("Run: `ollama pull llama3.2`")
            return
        
        # Update model if changed
        if selected_model != st.session_state.chatbot_model:
            st.session_state.chatbot_model = selected_model
            st.session_state.chatbot = None
            st.rerun()
        
        st.markdown('<div style="margin-top: 0.75rem"></div>', unsafe_allow_html=True)
        
        # System prompt section
        st.markdown('<div class="sidebar-section-label">System Prompt</div>', unsafe_allow_html=True)
        system_prompt = st.text_area(
            "Customize the chatbot's behavior",
            value="You are a helpful AI assistant.",
            height=100,
            help="Define how the chatbot should behave",
            label_visibility="collapsed"
        )
        
        st.markdown('<div style="margin-top: 0.75rem"></div>', unsafe_allow_html=True)
        
        # Actions section
        st.markdown('<div class="sidebar-section-label">Actions</div>', unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
        
        st.divider()
        
        # Info section
        with st.expander("ℹ️ About"):
            st.info(
                f"**Current Model:** {selected_model}\n\n"
                f"**Messages:** {len(st.session_state.chat_history)}\n\n"
                "This chatbot uses locally downloaded Ollama models "
                "without any document context (RAG)."
            )

    # ── Initialize Chatbot ───────────────────────────────────
    if st.session_state.chatbot is None:
        with st.spinner(f"Loading {selected_model}..."):
            try:
                st.session_state.chatbot = GenericChatbot(
                    model_name=selected_model,
                    system_prompt=system_prompt
                )
                st.success(f"✅ {selected_model} loaded successfully!")
            except Exception as e:
                st.error(f"❌ Error loading model: {e}")
                st.info("Make sure Ollama is running and the model is downloaded:\n"
                       f"`ollama pull {selected_model}`")
                return
    else:
        # Update system prompt if changed
        st.session_state.chatbot.update_system_prompt(system_prompt)

    # ── Chat Interface ───────────────────────────────────────
    chat_container = st.container(height=500, border=True)
    
    with chat_container:
        if len(st.session_state.chat_history) == 0:
            st.markdown("""
                <div class="empty-state">
                    <div class="empty-state-icon">💬</div>
                    <div class="empty-state-title">Start a Conversation</div>
                    <div class="empty-state-desc">Type a message below to begin chatting with your AI assistant</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    with st.chat_message("user", avatar="👤"):
                        st.write(msg["content"])
                else:
                    with st.chat_message("assistant", avatar="🤖"):
                        st.write(msg["content"])

    # Chat input
    if user_input := st.chat_input("Type your message here...", key="chat_input"):
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Get chatbot response
        try:
            response = st.session_state.chatbot.chat(
                message=user_input,
                chat_history=st.session_state.chat_history[:-1]
            )
            
            # Add assistant response to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })
            
        except Exception as e:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"⚠️ Error: {e}"
            })
        
        st.rerun()