# 📄 AskPDF - Local RAG Application

A powerful local RAG (Retrieval Augmented Generation) application that lets you chat with your PDF documents using Ollama and LangChain. Features a dual-mode interface: **Generic Chat** for direct LLM conversations and **PDF Chat** for document-based Q&A. Fully private, secure, and runs entirely on your machine.

## Architecture

AskPDF uses a modern architecture with a **React** frontend and **FastAPI** backend:

```
AskPDF/
├── frontend/                    # React frontend (Vite)
│   ├── src/
│   │   ├── api/                 # API client
│   │   │   └── client.js        # Fetch wrapper for all endpoints
│   │   ├── components/          # Reusable UI components
│   │   │   ├── Chat/            # ChatWindow, ChatMessage, ChatInput
│   │   │   ├── Layout/          # Navbar
│   │   │   ├── PDF/             # PDFUploader, PDFViewer
│   │   │   └── UI/              # EmptyState, LoadingSpinner, ModelSelector, FeatureCard
│   │   ├── pages/               # Page components
│   │   │   ├── Landing.jsx      # Home page with feature cards
│   │   │   ├── GenericChat.jsx  # Context-free LLM chat
│   │   │   └── PDFChat.jsx      # PDF upload + RAG chat
│   │   ├── App.jsx              # Router setup
│   │   ├── main.jsx             # Entry point
│   │   └── index.css            # Design system (dark mode)
│   ├── index.html
│   ├── vite.config.js           # Vite config with API proxy
│   └── package.json
├── src/                          # Python source code
│   └── core/                     # Core RAG functionality
│       ├── chatbot.py            # Generic chatbot (no RAG)
│       ├── document.py           # PDF processing & chunking
│       ├── embeddings.py         # Vector embeddings & ChromaDB
│       ├── llm.py                # LLM configuration & prompts
│       └── rag.py                # RAG pipeline implementation
├── server.py                     # FastAPI backend (REST API)
├── data/                         # Data storage
│   └── vectors/                  # Vector DB persistence
├── tests/                        # Unit tests
├── requirements.txt              # Python dependencies
├── requirements-server.txt       # FastAPI dependencies
├── run_app.py                    # Development runner
└── run.py                        # Legacy Streamlit runner
```

## ✨ Features

### Core Features
- 🔒 **100% Local & Private** - All processing happens on your machine, no data leaves
- 🎯 **Dual-Mode Interface**:
  - **Generic Chat**: Direct conversation with Ollama models
  - **PDF Chat**: RAG-based document Q&A with context-aware responses
- 📄 **Smart PDF Processing**: Intelligent chunking with overlap for better context
- 🧠 **Multi-Query Retrieval**: Generates multiple query variants for comprehensive context
- 🎨 **Premium Dark UI**: Modern React interface with glassmorphism and gradient accents
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

2. **Set Up Python Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-server.txt
   ```

3. **Set Up Frontend**
   ```bash
   cd frontend
   npm install
   ```

### 🎮 Running the Application

You need to run **two** processes:

**Terminal 1 — Backend (FastAPI):**
```bash
python server.py
```
This starts the API server at `http://localhost:8000`

**Terminal 2 — Frontend (React):**
```bash
cd frontend
npm run dev
```
This starts the React dev server at `http://localhost:5173`

Then open your browser to **http://localhost:5173**

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health check |
| `/api/models` | GET | List available Ollama models |
| `/api/chat` | POST | Send message (generic chat) |
| `/api/chat/clear` | POST | Clear chat history |
| `/api/pdf/upload` | POST | Upload PDF files |
| `/api/pdf/ask` | POST | Ask question about PDFs (RAG) |
| `/api/pdf/delete` | DELETE | Delete vector collection |
| `/api/pdf/pages` | GET | Get uploaded PDF page images |

API documentation available at `http://localhost:8000/docs`

## 💡 Usage Tips

### Generic Chat Mode
1. **Select Model**: Choose from locally available Ollama models
2. **Configure System Prompt** (Optional): Set custom behavior for the chatbot
3. **Start Chatting**: Have natural conversations without document context

### PDF Chat Mode
1. **Upload PDFs**: Drag & drop or click to upload multiple PDF files
2. **Select Model**: Choose your preferred Ollama model
3. **Ask Questions**: Query your documents with natural language
4. **Adjust View**: Use zoom slider to resize PDF display
5. **Clean Up**: Use "Delete Collection" button to clear vector database

### Best Practices
- For technical documents, use models like `llama3.2` or `mistral`
- Keep PDFs under 100 pages each for optimal performance
- Use specific questions for better RAG results
- Delete collections when switching to completely different topics

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run tests verbosely
python -m pytest tests/ -v
```

## ⚠️ Troubleshooting

- Ensure Ollama is running in the background
- Check that required models are downloaded (`ollama list` to verify)
- Verify Python environment is activated
- Make sure both the FastAPI server and React dev server are running

---

## 📝 License

This project is open source and available under the MIT License.
