"""
Streamlit application for PDF-based Retrieval-Augmented Generation (RAG) using Ollama + LangChain.

This application allows users to upload a PDF, process it,
and then ask questions about the content using a selected language model.
"""
import streamlit as st
import logging
import os
import tempfile
import shutil
import pdfplumber
import ollama
import warnings
from langchain_community.document_loaders import PyPDFLoader

# Suppress torch warning
warnings.filterwarnings('ignore', category=UserWarning, message='.*torch.classes.*')

from langchain_ollama import OllamaEmbeddings   
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain_classic.retrievers.multi_query import MultiQueryRetriever
from typing import List, Tuple, Dict, Any, Optional

# Set protobuf environment variable to avoid error messages
# This might cause some issues with latency but it's a tradeoff
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# Define persistent directory for ChromaDB
PERSIST_DIRECTORY = os.path.join("data", "vectors")

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def extract_model_names(models_info: Any) -> Tuple[str, ...]:
    """
    Extract model names from the provided models information.

    Args:
        models_info: Response from ollama.list()

    Returns:
        Tuple[str, ...]: A tuple of model names.
    """
    logger.info("Extracting model names from models_info")
    try:
        # The new response format returns a list of Model objects
        if hasattr(models_info, "models"):
            # Extract model names from the Model objects
            model_names = tuple(model.model for model in models_info.models)
        else:
            # Fallback for any other format
            model_names = tuple()
            
        logger.info(f"Extracted model names: {model_names}")
        return model_names
    except Exception as e:
        logger.error(f"Error extracting model names: {e}")
        return tuple()


def create_vector_db(file_uploads) -> Chroma:
    """
    Create a vector database from uploaded PDF files.
    Args:
        file_uploads: Single file or list of Streamlit file upload objects containing PDFs.
    Returns:
        Chroma: A vector store containing the processed document chunks from all files.
    """
    # Handle both single file and multiple files
    if not isinstance(file_uploads, list):
        file_uploads = [file_uploads]
    
    logger.info(f"Creating vector DB from {len(file_uploads)} file(s)")
    temp_dir = tempfile.mkdtemp()
    all_data = []
    
    try:
        # Process each uploaded file
        for file_upload in file_uploads:
            logger.info(f"Processing file: {file_upload.name}")
            path = os.path.join(temp_dir, file_upload.name)
            with open(path, "wb") as f:
                f.write(file_upload.getvalue())
                logger.info(f"File saved to temporary path: {path}")
            
            loader = PyPDFLoader(path)
            data = loader.load()
            all_data.extend(data)
            logger.info(f"Loaded {len(data)} pages from {file_upload.name}")
        
        # Split all documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=6000, chunk_overlap=500)
        chunks = text_splitter.split_documents(all_data)
        logger.info(f"Total {len(all_data)} pages split into {len(chunks)} chunks")
        
        # Create embeddings and vector DB
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        
        # Create unique collection name based on all files
        file_names = "_".join([f.name for f in file_uploads])
        collection_name = f"pdf_collection_{hash(file_names)}"
        
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=PERSIST_DIRECTORY,
            collection_name=collection_name
        )
        logger.info("Vector DB created with persistent storage")
        
    finally:
        # Always clean up temp directory
        shutil.rmtree(temp_dir)
        logger.info(f"Temporary directory {temp_dir} removed")
    
    return vector_db


def add_files_to_vector_db(file_uploads, vector_db: Chroma) -> None:
    """
    Add new files to an existing vector database.
    Args:
        file_uploads: Single file or list of Streamlit file upload objects containing PDFs.
        vector_db: Existing Chroma vector database to add documents to.
    """
    # Handle both single file and multiple files
    if not isinstance(file_uploads, list):
        file_uploads = [file_uploads]
    
    logger.info(f"Adding {len(file_uploads)} new file(s) to existing vector DB")
    temp_dir = tempfile.mkdtemp()
    all_data = []
    
    try:
        # Process each uploaded file
        for file_upload in file_uploads:
            logger.info(f"Processing new file: {file_upload.name}")
            path = os.path.join(temp_dir, file_upload.name)
            with open(path, "wb") as f:
                f.write(file_upload.getvalue())
                logger.info(f"File saved to temporary path: {path}")
            
            loader = PyPDFLoader(path)
            data = loader.load()
            all_data.extend(data)
            logger.info(f"Loaded {len(data)} pages from {file_upload.name}")
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=6000, chunk_overlap=500)
        chunks = text_splitter.split_documents(all_data)
        logger.info(f"Total {len(all_data)} pages split into {len(chunks)} chunks")
        
        # Add chunks to existing vector database
        vector_db.add_documents(chunks)
        logger.info(f"Added {len(chunks)} chunks to existing vector DB")
        
    finally:
        # Always clean up temp directory
        shutil.rmtree(temp_dir)
        logger.info(f"Temporary directory {temp_dir} removed")


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
    """
    Process a user question using the vector database and selected language model.

    Args:
        question (str): The user's question.
        vector_db (Chroma): The vector database containing document embeddings.
        selected_model (str): The name of the selected language model.

    Returns:
        str: The generated response to the user's question.
    """
    logger.info(f"Processing question: {question} using model: {selected_model}")
    
    # Initialize LLM with temperature=0 for deterministic, grounded responses
    llm = ChatOllama(model=selected_model, temperature=0, num_predict=8192)
    
    # Query prompt template
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

    # Set up retriever
    retriever = MultiQueryRetriever.from_llm(
        vector_db.as_retriever(search_kwargs={"k": 8}), 
        llm,
        prompt=QUERY_PROMPT
    )

    # RAG prompt template
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

    prompt = ChatPromptTemplate.from_template(template)

    # Create chain
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    response = chain.invoke(question)
    logger.info("Question processed and response generated")
    return response


@st.cache_data
def extract_all_pages_as_images(file_upload) -> List[Any]:
    """
    Extract all pages from a PDF file as images.

    Args:
        file_upload (st.UploadedFile): Streamlit file upload object containing the PDF.

    Returns:
        List[Any]: A list of image objects representing each page of the PDF.
    """
    logger.info(f"Extracting all pages as images from file: {file_upload.name}")
    pdf_pages = []
    with pdfplumber.open(file_upload) as pdf:
        pdf_pages = [page.to_image().original for page in pdf.pages]
    logger.info("PDF pages extracted as images")
    return pdf_pages


def delete_vector_db(vector_db: Optional[Chroma]) -> None:
    """
    Delete the vector database and clear related session state.

    Args:
        vector_db (Optional[Chroma]): The vector database to be deleted.
    """
    logger.info("Deleting vector DB")
    if vector_db is not None:
        try:
            # Delete the collection
            vector_db.delete_collection()
            
            # Clear session state
            st.session_state.pop("pdf_pages", None)
            st.session_state.pop("file_uploads", None)
            st.session_state.pop("vector_db", None)
            
            st.success("Collection and temporary files deleted successfully.")
            logger.info("Vector DB and related session state cleared")
            st.rerun()
        except Exception as e:
            st.error(f"Error deleting collection: {str(e)}")
            logger.error(f"Error deleting collection: {e}")
    else:
        st.error("No vector database found to delete.")
        logger.warning("Attempted to delete vector DB, but none was found")


def pdf_chat() -> None:
    """
    Main function to run the Streamlit application.
    """
    # Get available models
    models_info = ollama.list()
    available_models = extract_model_names(models_info)

    # ── Sidebar (Model Selection) ────────────────────────────
    with st.sidebar:
        st.markdown("""
            <div class="sidebar-brand">
                <span class="sidebar-brand-icon">📄</span>
                <span class="sidebar-brand-text">AskPDF</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-section-label">Model</div>', unsafe_allow_html=True)
        
        selected_model = None
        if available_models:
            selected_model = st.selectbox(
                "Pick a model",
                available_models,
                key="model_select",
                label_visibility="collapsed"
            )
        else:
            st.warning("No models found. Run `ollama pull llama3.2`")
        
        st.divider()
        
        # Info section
        st.markdown('<div class="sidebar-section-label">Info</div>', unsafe_allow_html=True)
        with st.expander("ℹ️ About"):
            file_count = len(st.session_state.get("file_uploads", []))
            msg_count = len(st.session_state.get("messages", []))
            st.info(
                f"**Model:** {selected_model or 'None'}\n\n"
                f"**Files:** {file_count}\n\n"
                f"**Messages:** {msg_count}\n\n"
                "Upload PDFs and ask questions using RAG-powered retrieval."
            )

    # ── Main Layout ──────────────────────────────────────────
    col1, col2 = st.columns([1.2, 1.8])

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "vector_db" not in st.session_state:
        st.session_state["vector_db"] = None

    # ── Left Column: PDF Upload & Viewer ─────────────────────
    with col1:
        # File upload supporting multiple PDFs
        file_uploads = st.file_uploader(
            "Upload PDF file(s)", 
            type="pdf", 
            accept_multiple_files=True,
            key="pdf_uploader",
            help="Upload one or more PDF files to chat with"
        )

        if file_uploads:
            # Initialize processed files tracking
            if "processed_files" not in st.session_state:
                st.session_state["processed_files"] = set()
            
            # Get current file set
            current_files = {f.name for f in file_uploads}
            processed_files = st.session_state["processed_files"]
            
            # Determine new files
            new_files = current_files - processed_files
            removed_files = processed_files - current_files
            
            # Handle removed files (user deselected some files)
            if removed_files:
                if st.session_state["vector_db"] is not None:
                    st.session_state["vector_db"].delete_collection()
                    st.session_state["vector_db"] = None
                    st.session_state.pop("pdf_pages", None)
                st.session_state["processed_files"] = set()
                st.session_state["file_uploads"] = []
                new_files = current_files
            
            # Process new files
            if new_files:
                new_file_objects = [f for f in file_uploads if f.name in new_files]
                file_count = len(new_file_objects)
                
                if st.session_state["vector_db"] is None:
                    with st.spinner(f"Processing {file_count} PDF file(s)..."):
                        st.session_state["vector_db"] = create_vector_db(new_file_objects)
                        st.session_state["processed_files"].update(new_files)
                        st.session_state["file_uploads"] = file_uploads
                        
                        all_pages = []
                        for file_upload in file_uploads:
                            with pdfplumber.open(file_upload) as pdf:
                                all_pages.extend([page.to_image().original for page in pdf.pages])
                        st.session_state["pdf_pages"] = all_pages
                else:
                    with st.spinner(f"Adding {file_count} new PDF file(s)..."):
                        add_files_to_vector_db(new_file_objects, st.session_state["vector_db"])
                        st.session_state["processed_files"].update(new_files)
                        st.session_state["file_uploads"] = file_uploads
                        
                        all_pages = st.session_state.get("pdf_pages", [])
                        for file_upload in new_file_objects:
                            with pdfplumber.open(file_upload) as pdf:
                                all_pages.extend([page.to_image().original for page in pdf.pages])
                        st.session_state["pdf_pages"] = all_pages
                
                st.success(f"✅ Processed {file_count} PDF file(s)")
            
            # Display uploaded file pills
            if "file_uploads" in st.session_state and st.session_state["file_uploads"]:
                file_pills_html = '<div class="file-pills">'
                for f in st.session_state["file_uploads"]:
                    file_pills_html += f'<span class="file-pill">📄 {f.name}</span>'
                file_pills_html += '</div>'
                st.markdown(file_pills_html, unsafe_allow_html=True)

        # Display PDF if pages are available
        if "pdf_pages" in st.session_state and st.session_state["pdf_pages"]:
            total_pages = len(st.session_state["pdf_pages"])
            
            st.markdown(f"""
                <div class="card-header">
                    <div class="card-header-title">📄 Document Preview</div>
                    <div class="card-header-badge">{total_pages} page{'s' if total_pages != 1 else ''}</div>
                </div>
            """, unsafe_allow_html=True)
            
            zoom_level = st.slider(
                "Zoom Level", 
                min_value=100, 
                max_value=1000, 
                value=700, 
                step=50,
                key="zoom_slider"
            )

            with st.container(height=410, border=True):
                for page_image in st.session_state["pdf_pages"]:
                    st.image(page_image, width=zoom_level)

        # Delete collection button
        st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
        delete_collection = st.button(
            "⚠️ Delete collection", 
            type="secondary",
            key="delete_button"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if delete_collection:
            delete_vector_db(st.session_state["vector_db"])

    # ── Right Column: Chat Interface ─────────────────────────
    with col2:
        message_container = st.container(height=550, border=True)

        # Display chat history
        with message_container:
            if not st.session_state["messages"] and st.session_state["vector_db"] is None:
                st.markdown("""
                    <div class="empty-state">
                        <div class="empty-state-icon">📄</div>
                        <div class="empty-state-title">Upload a PDF to Begin</div>
                        <div class="empty-state-desc">Upload one or more PDF files, then ask questions about their content</div>
                    </div>
                """, unsafe_allow_html=True)
            elif not st.session_state["messages"]:
                st.markdown("""
                    <div class="empty-state">
                        <div class="empty-state-icon">💬</div>
                        <div class="empty-state-title">Ready to Chat</div>
                        <div class="empty-state-desc">Your documents are loaded. Ask a question below!</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                for message in st.session_state["messages"]:
                    avatar = "🤖" if message["role"] == "assistant" else "👤"
                    with st.chat_message(message["role"], avatar=avatar):
                        st.markdown(message["content"])

        # Chat input and processing
        if prompt := st.chat_input("Ask about your documents...", key="chat_input"):
            try:
                # Add user message to chat
                st.session_state["messages"].append({"role": "user", "content": prompt})
                with message_container.chat_message("user", avatar="👤"):
                    st.markdown(prompt)

                # Process and display assistant response
                with message_container.chat_message("assistant", avatar="🤖"):
                    with st.spinner(":green[processing...]"):
                        if st.session_state["vector_db"] is not None:
                            response = process_question(
                                prompt, st.session_state["vector_db"], selected_model
                            )
                            st.markdown(response)
                        else:
                            st.warning("Please upload a PDF file first.")

                # Add assistant response to chat history
                if st.session_state["vector_db"] is not None:
                    st.session_state["messages"].append(
                        {"role": "assistant", "content": response}
                    )

            except Exception as e:
                st.error(e, icon="⛔️")
                logger.error(f"Error processing prompt: {e}")
