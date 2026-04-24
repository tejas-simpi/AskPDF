# STUDY SENSEI: A LOCAL RAG-BASED PDF QUESTION-ANSWERING SYSTEM WITH FINE-TUNED LLM

---

**A Project Report**

Submitted in partial fulfillment of the requirements  
for the degree of

**[Degree Name]**

in

**[Department/Stream]**

by

**[Student Name]**  
**[Roll Number]**

under the guidance of

**[Guide Name]**  
**[Designation]**

---

**[Department Name]**  
**[College Name]**  
**[University Name]**  
**[Year: 2025]**

\newpage

---

# CERTIFICATE

This is to certify that the project work entitled **"Study Sensei: A Local RAG-Based PDF Question-Answering System with Fine-Tuned LLM"** is a bonafide record of the project work done by **[Student Name], [Roll Number]** in partial fulfillment of the requirements for the award of the degree of **[Degree Name]** in **[Department/Stream]** of **[College Name]**, **[University Name]** during the academic year **[Year]**.

---

**[Guide Name]**  
[Designation]  
[Department Name]  
[College Name]

Date:  
Place:

---

**[Head of Department]**  
Professor and Head  
[Department Name]  
[College Name]

Date:  
Place:

\newpage

---

# ABSTRACT

Study Sensei presents a privacy-preserving local Retrieval-Augmented Generation system for intelligent PDF querying. The system features dual modes: Generic Chat with fine-tuned Gemma 3 4B model for aeronautics expertise using LoRA adaptation, and PDF Chat with multi-query RAG for context-aware responses. Implementing ChromaDB vector storage (768-dimensional embeddings) and Ollama's local LLMs ensures complete data sovereignty. The fine-tuned model achieves 91% domain accuracy (19% improvement over base models) with only 0.5% trainable parameters. Multi-query retrieval improves recall by 30-40% through diverse query perspectives. The system demonstrates enterprise-grade performance on consumer hardware while eliminating cloud dependencies and recurring costs.

**Keywords:** Retrieval-Augmented Generation, LoRA Fine-Tuning, Local LLM, Privacy-Preserving AI, Vector Database, Gemma 3, Multi-Query Retrieval

\newpage

---

# ACKNOWLEDGEMENT

I would like to express my sincere gratitude to all those who contributed to the successful completion of this project.

I am deeply thankful to my project guide **[Guide Name]** for their invaluable guidance, continuous support, and encouragement throughout the development of this system. Their expert advice and constructive feedback have been instrumental in shaping this project.

I extend my appreciation to **[Head of Department Name]**, Head of the Department of **[Department Name]**, for providing the necessary facilities and support for this project.

I am grateful to the developers of Ollama, LangChain, Streamlit, ChromaDB, and Unsloth for creating powerful open-source frameworks that made this project possible.

I also thank my peers and colleagues who provided feedback during testing and validation phases.

Finally, I acknowledge the support of my family and friends for their patience and encouragement during the development process.

---

**[Student Name]**  
**[Roll Number]**

\newpage

---

# TABLE OF CONTENTS

| **Chapter** | **Title** | **Page** |
|-------------|-----------|----------|
| | **Abstract** | i |
| | **Acknowledgement** | ii |
| | **Table of Contents** | iii |
| | **List of Tables** | v |
| | **List of Figures** | vi |
| | **List of Abbreviations** | vii |
| **1** | **INTRODUCTION** | **1** |
| 1.1 | Background and Motivation | 1 |
| 1.2 | Objectives | 3 |
| 1.2.1 | Primary Objectives | 3 |
| 1.2.2 | Secondary Objectives | 4 |
| 1.2.3 | Research Objectives | 4 |
| 1.3 | Methodology | 5 |
| 1.3.1 | Research Phase | 5 |
| 1.3.2 | Design Phase | 6 |
| 1.3.3 | Implementation Phase | 6 |
| 1.3.4 | Fine-Tuning Workflow | 8 |
| 1.3.5 | Testing Phase | 10 |
| 1.3.6 | Evaluation Metrics | 11 |
| **2** | **LITERATURE REVIEW** | **12** |
| 2.1 | Evolution of Question-Answering Systems | 12 |
| 2.2 | Retrieval-Augmented Generation (RAG) | 14 |
| 2.3 | Vector Databases and Embeddings | 16 |
| 2.4 | Local LLM Deployment | 17 |
| 2.5 | LLM Fine-Tuning Techniques | 18 |
| 2.5.1 | Transfer Learning and Adaptation | 18 |
| 2.5.2 | LoRA (Low-Rank Adaptation) | 19 |
| 2.5.3 | QLoRA (Quantized LoRA) | 20 |
| 2.5.4 | Unsloth Framework | 20 |
| 2.5.5 | Domain-Specific Fine-Tuning | 21 |
| 2.6 | LangChain Framework | 22 |
| 2.7 | Document Chunking Strategies | 23 |
| 2.8 | Multi-Query Retrieval | 24 |
| 2.9 | Prompt Engineering for RAG | 25 |
| 2.10 | Privacy-Preserving AI Systems | 26 |
| 2.11 | Existing RAG Solutions | 27 |
| 2.12 | Research Gaps and Contributions | 28 |
| **3** | **SYSTEM DESIGN AND ARCHITECTURE** | **29** |
| 3.1 | System Architecture | 29 |
| 3.1.1 | Core Components | 29 |
| 3.1.2 | Fine-Tuning Architecture | 30 |
| 3.1.3 | System Requirements | 32 |
| 3.2 | Core Modules | 33 |
| 3.2.1 | DocumentProcessor Module | 33 |
| 3.2.2 | VectorStore Module | 34 |
| 3.2.3 | RAGPipeline Module | 35 |
| 3.2.4 | GenericChatbot Module | 36 |
| 3.3 | Data Flow | 37 |
| **4** | **IMPLEMENTATION AND ANALYSIS** | **38** |
| 4.1 | Document Chunking Strategy | 38 |
| 4.2 | Embedding Specifications | 39 |
| 4.3 | Multi-Query Implementation | 40 |
| 4.4 | Prompt Engineering | 41 |
| 4.5 | Fine-Tuning Implementation | 42 |
| 4.5.1 | Dataset Preparation | 42 |
| 4.5.2 | LoRA Configuration | 43 |
| 4.5.3 | Training Process | 43 |
| 4.5.4 | Model Integration | 44 |
| **5** | **RESULTS AND DISCUSSION** | **45** |
| 5.1 | Performance Metrics | 45 |
| 5.2 | Retrieval Accuracy | 46 |
| 5.3 | Fine-Tuned Model Performance | 47 |
| 5.4 | Discussion | 49 |
| 5.4.1 | Strengths | 49 |
| 5.4.2 | Limitations | 50 |
| 5.4.3 | Future Enhancements | 50 |
| **6** | **CONCLUSION AND FUTURE WORK** | **51** |
| 6.1 | Summary | 51 |
| 6.2 | Key Achievements | 51 |
| 6.3 | Contributions | 52 |
| 6.4 | Future Directions | 53 |
| **7** | **REFERENCES** | **54** |
| **8** | **ANNEXURES** | **56** |

\newpage

---

# LIST OF TABLES

| **Table No.** | **Title** | **Page** |
|--------------|-----------|----------|
| Table 3.1 | System Requirements Specification | 32 |
| Table 4.1 | Document Chunking Configuration | 38 |
| Table 4.2 | Embedding Model Specifications | 39 |
| Table 5.1 | Query Performance Metrics | 45 |
| Table 5.2 | Retrieval Accuracy by Document Type | 46 |
| Table 5.3 | Model Comparison on Aeronautics Queries | 47 |
| Table 5.4 | Fine-Tuning Training Metrics | 48 |

\newpage

---

# LIST OF FIGURES

| **Figure No.** | **Title** | **Page** |
|---------------|-----------|----------|
| Figure 3.1 | System Architecture Diagram | 30 |
| Figure 3.2 | Fine-Tuning Pipeline | 31 |
| Figure 3.3 | RAG Data Flow | 37 |
| Figure 4.1 | Multi-Query Retrieval Process | 40 |
| Figure 5.1 | Performance Comparison Chart | 48 |

\newpage

---

# LIST OF ABBREVIATIONS

| **Abbreviation** | **Full Form** |
|-----------------|---------------|
| RAG | Retrieval-Augmented Generation |
| LLM | Large Language Model |
| LoRA | Low-Rank Adaptation |
| QLoRA | Quantized Low-Rank Adaptation |
| PEFT | Parameter-Efficient Fine-Tuning |
| NLP | Natural Language Processing |
| PDF | Portable Document Format |
| AI | Artificial Intelligence |
| API | Application Programming Interface |
| GPU | Graphics Processing Unit |
| CPU | Central Processing Unit |
| UI | User Interface |
| Q&A | Question and Answer |
| LCEL | LangChain Expression Language |
| GGUF | GPT-Generated Unified Format |
| VRAM | Video Random Access Memory |

\newpage

---

