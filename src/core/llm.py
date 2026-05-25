"""LLM configuration and setup."""
import logging
from langchain_ollama.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate

logger = logging.getLogger(__name__)

class LLMManager:
    """Manages LLM configuration and prompts."""
    
    def __init__(self, model_name: str = "llama2"):
        self.model_name = model_name
        self.llm = ChatOllama(model=model_name, temperature=0, num_predict=8192)
        
    def get_query_prompt(self) -> PromptTemplate:
        """Get query generation prompt."""
        return PromptTemplate(
            input_variables=["question"],
            template="""You are a search query optimization assistant. Your task is to generate 2 alternative versions of the given user question to improve document retrieval from a vector database.

For each alternative:
- Rephrase using synonyms, broader terms, or more specific terminology
- Consider both conceptual phrasings (why/how) and factual phrasings (what/when/where)
- Approach the question from a different angle or perspective
- Keep each alternative focused and directly relevant to the original intent — do not make them generic

Provide ONLY the 2 alternative questions, each on its own line. Do not number them or add any other text.

Original question: {question}"""
        )
    
    def get_rag_prompt(self) -> ChatPromptTemplate:
        """Get RAG prompt template."""
        template = """You are answering questions strictly from the context provided below. You must ONLY use information found in the context. Do NOT use your own knowledge, training data, or any outside information under any circumstances.

If the question CANNOT be answered using the context below, you MUST respond ONLY with: "I couldn't find that in the document." Do not attempt to answer, guess, or provide general knowledge.

Rules:
- NEVER answer from your own knowledge. If the context does not contain the answer, refuse.
- Never mention the context, document, source, or provided text. Just state the information directly.
- Never add closing statements like "I have covered all points" or similar.

Response style:
- COMPLETENESS IS THE TOP PRIORITY. Cover ALL categories, types, and points present in the context before adding detail to any single one.
- Distribute detail evenly across all points — do not over-expand early points at the expense of later ones.
- Include definitions, sub-types, and examples for each point but keep them concise.
- Use numbered lists for main categories and bullet points for sub-details.
- Use proper line breaks and clean formatting.
- When explaining structures, layers, flows, or hierarchies, use ASCII box-drawing diagrams (─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼ ║ ═ ╔ ╗ ╚ ╝).

Context:
{context}

Question: {question}
"""
        return ChatPromptTemplate.from_template(template) 