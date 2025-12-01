# 🤖 Study Sensei - Local RAG Application

A powerful local RAG (Retrieval Augmented Generation) application that lets you chat with your PDF documents using Ollama and LangChain. Features a dual-mode interface: **Generic Chat** for direct LLM conversations and **PDF Chat** for document-based Q&A. Fully private, secure, and runs entirely on your machine.

[![Python Tests](https://github.com/tonykipkemboi/ollama_pdf_rag/actions/workflows/tests.yml/badge.svg)](https://github.com/tonykipkemboi/ollama_pdf_rag/actions/workflows/tests.yml)

## Project Structure
```
ollama_pdf_rag/
├── src/                      # Source code
│   ├── app/                  # Streamlit application
│   │   ├── components/       # Reusable UI components
│   │   │   ├── chat.py      # Chat interface component
│   │   │   ├── pdf_viewer.py # PDF display component
│   │   │   └── sidebar.py   # Sidebar controls
│   │   ├── main.py          # Main app with landing page
│   │   ├── page1.py         # Generic Chat (direct LLM)
│   │   ├── page2.py         # PDF Chat (RAG-based)
│   │   └── styles.css       # Custom styling
│   └── core/                 # Core functionality
│       ├── chatbot.py       # Generic chatbot (no RAG)
│       ├── document.py       # PDF processing & chunking
│       ├── embeddings.py     # Vector embeddings & ChromaDB
│       ├── llm.py           # LLM configuration & prompts
│       └── rag.py           # RAG pipeline implementation
├── .streamlit/              # Streamlit configuration
│   └── config.toml          # Theme and UI settings
├── data/                     # Data storage
│   ├── pdfs/                # PDF storage
│   └── vectors/             # Vector DB persistence
├── notebooks/               # Jupyter notebooks
├── tests/                   # Unit tests
├── docs/                    # Documentation
├── TECHNICAL_WORKFLOW.md    # Detailed technical documentation
├── requirements.txt         # Python dependencies
└── run.py                   # Application runner
```

## ✨ Features

### Core Features
- 🔒 **100% Local & Private** - All processing happens on your machine, no data leaves
- 🎯 **Dual-Mode Interface**:
  - **Generic Chat**: Direct conversation with Ollama models
  - **PDF Chat**: RAG-based document Q&A with context-aware responses
- 📄 **Smart PDF Processing**: Intelligent chunking with overlap for better context
- 🧠 **Multi-Query Retrieval**: Generates multiple query variants for comprehensive context
- 🎨 **Modern UI**: Clean, light theme with magenta accents
- 📊 **Multiple PDF Support**: Upload and query across multiple documents
- 💾 **Persistent Vector Store**: ChromaDB storage survives app restarts
- 🔄 **Model Switching**: Choose from any locally available Ollama model
- 📱 **Responsive Layout**: Full-width design optimized for various screen sizes

## 🚀 Getting Started

### Prerequisites

1. **Install Ollama**
   - Visit [Ollama's website](https://ollama.ai) to download and install
   - Pull required models:
     ```bash
     ollama pull llama3.2  # or your preferred model
     ollama pull nomic-embed-text
     ```

2. **Clone Repository**
   ```bash
   git clone https://github.com/tonykipkemboi/ollama_pdf_rag.git
   cd ollama_pdf_rag
   ```

3. **Set Up Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

   Key dependencies and their versions:
   ```txt
   ollama==0.4.4
   streamlit==1.40.0
   pdfplumber==0.11.4
   langchain==0.3.14
   langchain-core==0.3.29
   langchain-ollama==0.2.2
   chromadb>=0.4.22
   ```

### 🎮 Running the Application

#### Option 1: Streamlit Interface
```bash
python run.py
```
Then open your browser to `http://localhost:8501`

**Interface Overview**:
- **Landing Page**: Choose between Generic Chat or PDF Chat
- **Generic Chat**: Talk directly with Ollama models, customize system prompts
- **PDF Chat**: Upload PDFs and ask questions based on document content

#### Option 2: Jupyter Notebook
```bash
jupyter notebook
```
Open `updated_rag_notebook.ipynb` to experiment with the code

## 💡 Usage Tips

### Generic Chat Mode
1. **Select Model**: Choose from locally available Ollama models
2. **Configure System Prompt** (Optional): Set custom behavior for the chatbot
3. **Start Chatting**: Have natural conversations without document context

### PDF Chat Mode
1. **Upload PDFs**: Support for single or multiple PDF files
2. **Select Model**: Choose your preferred Ollama model
3. **Ask Questions**: Query your documents with natural language
4. **Adjust View**: Use zoom slider to resize PDF display
5. **Add More Files**: Upload additional PDFs to expand knowledge base
6. **Clean Up**: Use "Delete Collection" button to clear vector database

### Best Practices
- For technical documents, use models like `llama3.2` or `mistral`
- Keep PDFs under 100 pages each for optimal performance
- Use specific questions for better RAG results
- Delete collections when switching to completely different topics

## 📚 Documentation

For detailed technical information, see [TECHNICAL_WORKFLOW.md](TECHNICAL_WORKFLOW.md):
- System architecture and component diagrams
- Detailed module explanations
- Data flow and processing pipeline
- API reference and code examples
- Performance considerations
- Troubleshooting guide

## ⚠️ Troubleshooting

- Ensure Ollama is running in the background
- Check that required models are downloaded
- Verify Python environment is activated
- For Windows users, ensure WSL2 is properly configured if using Ollama


#### CPU-Only Systems
If you're running on a CPU-only system:

1. Ensure you have the CPU version of ONNX Runtime:
   ```bash
   pip uninstall onnxruntime-gpu  # Remove GPU version if installed
   pip install onnxruntime  # Install CPU-only version
   ```

2. You may need to modify the chunk size in the code to prevent memory issues:
   - Reduce `chunk_size` to 500-1000 if you experience memory problems
   - Increase `chunk_overlap` for better context preservation

Note: The application will run slower on CPU-only systems, but it will still work effectively.

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m unittest discover tests

# Run tests verbosely
python -m unittest discover tests -v
```

### Pre-commit Hooks
The project uses pre-commit hooks to ensure code quality. To set up:

```bash
pip install pre-commit
pre-commit install
```

This will:
- Run tests before each commit
- Run linting checks
- Ensure code quality standards are met

### Continuous Integration
The project uses GitHub Actions for CI. On every push and pull request:
- Tests are run on multiple Python versions (3.9, 3.10, 3.11)
- Dependencies are installed
- Ollama models are pulled
- Test results are uploaded as artifacts

---

## 📝 License

This project is open source and available under the MIT License.
