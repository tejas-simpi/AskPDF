"""FastAPI backend for AskPDF — wraps existing core logic as REST APIs."""
import os
import sys
import base64
import tempfile
import shutil
import logging
import warnings
from pathlib import Path
from typing import Any, List, Optional
from io import BytesIO

# Add src to path so we can import core modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import ollama
import pdfplumber

# Suppress torch warning
warnings.filterwarnings('ignore', category=UserWarning, message='.*torch.classes.*')

from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain_classic.retrievers.multi_query import MultiQueryRetriever

from core.chatbot import GenericChatbot

# Set protobuf environment variable
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────
PERSIST_DIRECTORY = os.path.join("data", "vectors")

# ── FastAPI App ──────────────────────────────────────────────────────────
app = FastAPI(title="AskPDF API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory State (single-user local app) ─────────────────────────────
state = {
    "chatbot": None,
    "chatbot_model": None,
    "chat_history": [],
    "vector_db": None,
    "processed_files": set(),
    "pdf_pages_b64": [],
    "file_names": [],
}


# ── Pydantic Models ─────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    model: str = "llama3.2"
    system_prompt: str = "You are a helpful AI assistant."


class PDFAskRequest(BaseModel):
    question: str
    model: str = "llama3.2"


class ChatMessage(BaseModel):
    role: str
    content: str


# ── Helper Functions ─────────────────────────────────────────────────────
def extract_model_names(models_info: Any):
    """Extract model names from ollama.list() response."""
    try:
        if hasattr(models_info, "models"):
            return [model.model for model in models_info.models]
        return []
    except Exception as e:
        logger.error(f"Error extracting model names: {e}")
        return []


def format_docs(docs):
    """Format retrieved documents into clean text with deduplication."""
    seen = set()
    parts = []
    for doc in docs:
        if doc.page_content not in seen:
            seen.add(doc.page_content)
            parts.append(doc.page_content)
    logger.info(f"Formatted {len(parts)} unique chunks from {len(docs)} retrieved documents")
    return "\n\n---\n\n".join(parts)


def process_question(question: str, vector_db: Chroma, selected_model: str) -> str:
    """Process a user question using the RAG pipeline.

    Uses explicit step-by-step execution (not a single chain) so we can
    verify retrieval results and short-circuit when context is empty.
    """
    logger.info(f"Processing question: {question} using model: {selected_model}")

    llm = ChatOllama(model=selected_model, temperature=0, num_predict=8192)

    # ── Step 1: Multi-query retrieval with relevance filtering ────────────
    # ChromaDB always returns k results even if none are relevant.
    # We use relevance scores to filter out irrelevant chunks.

    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""You are a search query optimization assistant. Your task is to generate 2 alternative versions of the given user question to improve document retrieval from a vector database.

For each alternative:
- Rephrase using synonyms, broader terms, or more specific terminology
- Consider both conceptual phrasings (why/how) and factual phrasings (what/when/where)
- Approach the question from a different angle or perspective
- Keep each alternative focused and directly relevant to the original intent — do not make them generic

Provide ONLY the 2 alternative questions, each on its own line. Do not number them or add any other text.

Original question: {question}""",
    )

    retriever = MultiQueryRetriever.from_llm(
        vector_db.as_retriever(search_kwargs={"k": 8}),
        llm,
        prompt=QUERY_PROMPT,
    )

    # Retrieve documents explicitly
    retrieved_docs = retriever.invoke(question)

    # ── Relevance filtering ──────────────────────────────────────────────
    # Re-score each retrieved chunk against the original question.
    # ChromaDB returns cosine distance; relevance = 1 - distance.
    # Only keep chunks with relevance >= threshold.
    RELEVANCE_THRESHOLD = 0.35
    scored_results = vector_db.similarity_search_with_relevance_scores(
        question, k=min(len(retrieved_docs), 20)
    )

    # Build a set of page contents that pass the threshold
    relevant_contents = set()
    for doc, score in scored_results:
        if score >= RELEVANCE_THRESHOLD:
            relevant_contents.add(doc.page_content)
            logger.info(f"  Chunk (score={score:.3f}): {doc.page_content[:80]}...")
        else:
            logger.info(f"  REJECTED (score={score:.3f}): {doc.page_content[:80]}...")

    # Filter the multi-query results to only include relevant chunks
    filtered_docs = [
        doc for doc in retrieved_docs
        if doc.page_content in relevant_contents
    ]

    logger.info(
        f"Relevance filter: {len(retrieved_docs)} retrieved -> "
        f"{len(filtered_docs)} passed (threshold={RELEVANCE_THRESHOLD})"
    )

    context = format_docs(filtered_docs)
    logger.info(f"Context length: {len(context)} chars")

    # ── Step 2: Short-circuit if no relevant context ─────────────────────
    if not context or len(context.strip()) < 20:
        logger.warning("No relevant context found — returning refusal")
        return "I couldn't find that in the document."

    # ── Step 3: Generate answer strictly from context ────────────────────
    template = """You are answering questions strictly from the context provided below. You must ONLY use information found in the context. Do NOT use your own knowledge, training data, or any outside information under any circumstances.

If the question CANNOT be answered using the context below, you MUST respond ONLY with: "I couldn't find that in the document." Do not attempt to answer, guess, or provide general knowledge.

Rules:
- NEVER answer from your own knowledge. If the context does not contain the answer, refuse.
- Never mention the context, document, source, or provided text. Just state the information directly.
- Never add closing statements like "I have covered all points" or similar.
- NEVER ask follow-up questions like "Do you want me to elaborate?" or "Would you like to know more?" — just stop after answering.
- Do NOT add analogies, metaphors, or examples unless they are explicitly present in the context.

Response style:
- COMPLETENESS IS THE TOP PRIORITY. Cover ALL categories, types, and points present in the context before adding detail to any single one.
- Distribute detail evenly across all points — do not over-expand early points at the expense of later ones.
- Include definitions, sub-types, and examples for each point but keep them concise.
- Use numbered lists for main categories and bullet points for sub-details.
- Use proper line breaks and clean formatting.
- When explaining structures, layers, flows, or hierarchies, use ASCII box-drawing diagrams.

Context:
{context}

Question: {question}
"""

    prompt = ChatPromptTemplate.from_template(template)

    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({"context": context, "question": question})
    logger.info("Question processed and response generated")
    return response


def pdf_to_base64_pages(file_bytes: bytes, filename: str) -> list[str]:
    """Convert PDF file bytes to a list of base64-encoded page images."""
    pages_b64 = []
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            img = page.to_image(resolution=150).original
            buf = BytesIO()
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            pages_b64.append(f"data:image/png;base64,{b64}")
    return pages_b64


# ── API Endpoints ────────────────────────────────────────────────────────
# NOTE: All endpoints use `def` (not `async def`) because LangChain,
# Ollama, and ChromaDB operations are synchronous/blocking.
# FastAPI automatically runs `def` endpoints in a threadpool,
# which is correct for blocking I/O. Using `async def` with blocking
# calls would freeze the event loop and can cause silent failures.

@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "2.0.0"}


@app.get("/api/models")
def list_models():
    """List available Ollama models."""
    try:
        models_info = ollama.list()
        models = extract_model_names(models_info)
        return {"models": models}
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=503, detail=f"Could not connect to Ollama: {e}")


@app.post("/api/chat")
def generic_chat(request: ChatRequest):
    """Send a message to the generic chatbot (no RAG)."""
    try:
        # Initialize or update chatbot if model changed
        if state["chatbot"] is None or state["chatbot_model"] != request.model:
            state["chatbot"] = GenericChatbot(
                model_name=request.model,
                system_prompt=request.system_prompt,
            )
            state["chatbot_model"] = request.model
            state["chat_history"] = []
        else:
            state["chatbot"].update_system_prompt(request.system_prompt)

        # Get response
        response = state["chatbot"].chat(
            message=request.message,
            chat_history=state["chat_history"],
        )

        # Update history
        state["chat_history"].append({"role": "user", "content": request.message})
        state["chat_history"].append({"role": "assistant", "content": response})

        return {"response": response, "history": state["chat_history"]}

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/clear")
def clear_chat():
    """Clear generic chat history."""
    state["chat_history"] = []
    state["chatbot"] = None
    return {"status": "cleared"}


@app.post("/api/pdf/upload")
def upload_pdfs(files: List[UploadFile] = File(...)):
    """Upload PDF files, create vector DB, return page images."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    temp_dir = tempfile.mkdtemp()
    all_data = []
    all_pages_b64 = []
    file_names = []

    try:
        for file in files:
            if not file.filename.lower().endswith(".pdf"):
                continue

            file_bytes = file.file.read()
            file_names.append(file.filename)

            # Save to temp for PyPDFLoader
            path = os.path.join(temp_dir, file.filename)
            with open(path, "wb") as f:
                f.write(file_bytes)

            # Load document
            loader = PyPDFLoader(path)
            data = loader.load()
            all_data.extend(data)
            logger.info(f"Loaded {len(data)} pages from {file.filename}")

            # Extract page images as base64
            pages = pdf_to_base64_pages(file_bytes, file.filename)
            all_pages_b64.extend(pages)

        if not all_data:
            raise HTTPException(status_code=400, detail="No valid PDF files found")

        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=6000, chunk_overlap=500
        )
        chunks = text_splitter.split_documents(all_data)
        logger.info(f"Split {len(all_data)} pages into {len(chunks)} chunks")

        # Create embeddings and vector DB
        embeddings = OllamaEmbeddings(model="nomic-embed-text")

        # Create unique collection name based on all files
        file_names_key = "_".join(file_names)
        collection_name = f"pdf_collection_{hash(file_names_key)}"

        # Delete existing vector DB if any
        if state["vector_db"] is not None:
            try:
                state["vector_db"].delete_collection()
            except Exception:
                pass

        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=PERSIST_DIRECTORY,
            collection_name=collection_name,
        )
        logger.info("Vector DB created with persistent storage")

        # Update state
        state["vector_db"] = vector_db
        state["processed_files"] = set(file_names)
        state["pdf_pages_b64"] = all_pages_b64
        state["file_names"] = file_names

        return {
            "status": "success",
            "files": file_names,
            "total_pages": len(all_pages_b64),
            "total_chunks": len(chunks),
            "pages": all_pages_b64,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.get("/api/pdf/pages")
def get_pdf_pages():
    """Get previously uploaded PDF page images."""
    return {
        "pages": state["pdf_pages_b64"],
        "files": state["file_names"],
        "total_pages": len(state["pdf_pages_b64"]),
    }


@app.post("/api/pdf/ask")
def ask_pdf(request: PDFAskRequest):
    """Ask a question about uploaded PDFs using RAG."""
    if state["vector_db"] is None:
        raise HTTPException(status_code=400, detail="No PDF uploaded. Please upload a PDF first.")

    try:
        response = process_question(
            request.question, state["vector_db"], request.model
        )
        return {"response": response}
    except Exception as e:
        logger.error(f"PDF ask error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/pdf/delete")
def delete_collection():
    """Delete vector DB collection and clear PDF state."""
    if state["vector_db"] is not None:
        try:
            state["vector_db"].delete_collection()
        except Exception as e:
            logger.warning(f"Error deleting collection: {e}")

    state["vector_db"] = None
    state["processed_files"] = set()
    state["pdf_pages_b64"] = []
    state["file_names"] = []

    return {"status": "deleted"}


# ── Main ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    print("[AskPDF] Starting API server on http://127.0.0.1:8000")
    print("[AskPDF] API docs at http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)

