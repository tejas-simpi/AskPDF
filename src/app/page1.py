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


def page1():
    st.title("🤖 Context-Free chatbot")
    st.write("Chat with your locally downloaded LLM without any context")

    # Initialize session state
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chatbot_model" not in st.session_state:
        st.session_state.chatbot_model = "llama3.2"

    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Chatbot Settings")
        
        # Get available models from Ollama
        try:
            models_info = ollama.list()
            available_models = extract_model_names(models_info)
        except Exception as e:
            st.error(f"Error fetching Ollama models: {e}")
            available_models = ("llama3.2",)  # Fallback to default
        
        if available_models:
            # Determine default index
            default_index = 0
            if st.session_state.chatbot_model in available_models:
                default_index = available_models.index(st.session_state.chatbot_model)
            
            selected_model = st.selectbox(
                "Select Model",
                available_models,
                index=default_index,
                help="Choose from locally available Ollama models"
            )
        else:
            st.warning("No Ollama models found. Please install at least one model.")
            st.info("Run: `ollama pull llama3.2`")
            return
        
        # Update model if changed
        if selected_model != st.session_state.chatbot_model:
            st.session_state.chatbot_model = selected_model
            st.session_state.chatbot = None  # Reset chatbot
            st.rerun()
        
        # System prompt customization
        st.subheader("System Prompt")
        system_prompt = st.text_area(
            "Customize the chatbot's behavior",
            value="You are a helpful AI assistant.",
            height=100,
            help="Define how the chatbot should behave"
        )
        
        # Clear chat button
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

    # Initialize chatbot if needed
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

    # Display chat history
    st.subheader("💬 Conversation")
    
    # Chat container
    chat_container = st.container(height=400, border=True)
    
    with chat_container:
        if len(st.session_state.chat_history) == 0:
            st.info("👋 Start a conversation by typing a message below!")
        else:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    with st.chat_message("user", avatar="👤"):
                        st.write(msg["content"])
                else:
                    with st.chat_message("assistant", avatar="🤖"):
                        st.write(msg["content"])

    # Chat input
    user_input = st.chat_input("Type your message here...", key="chat_input")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Get chatbot response
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.chatbot.chat(
                    message=user_input,
                    chat_history=st.session_state.chat_history[:-1]  # Exclude the current message
                )
                
                # Add assistant response to history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Error getting response: {e}")