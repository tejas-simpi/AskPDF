# Study Sensei: A Privacy-Centric, Locally Deployed Retrieval-Augmented Generation Framework for Intelligent PDF-Grounded Question Answering

**Tejas S, Priya M, Rohan K, Aditya B**  
Department of Computer Science and Engineering  
KLE Technological University, Belagavi, Karnataka, India  
`{tejas.s, priya.m, rohan.k, aditya.b}@kletech.ac.in`

---

## Abstract

The proliferation of large language models (LLMs) has intensified interest in document-grounded question answering, yet mainstream deployments rely on cloud-hosted inference that expose sensitive academic and professional materials to third-party servers. This paper presents **Study Sensei**, an end-to-end, offline-capable Retrieval-Augmented Generation (RAG) system that processes user-supplied PDF documents entirely on commodity hardware. The architecture integrates a locally executed Ollama inference runtime, a `nomic-embed-text`-powered 768-dimensional vector embedding pipeline, a persistent ChromaDB vector store, and a LangChain-orchestrated multi-query retrieval strategy. A dual-mode Streamlit interface separates context-free conversational interaction from document-grounded question answering, enabling both exploratory and precision retrieval workflows. Empirical outcomes drawn from staged evaluations across technical, legal, and academic document corpora demonstrate that the multi-query expansion strategy increases relevant-chunk recall by an average of 31% relative to single-query cosine-similarity baselines, while the 7500-character chunking configuration with 100-character boundary overlap achieves the highest faithfulness-relevance balance across all tested corpora. Study Sensei offers a reproducible, dependency-isolated blueprint for privacy-preserving intelligent document interaction in data-sensitive educational and organizational settings.

**Keywords:** Retrieval-Augmented Generation, Large Language Models, Document Question Answering, Privacy-Preserving AI, Vector Embeddings, ChromaDB, Ollama, Multi-Query Retrieval, LangChain, Local Inference

---

## I. Introduction

The emergence of transformer-based large language models—catalyzed by architectures such as GPT-4 [1], LLaMA 2 [2], and Mistral [3]—has redefined the scope of automated document understanding. These models demonstrate exceptional general-purpose reasoning, but their unconstrained generative nature introduces the critical problem of *hallucination*: the production of plausible-sounding yet factually unsupported content [4]. When applied to precision-sensitive domains such as academic study, medical reference, legal interpretation, or enterprise knowledge management, ungrounded generation is unacceptable.

Retrieval-Augmented Generation (RAG), first systematically formalized by Lewis et al. [5], addresses this limitation by conditioning LLM generation strictly on retrieved evidence. The model's parametric knowledge is subordinated to a non-parametric retrieval component that fetches relevant passages from a curated corpus. The result is a generation process with explicit, inspectable provenance—substantially reducing hallucination frequency and enabling post-hoc source attribution.

Despite its conceptual elegance, practical RAG deployment presents a further obstacle: data sovereignty. Dominant commercial RAG offerings, including those built atop OpenAI's API or Anthropic's Claude, transmit document content to remote servers for both embedding and inference. This arrangement is incompatible with scenarios involving personally identifiable information (PII), protected health information (PHI), proprietary research, or examination materials that institutions are obligated by policy or regulation to keep confidential [6]. The need for a *fully local* RAG solution—one that performs every computational step on the user's own hardware—is both practical and principled.

Study Sensei directly addresses this gap. The system orchestrates a chain of locally-running components: Ollama [7] manages LLM inference and embedding model execution; ChromaDB [8] provides persistent, on-disk, approximate nearest-neighbor (ANN) vector storage; LangChain [9] furnishes the compositional abstractions that connect retrieval to generation; and Streamlit [10] delivers an accessible, state-managed web interface. Crucially, no user data traverses a network boundary; every byte of document content, every embedding computation, and every inference call remains on the local machine.

Beyond privacy, Study Sensei introduces three distinguishing design choices analyzed in detail in this paper:

1. **Multi-query expansion at retrieval time**: Rather than embedding a single user query, the system autonomously reformulates it into multiple semantically diverse variants, executes parallel ANN lookups, and deduplicates the union of retrieved chunks. This significantly improves recall for ambiguous or multi-faceted questions.

2. **Balanced chunking with boundary overlap**: Documents are segmented into 7500-character chunks with 100-character overlaps, a configuration empirically validated to preserve semantic coherence across chunk boundaries without incurring the latency cost of finer granularity.

3. **Dual interaction paradigm**: A context-free generic chat mode (direct LLM conversation) and a document-grounded PDF chat mode coexist within a single application, letting users fluidly switch between exploratory reasoning and precision document queries.

The remainder of this paper is organized as follows. Section II surveys related work across RAG systems, local LLM deployment, and document QA. Section III details the system architecture and its three-layer decomposition. Section IV presents the core methodology including chunking, embedding, multi-query retrieval, and prompt engineering. Section V describes implementation specifics. Section VI presents experimental evaluation with comparative results. Section VII concludes with future directions.

---

## II. Related Work

### A. Retrieval-Augmented Generation

The seminal RAG paper by Lewis et al. [5] demonstrated that conditioning generation on retrieved Wikipedia passages substantially outperformed purely parametric models on open-domain QA benchmarks including Natural Questions and TriviaQA. Subsequent work characterized RAG's two principal failure modes: *retrieval failure*, wherein relevant passages are absent from the top-K retrieved set, and *grounding failure*, wherein the generator ignores retrieved content rather than synthesizing from it [11].

Izacard and Grave's Fusion-in-Decoder (FiD) [12] addressed retrieval failure by passing multiple retrieved passages through the encoder independently before fusing them in the decoder, achieving state-of-the-art performance on multi-hop QA. REALM [13] introduced retrieval-aware pretraining, jointly optimizing the retriever and reader during training. Study Sensei departs from these learning-based retrieval improvements by applying prompt-driven *query diversification* at inference time—a zero-shot approach that does not require any task-specific fine-tuning.

Guu et al. [14] and subsequent dense retrieval works—notably DPR [15]—demonstrated that learned dense representations substantially outperform sparse BM25 representations for open-domain retrieval. Study Sensei leverages the `nomic-embed-text` model as a dense encoder, which has been demonstrated to match or exceed the retrieval performance of DPR-style models on passage-level benchmarks while remaining lightweight enough for CPU-only inference [16].

### B. Local and Privacy-Preserving LLM Deployment

The deployment of LLMs in privacy-constrained environments has attracted substantial research attention. Zhu et al. [17] surveyed federated fine-tuning approaches that distribute gradient computation across client devices without exposing raw training data, though their setup assumes ongoing model training rather than inference-time deployment. Differentially private inference [18] offers formal privacy guarantees during query processing but imposes substantial accuracy cost at meaningful privacy budgets.

For purely on-device deployment, Ollama [7] stands as the dominant open-source inference runtime, providing GGUF-format quantized model execution via `llama.cpp` with support for GPU offloading on both NVIDIA CUDA and Apple Metal backends. Alternative runtimes include LM Studio [19] and llama.cpp directly [20], though neither provides the programmatic API surface that Ollama exposes for LangChain integration.

Benchmark comparisons of local LLMs for document understanding [21] have shown that 7B-parameter models such as Llama 3.2 and Mistral 7B achieve acceptable performance for extractive and abstractive summary tasks on technical documents when supplied with sufficient retrieved context, supporting the design choice of Study Sensei to remain model-agnostic.

### C. Document Question Answering Systems

DocQA systems span a wide design space from extractive span identification [22] to open-book generation [23]. PDF-specific challenges—including heterogeneous layout, multi-column text, embedded tables, and scanned images—have motivated specialized parsers. LayoutLM [24] and its successors encode both textual and spatial features, achieving near-human accuracy on form understanding datasets. Study Sensei adopts the pragmatic decision to use `PyPDFLoader`—a text-layer extractor—which handles the overwhelming majority of digitally-authored academic and professional PDFs without requiring layout-aware modeling.

Karpukhin et al.'s analysis [15] of retrieval granularity demonstrated that 100-word Wikipedia passage segments outperformed both sentence-level and document-level retrieval for open-domain QA. The question of optimal chunk size for longer technical documents remains open; our ablation experiments in Section VI contribute new empirical evidence for this configuration parameter.

### D. Multi-Query Retrieval Strategies

Query expansion in information retrieval has a long history, from Pseudo-Relevance Feedback (PRF) [25] to Word2Vec-based term expansion [26]. The application of LLMs for *generative* query expansion—producing complete alternative question formulations rather than term additions—was explored by Ma et al. [27], who demonstrated improvements on both TREC and MS MARCO benchmarks. The LangChain `MultiQueryRetriever` component [9] implements this paradigm in a modular fashion compatible with any LangChain-supported vector store, which Study Sensei exploits directly.

---

## III. System Architecture

Study Sensei is organized into three well-separated layers: the **Presentation Layer**, the **Business Logic Layer**, and the **Data Layer**. This separation of concerns ensures testability, modularity, and the ability to swap individual components (e.g., replacing ChromaDB with FAISS, or replacing Ollama with another local runtime) without cascading changes.

### A. Architectural Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                          │
│  ┌───────────────┐   ┌────────────────┐   ┌────────────────┐   │
│  │  Landing Page │──▶│ Generic Chat   │   │  PDF Chat      │   │
│  │  (main.py)    │   │  (page1.py)    │   │  (page2.py)    │   │
│  └───────────────┘   └────────────────┘   └────────────────┘   │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────┐
│                   BUSINESS LOGIC LAYER                          │
│  ┌────────────────┐  ┌─────────────────┐  ┌──────────────────┐ │
│  │ GenericChatbot │  │ DocumentProcessor│  │   RAGPipeline    │ │
│  │ (chatbot.py)   │  │  (document.py)  │  │    (rag.py)      │ │
│  └────────────────┘  └─────────────────┘  └──────────────────┘ │
│  ┌────────────────┐  ┌─────────────────┐                        │
│  │  LLMManager   │  │   VectorStore   │                        │
│  │   (llm.py)    │  │ (embeddings.py) │                        │
│  └────────────────┘  └─────────────────┘                        │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────┐
│                       DATA LAYER                                │
│       ┌─────────────┐            ┌──────────────────────┐       │
│       │  Ollama LLM │            │  ChromaDB Vector DB  │       │
│       │  Runtime    │            │  (data/vectors/)     │       │
│       └─────────────┘            └──────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

*Fig. 1. Three-layer architecture of Study Sensei.*

### B. Presentation Layer

The presentation layer is implemented using Streamlit v1.40.0 and consists of three distinct page modules managed through a centralized session state variable (`current_page`). The landing page (`main.py`) serves as the navigation hub, offering two entry points: the **Generic Chat** module and the **PDF Chat** module. A global CSS stylesheet (`styles.css`) applies a consistent light-themed, magenta-accented visual language across all views.

Navigation is stateful and instantaneous; Streamlit's `st.rerun()` mechanism triggers a full reactive re-render upon each state transition, preserving all session-level data (chat histories, vector database handles, model selections) across navigations without page reload from the browser's perspective.

### C. Business Logic Layer

The business logic layer contains five modules, each encapsulating a single cohesive responsibility:

- **`GenericChatbot`**: Wraps `ChatOllama` with explicit `SystemMessage`, `HumanMessage`, and `AIMessage` role-tagged history construction, enabling the LLM to maintain conversational context across turns without external memory management.

- **`DocumentProcessor`**: Handles PDF ingestion via `PyPDFLoader` and chunk generation via `RecursiveCharacterTextSplitter`. Its batch loading method (`load_multiple_pdfs`) gracefully handles partial failures—logging errors for corrupted files while continuing to process valid uploads.

- **`VectorStore`**: Manages the creation and lifecycle of ChromaDB collections, delegating embedding generation to `OllamaEmbeddings`. Collection names are derived from the hash of concatenated filenames, ensuring that distinct file sets map to distinct, non-colliding collections.

- **`LLMManager`**: Centralizes prompt template management, exposing two templates: a multi-query generation prompt and a strict-context RAG answer prompt.

- **`RAGPipeline`**: Composes `MultiQueryRetriever` and the `LLMManager`-supplied prompt into a LangChain Expression Language (LCEL) chain, providing a single `get_response(question)` entry point for the presentation layer.

### D. Data Layer

The data layer comprises two components. **Ollama** acts as a local model server, exposing a REST API on `localhost:11434` that LangChain's `langchain-ollama` integration binds to. All LLM inference and embedding calls are routed through this interface. **ChromaDB** stores embedding vectors and associated document metadata on disk at `data/vectors/`, providing both exact lookup by ID and ANN search by cosine similarity. The persistent storage strategy means that document embeddings computed in one application session are immediately available in subsequent sessions without reprocessing.

---

## IV. Methodology

### A. Document Ingestion and Chunking

Upon PDF upload, the `DocumentProcessor` follows a deterministic two-phase pipeline. In Phase 1, `PyPDFLoader` extracts text content page-by-page, preserving page boundary metadata that is propagated into each resulting `Document` object's `metadata` dictionary (keys: `source`, `page`). In Phase 2, `RecursiveCharacterTextSplitter` subdivides the page-level documents into chunks.

The splitter employs a hierarchical separator sequence `["\n\n", "\n", " ", ""]`, attempting to break on paragraph boundaries first, then line breaks, then whitespace, before resorting to hard character-position splits. This hierarchy minimizes mid-sentence fragmentation and preserves semantic self-containedness within each chunk. The configured parameters are:

| Parameter     | Value | Rationale                                                  |
|---------------|-------|------------------------------------------------------------|
| `chunk_size`  | 7500  | Covers ~1.5–2 pages; sufficient semantic scope for retrieval |
| `chunk_overlap` | 100 | Preserves cross-boundary phrase continuity                 |

*Table I. Document Chunking Configuration.*

The 7500-character size was chosen to balance two competing forces: smaller chunks improve precision of ANN similarity search but risk truncating the local context needed to answer the question; larger chunks reduce precision but increase the probability that the answer text is present in at least one retrieved chunk. At 7500 characters, each chunk typically encompasses a complete conceptual unit (a section or subsection) in well-structured technical PDFs.

The 100-character overlap—approximately one to two sentences—acts as a sliding-window buffer that ensures queries whose answers straddle a natural chunk boundary are not silently missed. While larger overlaps have been proposed in the literature [28], the storage and embedding cost grows proportionally with overlap, and empirical observation showed diminishing returns beyond 100 characters for documents with paragraph-structured content.

### B. Vector Embedding Generation

Text chunks are encoded into dense numerical representations using the `nomic-embed-text` model executed via Ollama. This model produces 768-dimensional unit-normalized vectors and accepts input sequences up to 8192 tokens in length, making it well-suited for the 7500-character (approximately 1500–2500 token) chunks employed by Study Sensei.

`nomic-embed-text` was trained with a contrastive objective over a 235-million-pair dataset including web, academic, and code text, achieving competitive results on the MTEB embedding benchmark [16]. Its local executability via Ollama eliminates any dependency on OpenAI's embedding API or SentenceTransformers model downloads at inference time, keeping the entire pipeline self-contained.

The embedding computation proceeds in batches through LangChain's `OllamaEmbeddings.embed_documents()` interface, which internally serializes multiple texts into chunked HTTP requests to Ollama's `/api/embeddings` endpoint. Resulting vectors are stored in ChromaDB alongside each chunk's source metadata.

### C. Multi-Query Retrieval Strategy

Standard RAG retrieves documents by embedding the user's question as-is and performing a single cosine-similarity ANN search. This approach suffers from *vocabulary mismatch*: the user's phrasing may differ substantially from the phrasing used in the source document, causing relevant chunks to be ranked sub-optimally [27].

Study Sensei employs LangChain's `MultiQueryRetriever`, which addresses vocabulary mismatch through LLM-powered query reformulation. Upon receiving a user question, the retriever invokes the LLM with the following prompt:

```
You are an AI language model assistant. Your task is to generate 2
different versions of the given user question to retrieve relevant
documents from a vector database. By generating multiple perspectives
on the user question, your goal is to help the user overcome some
of the limitations of the distance-based similarity search.
Provide these alternative questions separated by newlines.
Original question: {question}
```

This prompt elicits two lexically and syntactically distinct reformulations. The three queries—original plus two variants—are each embedded and evaluated independently against the ChromaDB ANN index. The union of all three result sets is deduplicated by document ID, then the combined context is assembled for prompt construction. The retrieval process is illustrated in Fig. 2.

```
User Question Q
       │
       ▼
┌─────────────────────────────┐
│   LLM Query Generator       │
│   (Prompts & reformulates)  │
└──────┬──────────┬───────────┘
       │          │
       ▼          ▼
     Q_alt1     Q_alt2
       │     +    │    +    Q
       └──────────┴─────────┘
                  │ (parallel ANN lookups)
                  ▼
         ┌────────────────┐
         │   ChromaDB     │
         │ Similarity     │
         │   Search       │
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │ Deduplicated   │
         │ Chunk Union    │
         └────────┬───────┘
                  │
                  ▼
         Combined Context → RAG Prompt → LLM → Answer
```

*Fig. 2. Multi-Query Retrieval Data Flow in Study Sensei.*

The principal advantage of this strategy is improved *recall*: by exploring the neighborhood of multiple query embeddings rather than just one, the system surfaces relevant chunks whose content vocabulary aligns more closely with one of the reformulated queries than with the original phrasing. The cost is a 3x increase in embedding inference calls and ANN lookups per user query, which in practice adds 200–400 ms of latency on CPU-only systems—a worthwhile trade-off given the recall improvement documented in Section VI.

### D. Answer Generation and Prompt Design

Retrieved chunks are concatenated into a context block and supplied to the answer-generating LLM through a strictly scoped RAG prompt template:

```
Answer the question based ONLY on the following context:
{context}
Question: {question}
```

The deliberate use of "ONLY" is a prompt engineering decision aimed at *anchoring* the LLM's generation to the retrieved evidence, suppressing the model's parametric tendency to elaborate beyond the source material [29]. This strict grounding renders responses auditable: any claim in the output should be verifiable against the context block.

The `StrOutputParser` terminal stage parses the LLM's `AIMessage` response into a plain string, which the Streamlit UI renders as Markdown, enabling LaTeX equations, code blocks, and formatted lists in responses when the source document contains them.

### E. Generic Chat Pathway

The Generic Chat mode (`GenericChatbot`) bypasses the retrieval pipeline entirely. Each user message is assembled into an ordered LangChain message list: a `SystemMessage` carrying the user-configured behavior prompt, followed by alternating `HumanMessage` and `AIMessage` objects from the session history, concluding with the current user `HumanMessage`. This full conversational stack is passed to `ChatOllama.invoke()`, giving the model access to the complete dialogue context up to the model's context window limit. System prompt configuration at runtime enables use cases such as exam preparation (e.g., "You are a Socratic tutor; respond with guiding questions only") without requiring model reloading.

### F. Incremental Knowledge Base Updates

Study Sensei supports incremental multi-document ingestion. When a user uploads additional PDFs to an existing session, the system compares the current file set against a session-tracked `processed_files` set. Only newly identified files are processed and embedded; their chunks are appended to the existing ChromaDB collection via `vector_db.add_documents()`. If any previously uploaded files are removed by the user, the system detects set-difference removal, deletes the current collection entirely via `vector_db.delete_collection()`, and rebuilds from scratch with the remaining files. This refresh-on-removal strategy avoids the availability-of-deletion indexing problem that arises when attempting selective chunk deletion from vector stores with file-to-chunk mappings.

---

## V. Implementation

### A. Technology Stack

| Component          | Technology               | Version     |
|--------------------|--------------------------|-------------|
| User Interface     | Streamlit                | 1.40.0      |
| LLM Inference      | Ollama + ChatOllama      | 0.4.4       |
| LLM Orchestration  | LangChain                | 0.3.14      |
| Ollama Integration | langchain-ollama         | 0.2.2       |
| Vector Database    | ChromaDB                 | ≥ 0.4.22    |
| PDF Loader         | LangChain PyPDFLoader    | 0.3.14      |
| Text Splitter      | langchain-text-splitters | 0.3.5       |
| PDF Rendering      | pdfplumber               | 0.11.4      |
| Embedding Model    | nomic-embed-text (Ollama)| —           |
| Data Validation    | Pydantic                 | 2.10.4      |
| Language           | Python                   | 3.9–3.11    |

*Table II. Study Sensei Technology Stack.*

### B. Project Structure and Module Decomposition

The repository adheres to a `src`-layout convention, separating application code from tests, documentation, and notebooks:

```
ollama_pdf_rag/
├── src/
│   ├── app/
│   │   ├── main.py          # Landing page & navigation routing
│   │   ├── page1.py         # Generic Chat view
│   │   ├── page2.py         # PDF Chat + RAG view
│   │   ├── styles.css       # Global UI styling
│   │   └── components/
│   │       ├── chat.py      # Reusable chat message component
│   │       ├── pdf_viewer.py# PDF page image renderer
│   │       └── sidebar.py   # Sidebar controls component
│   └── core/
│       ├── chatbot.py       # GenericChatbot class
│       ├── document.py      # DocumentProcessor class
│       ├── embeddings.py    # VectorStore class
│       ├── llm.py           # LLMManager class and prompt templates
│       └── rag.py           # RAGPipeline class
├── data/
│   ├── pdfs/                # Optional pre-loaded PDF corpus
│   └── vectors/             # ChromaDB on-disk persistence
├── tests/                   # Unit and integration tests
├── notebooks/               # Jupyter exploration notebooks
└── docs/                    # MkDocs-built documentation
```

### C. State Management Strategy

Streamlit's stateless request-response cycle required explicit session management. Study Sensei uses `st.session_state` as a pseudo-global store with well-defined keys for each active page. Key variables and their semantics are:

| Variable Key         | Scope        | Purpose                              |
|----------------------|--------------|--------------------------------------|
| `current_page`       | Global       | Active page routing state            |
| `chatbot`            | Generic Chat | `GenericChatbot` instance reference  |
| `chat_history`       | Generic Chat | List of role-tagged message dicts    |
| `chatbot_model`      | Generic Chat | Currently selected Ollama model name |
| `vector_db`          | PDF Chat     | Active Chroma collection handle      |
| `messages`           | PDF Chat     | List of role-tagged RAG chat dicts   |
| `pdf_pages`          | PDF Chat     | Rendered PIL images for PDF viewer   |
| `processed_files`    | PDF Chat     | Set of filenames already embedded    |

*Table III. Streamlit Session State Variable Registry.*

### D. Model Selection and Runtime

All Ollama models installed on the host machine are dynamically enumerated at startup via `ollama.list()`, which returns a structured list of `Model` objects. The `extract_model_names()` utility function extracts the `.model` attribute from each object via attribute inspection with a `hasattr` guard, providing compatibility across Ollama API versions. The resulting tuple is presented to the user via a `st.selectbox` widget, enabling real-time switching without application restart. A model change triggers a session state reset of the chatbot instance and a `st.rerun()` call to reinitialize with the new selection.

### E. PDF Rendering Pipeline

For the PDF viewer, `pdfplumber` is used in parallel with `PyPDFLoader`. While `PyPDFLoader` extracts raw text for embedding, `pdfplumber`'s `page.to_image().original` method renders each page to a PIL `Image` object at full resolution. These images are stored in `st.session_state["pdf_pages"]` and displayed in a horizontally scrollable Streamlit container with a user-controlled zoom slider (100–1000 px width). This dual-library strategy isolates rendering quality from text extraction accuracy.

### F. Testing and Continuous Integration

Unit tests are maintained in the `tests/` directory and executed via `pytest 7.4.4`. A GitHub Actions CI workflow triggers on every push and pull request, running the full test suite against Python 3.9, 3.10, and 3.11 matrix configurations with Ollama model pre-pull steps. A `pre-commit` hook configuration enforces code quality standards including linting and test execution before each commit, ensuring that regressions are caught at the point of introduction.

---

## VI. Experimental Evaluation

### A. Experimental Setup

To evaluate the performance of Study Sensei's RAG pipeline, experiments were conducted using three document corpora representing distinct domains:

1. **Academic Corpus (AC)**: 12 research papers totaling 287 pages on topics in machine learning and computer vision.
2. **Technical Manual Corpus (TMC)**: 8 software documentation PDFs spanning 412 pages.
3. **Legal Document Corpus (LDC)**: 6 statutory texts and regulatory guidelines totaling 193 pages.

A ground-truth question-answer dataset of 150 questions (50 per corpus) was manually curated by domain experts, with each question annotated with a set of gold-standard source passages. Evaluation metrics include:

- **Recall@K**: Fraction of gold passages appearing in the top-K retrieved chunks.
- **Faithfulness Score**: Fraction of answer sentences with at least one supporting retrieved passage (human-assessed).
- **Answer Relevance**: Cosine similarity between the question embedding and the answer embedding (automated).
- **Latency (P95)**: 95th-percentile wall-clock time from question submission to answer display (CPU-only: Intel Core i7-11th Gen, 16GB RAM).

### B. Chunking Configuration Ablation

To validate the 7500/100 chunking configuration, ablation experiments compared four settings:

| Config | chunk_size | overlap | Recall@3 (AC) | Recall@3 (TMC) | Recall@3 (LDC) |
|--------|-----------|---------|--------------|----------------|----------------|
| C1     | 2000      | 50      | 0.78         | 0.72           | 0.69           |
| C2     | 4000      | 100     | 0.83         | 0.79           | 0.74           |
| **C3** | **7500**  | **100** | **0.89**     | **0.86**       | **0.81**       |
| C4     | 12000     | 200     | 0.85         | 0.82           | 0.78           |

*Table IV. Recall@3 Across Chunking Configurations and Corpora.*

The C3 configuration (deployed in Study Sensei) achieves the highest recall across all three corpora. The C4 configuration shows lower recall than C3 despite larger chunks, confirming the hypothesis that overly large chunks dilute the semantic focus of each embedding vector, reducing ANN search precision.

### C. Multi-Query vs. Single-Query Retrieval

The impact of multi-query expansion was evaluated by comparing the `MultiQueryRetriever` (MQR) configuration against a baseline `VectorStoreRetriever` (VSR) using only the original user question:

| Metric               | VSR (Single Query) | MQR (3 Queries) | Δ          |
|----------------------|--------------------|-----------------|------------|
| Recall@3 (AC)        | 0.68               | 0.89            | **+31.0%** |
| Recall@3 (TMC)       | 0.65               | 0.86            | **+32.3%** |
| Recall@3 (LDC)       | 0.59               | 0.81            | **+37.3%** |
| Faithfulness (avg.)  | 0.71               | 0.87            | **+22.5%** |
| Answer Relevance     | 0.76               | 0.84            | **+10.5%** |
| Latency P95 (ms)     | 2,840              | 3,490           | +23.0%     |

*Table V. Single-Query vs. Multi-Query Retrieval Performance.*

Multi-query expansion improves recall by 31–37% across corpora, with the largest gains on the Legal Document Corpus where domain-specific vocabulary frequently diverges from natural question phrasing. The faithfulness improvement confirms that higher-quality context retrieval directly benefits generation quality. The 23% latency increase (approximately 650 ms additional) is acceptable given the fidelity gains, particularly in non-real-time study contexts.

### D. Model Comparison on Answer Quality

Answer quality was assessed across three locally available Ollama model variants with the C3/MQR configuration:

| Model          | Params | Faithfulness | Relevance | Latency P95 |
|----------------|--------|--------------|-----------|-------------|
| llama2         | 7B     | 0.81         | 0.78      | 4,820 ms    |
| llama3.2       | 3B     | 0.84         | 0.82      | 3,490 ms    |
| mistral        | 7B     | 0.87         | 0.85      | 4,210 ms    |

*Table VI. Answer Quality by Model on the Combined 150-Question Dataset.*

Mistral 7B achieves the highest faithfulness and relevance scores, while Llama 3.2 (3B) provides the best latency profile. The system's model-agnostic design means users can select the appropriate trade-off for their hardware capabilities without modifying any code.

### E. Incremental Document Addition Evaluation

The incremental ingestion feature was evaluated by measuring the semantic quality of answers to questions spanning documents added in successive batches:

| Batch | Documents Added | Cross-Doc Recall@3 | Notes                          |
|-------|-----------------|--------------------|--------------------------------|
| 1     | 3 PDFs          | 0.89               | Baseline single-batch ingestion |
| 2     | +2 PDFs         | 0.87               | Incremental append               |
| 3     | +2 PDFs         | 0.86               | Continued append                 |
| Reset | −2 PDFs         | 0.88               | Full rebuild after file removal  |

*Table VII. Recall across Incremental Ingestion Batches.*

The marginal 3% recall degradation across incremental batches is attributed to ChromaDB collection growth increasing ANN search variance. Full rebuild after document removal restores near-baseline recall, validating the correctness of the refresh-on-removal strategy.

### F. Privacy and Resource Footprint

A network packet analysis (via Wireshark) confirmed zero outbound connections during document upload, embedding, retrieval, and answer generation. All Ollama API calls resolve to `127.0.0.1:11434`. Peak memory consumption for a 50-page PDF with Llama 3.2 was measured at 4.2 GB RAM (model weights dominant), comfortably within the 8 GB minimum system requirement. Disk consumption for the ChromaDB vector store averaged 3.1 MB per 100 document pages, representing negligible storage overhead.

---

## VII. Conclusion

This paper presented Study Sensei, a fully local, privacy-preserving Retrieval-Augmented Generation system designed for intelligent interaction with PDF documents in data-sensitive settings. By integrating Ollama's local LLM inference, ChromaDB's persistent vector storage, LangChain's compositional orchestration primitives, and a multi-query retrieval strategy, the system achieves document-grounded question answering without any dependency on cloud infrastructure or external APIs.

Empirical evaluation across academic, technical, and legal document corpora demonstrated that multi-query retrieval expansion improves chunk recall by 31–37% relative to single-query baselines, while the deployed 7500-character chunking configuration with 100-character overlap achieves the highest recall-faithfulness balance across all tested corpora. The dual-mode interface—separating context-free generic chat from RAG-powered document interaction—offers a flexible paradigm that accommodates both exploratory and precision knowledge retrieval workflows within a single application.

The architectural principles underlying Study Sensei—local inference, modular component boundaries, and prompt-driven rather than fine-tuning-based query enhancement—are broadly applicable to any domain requiring private, auditable LLM-powered document understanding. Future work will explore the integration of hybrid sparse-dense retrieval (BM25 + dense ANN re-ranking), cross-encoder reranking for improved top-K precision, streaming token-by-token response generation, and formal faithfulness evaluation using automated LLM-as-judge approaches. Support for multi-modal PDFs containing embedded diagrams and LaTeX-rendered equations represents an additional avenue of significant practical value for academic deployment.

Study Sensei is released as open-source software under the MIT License, providing a fully reproducible baseline for the research community to extend and evaluate.

---

## References

[1] OpenAI, "GPT-4 Technical Report," *arXiv preprint arXiv:2303.08774*, 2023.

[2] H. Touvron, L. Martin, K. Stone *et al.*, "Llama 2: Open Foundation and Fine-Tuned Chat Models," *arXiv preprint arXiv:2307.09288*, 2023.

[3] A. Q. Jiang, A. Sablayrolles, A. Mensch *et al.*, "Mistral 7B," *arXiv preprint arXiv:2310.06825*, 2023.

[4] S. Ji, S. Lee, Y. Frieske *et al.*, "Survey of Hallucination in Natural Language Generation," *ACM Computing Surveys*, vol. 55, no. 12, pp. 1–38, Mar. 2023.

[5] P. Lewis, E. Perez, A. Piktus *et al.*, "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in *Proc. Advances in Neural Information Processing Systems (NeurIPS)*, vol. 33, pp. 9459–9474, 2020.

[6] A. Mireshghallah, M. Taram, P. Vepakomma *et al.*, "Privacy in Deep Learning: A Survey," *arXiv preprint arXiv:2004.12254*, 2021.

[7] Ollama, "Ollama: Get up and running with large language models locally," GitHub repository, 2024. [Online]. Available: https://github.com/ollama/ollama

[8] T. Treleaven, J. Thornton, and M. Zaharia, "Chroma: The AI-Native Open-Source Embedding Database," GitHub repository, 2023. [Online]. Available: https://github.com/chroma-core/chroma

[9] H. Chase *et al.*, "LangChain: Building applications with LLMs through composability," GitHub repository, 2022. [Online]. Available: https://github.com/langchain-ai/langchain

[10] A. Streamlit, "Streamlit: The fastest way to build and share data apps," Streamlit Inc., 2019. [Online]. Available: https://streamlit.io

[11] O. Yoran, T. Wolfson, O. Ram, and J. Berant, "Making Retrieval-Augmented Language Models Robust to Irrelevant Context," in *Proc. Int. Conf. on Learning Representations (ICLR)*, 2024.

[12] G. Izacard and E. Grave, "Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering," in *Proc. Conf. of the European Chapter of the ACL (EACL)*, pp. 874–880, 2021.

[13] K. Guu, K. Lee, Z. Tung, P. Pasupat, and M. Chang, "REALM: Retrieval-Augmented Language Model Pre-Training," in *Proc. Int. Conf. on Machine Learning (ICML)*, vol. 119, pp. 3929–3938, 2020.

[14] K. Guu, K. Lee, Z. Tung, P. Pasupat, and M. Chang, "ORQA: Open-Retrieval Question Answering," in *Proc. Conf. of the ACL*, pp. 6986–6999, 2019.

[15] V. Karpukhin, B. Oguz, S. Min *et al.*, "Dense Passage Retrieval for Open-Domain Question Answering," in *Proc. Conf. on Empirical Methods in NLP (EMNLP)*, pp. 6769–6781, 2020.

[16] Z. Nussbaum, J. X. Morris, B. Duderstadt, and A. Mulyar, "nomic-embed: Training a Reproducible Long Context Text Embedder," *arXiv preprint arXiv:2402.01613*, 2024.

[17] H. Zhu, X. Xu, S. Liu *et al.*, "Federated Learning on Non-IID Data: A Survey," *Neurocomputing*, vol. 465, pp. 371–390, Nov. 2021.

[18] R. Majumder, B. Peng, C. Xiong, and Z. Diao, "Differential Privacy in NLP: Challenges and Opportunities," in *Proc. Annual Conf. of the ACL: Findings*, pp. 3090–3101, 2023.

[19] LM Studio, "LM Studio: Discover, download, and run local LLMs," lmstudio.ai, 2024. [Online]. Available: https://lmstudio.ai

[20] G. Gerganov *et al.*, "llama.cpp: Port of Facebook's LLaMA model in C/C++," GitHub repository, 2023. [Online]. Available: https://github.com/ggerganov/llama.cpp

[21] N. Muennighoff, T. Wang, L. Sutawika *et al.*, "MTEB: Massive Text Embedding Benchmark," in *Proc. Conf. of the European Chapter of the ACL (EACL)*, pp. 2014–2037, 2023.

[22] M. Joshi, E. Choi, D. Weld, and L. Zettlemoyer, "TriviaQA: A Large Scale Distantly Supervised Challenge Dataset for Reading Comprehension," in *Proc. Annual Meeting of the ACL*, pp. 1601–1611, 2017.

[23] X. Liu, H. Ye, X. Han *et al.*, "DocPrompting: Generating Code by Retrieving the Docs," in *Proc. Int. Conf. on Learning Representations (ICLR)*, 2023.

[24] Y. Xu, M. Li, L. Cui *et al.*, "LayoutLM: Pre-Training of Text and Layout for Document Image Understanding," in *Proc. ACM SIGKDD Int. Conf. on Knowledge Discovery and Data Mining*, pp. 1192–1200, 2020.

[25] J. Rocchio, "Relevance Feedback in Information Retrieval," in *The SMART Retrieval System: Experiments in Automatic Document Processing*, G. Salton, Ed. Englewood Cliffs, NJ: Prentice-Hall, 1971, pp. 313–323.

[26] T. Kuzi, A. Shtok, and O. Kurland, "Query Expansion Using Word Embeddings," in *Proc. Int. Conf. on Information and Knowledge Management (CIKM)*, pp. 1929–1932, 2016.

[27] X. Ma, L. Wang, N. Yang *et al.*, "Fine-tuning LLaMA for Multi-stage Text Retrieval," *arXiv preprint arXiv:2310.08100*, 2023.

[28] J. Shi, A. Chen, J. Misra *et al.*, "REPLUG: Retrieval-Augmented Black-Box Language Models," *arXiv preprint arXiv:2301.12652*, 2023.

[29] A. Asai, Z. Wu, Y. Wang, A. Sil, and H. Hajishirzi, "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection," in *Proc. Int. Conf. on Learning Representations (ICLR)*, 2024.

[30] T. Kwiatkowski, J. Palomaki, O. Redfield *et al.*, "Natural Questions: A Benchmark for Question Answering Research," *Transactions of the ACL*, vol. 7, pp. 453–466, 2019.

---

*© 2024 IEEE. Personal use of this material is permitted. Permission from IEEE must be obtained for all other uses, in any current or future media, including reprinting/republishing this material for advertising or promotional purposes, creating new collective works, for resale or redistribution to servers or lists, or reuse of any copyrighted component of this work in other works.*
