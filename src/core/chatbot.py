"""Generic chatbot functionality without RAG context."""
import logging
from langchain_ollama.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

logger = logging.getLogger(__name__)


class GenericChatbot:
    """A generic chatbot using Ollama models without RAG context."""
    
    def __init__(self, model_name: str = "llama3.2", system_prompt: str = None):
        """
        Initialize the chatbot.
        
        Args:
            model_name: Name of the Ollama model to use
            system_prompt: Optional system prompt to set chatbot behavior
        """
        self.model_name = model_name
        self.llm = ChatOllama(model=model_name)
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        logger.info(f"Initialized GenericChatbot with model: {model_name}")
    
    def chat(self, message: str, chat_history: list = None) -> str:
        """
        Send a message and get a response.
        
        Args:
            message: User message
            chat_history: List of previous messages in format [{"role": "user/assistant", "content": "..."}]
            
        Returns:
            AI response as string
        """
        try:
            # Build message history
            messages = [SystemMessage(content=self.system_prompt)]
            
            # Add chat history if provided
            if chat_history:
                for msg in chat_history:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
            
            # Add current message
            messages.append(HumanMessage(content=message))
            
            # Get response
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Error during chat: {e}")
            return f"Error: {str(e)}"
    
    def update_model(self, model_name: str):
        """Update the LLM model."""
        self.model_name = model_name
        self.llm = ChatOllama(model=model_name)
        logger.info(f"Updated model to: {model_name}")
    
    def update_system_prompt(self, system_prompt: str):
        """Update the system prompt."""
        self.system_prompt = system_prompt
        logger.info("Updated system prompt")
