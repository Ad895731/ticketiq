# TicketIQ — AI-Powered IT Helpdesk Triage & Grounded Resolution Engine

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://supabase.com/)
[![LangChain](https://img.shields.io/badge/LangChain-Orchestrator-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![Gemini](https://img.shields.io/badge/Gemini_1.5_Flash-Google_AI-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**TicketIQ** is a production-grade, AI-powered IT helpdesk system that unifies **explainable machine learning classification**, **sub-100ms vector similarity search**, and **grounded Retrieval-Augmented Generation (RAG)** to slash Mean Time To Resolve (MTTR) for enterprise support desks.

---

## 📌 Problem Statement

Enterprise IT support teams face three major operational bottlenecks:
1. **Manual Triage Latency & Inconsistency**: Incoming tickets sit in queues unassigned for hours; priority and category assignments vary widely across different support agents.
2. **Knowledge Silos & Reinventing the Wheel**: Up to 40% of incoming IT issues are duplicates or near-duplicates of previously resolved incidents, yet agents spend hours re-diagnosing known bugs.
3. **LLM Hallucinations in Automated Support**: Generic generative chatbots make up troubleshooting commands or cite non-existent internal knowledge bases when asked to solve complex IT faults.

---

## 🚀 Core Features

- **⚡ Sub-25ms Explainable Auto-Triage**: Dual Scikit-Learn multiclass classifiers trained on dense sentence embeddings (`all-MiniLM-L6-v2`) predict ticket **Category** (*Hardware, Software, Network, Access*) and **Priority** (*Low, Medium, High, Critical*) with calibrated probability distributions.
- **🔍 Sub-100ms Vector Similarity Retrieval**: Supabase PostgreSQL with the `pgvector` extension and HNSW indexing calculates cosine similarity against historical resolved tickets, providing support agents with instant relevant past fixes (Hit@3 benchmark $\ge 80\%$).
- **🛡️ Grounded RAG Incident Resolution**: LangChain RAG pipeline powered by **Google Gemini 1.5 Flash** generates deterministic, structured resolution steps constrained strictly to retrieved context—preventing hallucinations.
- **📊 Living Interview & Architecture Documentation**: Built with end-to-end mathematical rigor and system design documentation for every trade-off (TF-IDF vs Embeddings, HNSW vs IVFFlat, Cosine vs Euclidean metrics).

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Client Tier
        UI["Flutter Web Agent Dashboard"]
        Swagger["Swagger UI / Automated Pytest Suite"]
    end

    subgraph Application Tier [FastAPI Backend]
        Auth["OAuth2 & JWT Auth / RBAC"]
        Router["FastAPI Router (/api/v1/tickets)"]
        
        subgraph ML & RAG Services
            TriageSvc["Triage Classifier Service\n(all-MiniLM-L6-v2 + Logistic Regression)"]
            EmbedSvc["Embedding Service\n(sentence-transformers: 384-dim)"]
            RAGSvc["Grounded RAG Engine\n(LangChain + Gemini 1.5 Flash)"]
        end
    end

    subgraph Data Tier [Supabase PostgreSQL + pgvector]
        UsersTbl[("users table\n(RBAC & Auth)")]
        TicketsTbl[("tickets table\n(B-Tree + HNSW Vector Index)")]
    end

    subgraph External Hosted API
        Gemini["Google Gemini 1.5 Flash API\n(Google AI Studio)"]
    end

    UI -->|HTTPS / JWT Bearer| Router
    Swagger -->|HTTPS / JWT Bearer| Router
    Router --> Auth
    Router --> TriageSvc
    Router --> EmbedSvc
    Router --> RAGSvc
    
    TriageSvc -->|Loads serialized .joblib| EmbedSvc
    EmbedSvc -->|Generates 384-dim vector| TicketsTbl
    RAGSvc -->|Top-3 vector similarity query <=>| TicketsTbl
    RAGSvc -->|Formatted prompt with context| Gemini
    Gemini -->|Structured JSON fix| RAGSvc

    Router -->|SQLAlchemy ORM| UsersTbl
    Router -->|SQLAlchemy ORM| TicketsTbl
```

---

## 🛠️ Production Tech Stack

| Component | Technology | Rationale & Architectural Defense |
| :--- | :--- | :--- |
| **Backend Framework** | **FastAPI (Python 3.11)** | High-throughput async ASGI framework, native Pydantic validation, automatic OpenAPI generation. |
| **ML Triage Classifier** | **Scikit-Learn + Sentence-Transformers** | Lightweight inference ($<25\text{ ms}$, $<300\text{ MB}$ RAM), explainable calibrated probabilities, zero cold-start delay compared to giant LLM fine-tunes. |
| **Embeddings** | **`all-MiniLM-L6-v2`** | 384-dimensional dense vectors balancing semantic resolution, fast CPU encoding, and low vector storage overhead. |
| **Database & Vector Store** | **PostgreSQL + `pgvector` (Supabase)** | Eliminates dual-database drift by co-locating relational ticket metadata and vector embeddings in a single ACID-compliant PostgreSQL database with HNSW indexing. |
| **RAG Orchestrator** | **LangChain** | Manages prompt templates, structured Pydantic output parsers, and retrieval chains. |
| **LLM Provider** | **Google Gemini 1.5 Flash** | Sub-second inference latency, generous free tier via Google AI Studio, highly capable structured JSON generation. |
| **Frontend Dashboard** | **Flutter Web** | Cross-platform, reactive support agent queue and one-click resolution UI. |

---

## 🗺️ 5-Phase Implementation Roadmap

- [ ] **Phase 1: Standalone Classifier & ML Experimentation**
  - [ ] Exploratory Data Analysis (EDA) on IT support dataset (`ml/notebooks/01_eda_and_baseline.ipynb`)
  - [ ] Stratified 80/20 Train/Test split preserving Category and Priority distributions
  - [ ] Baseline model: TF-IDF + Logistic Regression
  - [ ] Embedding model: `all-MiniLM-L6-v2` + Logistic Regression
  - [ ] Metric validation: Category Macro-F1 $\ge 0.75$, Priority Macro-F1 $\ge 0.65$
  - [ ] Model serialization (`.joblib` artifacts)
- [ ] **Phase 2: Vector Search & pgvector Setup**
  - [ ] Supabase PostgreSQL database initialization with `pgvector` extension
  - [ ] Define relational + vector schema with HNSW index (`vector_cosine_ops`)
  - [ ] Historical resolved tickets batch ingestion pipeline
  - [ ] Retrieval evaluation: Hit@3 benchmark $\ge 80\%$ on 100 held-out tickets
- [ ] **Phase 3: Grounded RAG Chain & Authenticated FastAPI Backend (Core MVP)**
  - [ ] FastAPI application factory with OAuth2 JWT authentication and RBAC (`user`, `agent`, `admin`)
  - [ ] Ticket ingestion and auto-triage inference endpoints (`POST /api/v1/tickets`)
  - [ ] Grounded RAG resolution endpoint with Pydantic structured output (`POST /api/v1/tickets/{id}/resolve`)
  - [ ] Automated Pytest suite with $\ge 85\%$ test coverage
- [ ] **Phase 4: Flutter Web Agent Dashboard**
  - [ ] Real-time support agent queue with priority sorting and badge indicators
  - [ ] Interactive similar tickets pane displaying past resolution notes and similarity score
  - [ ] 1-Click RAG suggested resolution insertion
- [ ] **Phase 5: Production Hardening, Containerization & Cloud Deploy**
  - [ ] Docker multi-stage build optimization
  - [ ] Cloud deployment to Render / Railway with Supabase Managed PostgreSQL
  - [ ] End-to-end latency and throughput benchmarking

---

## 📁 Repository Structure

```text
TicketIQ/
├── .cursor/rules/             # Developer & interview documentation rules
├── docs/                      # Architectural specs, risk mitigations, interview journal
│   ├── architecture.md        # Complete system architecture specification
│   ├── phases.md              # 5-phase breakdown & deliverables
│   ├── interview_knowledge_journal.md # Living Q&A journal for technical interviews
│   └── index.html             # Interactive offline Web Reader
├── ml/                        # Machine Learning experimentation & data pipelines
│   ├── data/                  # Dataset dictionary, schema & raw data guidance
│   │   ├── README.md          # Dataset description & cleaning rules
│   │   └── raw/               # Gitignored raw CSV data files
│   └── notebooks/             # Jupyter notebooks for reproducible experiments
│       └── 01_eda_and_baseline.ipynb
├── scripts/                   # Utility scripts and doc compilers
│   └── build_docs_and_pdfs.py # Automated PDF & HTML documentation generator
├── .gitignore                 # Enterprise Python/ML/OS ignore rules
└── README.md                  # Project overview and roadmap
```

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Ad895731/ticketiq.git
cd ticketiq
```

### 2. Set Up Python Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

### 3. Review Documentation & Architectural Blueprints
Open the interactive documentation reader locally in your browser:
```bash
open docs/index.html
```

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
