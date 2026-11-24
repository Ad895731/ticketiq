# TicketIQ — Day-by-Day Workflow & Engineering Playbook

This document defines the 28-day execution plan (2–3 hours/day), Git branching conventions, metric logging protocol, and Definition-of-Done (DoD) checklists for every phase.

---

## 1. Day-by-Day Plan (28 Days)

### Week 1: Phase 1 — Standalone Classifier & Experimentation Notebook
*Goal: Build an explainable text classification pipeline predicting Category and Priority.*

- **Day 1: Environment Setup & EDA**
  - Initialize Git repo, create virtual environment (`venv`), install dependencies (`scikit-learn`, `pandas`, `numpy`, `matplotlib`, `seaborn`, `jupyter`).
  - Download dataset from Kaggle to `data/raw/`.
  - Open `notebooks/01_eda_and_cleaning.ipynb`: analyze class distributions, missing values, text length histograms.
- **Day 2: Data Preprocessing & Stratified Splitting**
  - Implement text cleaning functions (lowercase, regex strip URLs/HTML, whitespace normalization).
  - Create stratified 80/20 train/test split to preserve class ratios.
  - Carve out 100 historical resolved tickets into `data/processed/eval_100_heldout.csv` for Phase 2 retrieval testing.
  - Save `data/processed/train.csv` and `data/processed/test.csv`.
- **Day 3: Baseline Classifier (TF-IDF + Logistic Regression)**
  - Open `notebooks/02_baseline_tfidf_logistic_regression.ipynb`.
  - Fit `TfidfVectorizer(max_features=5000, ngram_range=(1,2))` on training text.
  - Train baseline `LogisticRegression(class_weight='balanced')` for **Category**.
  - Train baseline `LogisticRegression(class_weight='balanced')` for **Priority**.
  - Compute classification report (precision, recall, macro-F1) and plot confusion matrix.
- **Day 4: Dense Sentence Embeddings (`all-MiniLM-L6-v2`)**
  - Open `notebooks/03_embeddings_logistic_regression.ipynb`.
  - Install `sentence-transformers` and encode train/test text into 384-dimensional dense vectors.
  - Train `LogisticRegression` on embeddings for Category and Priority.
  - Log macro-F1 and compare head-to-head against TF-IDF baseline.
- **Day 5: Error Analysis & Hyperparameter Tuning**
  - Inspect confusion matrices: where does the classifier fail? (e.g. "Access" vs "Software", "Medium" vs "High").
  - Tune regularization parameter \(C \in [0.1, 1.0, 10.0]\) using stratified validation.
  - Validate that inference latency on a single text string is \(< 25\text{ ms}\).
- **Day 6: Serialization & Phase 1 Sign-Off**
  - Export trained models to `data/models/`:
    - `embedding_category_lr.joblib`
    - `embedding_priority_lr.joblib`
    - `label_encoders.joblib`
  - Write a standalone test script `scripts/verify_models.py` verifying that models load and predict correctly.
  - Complete Phase 1 Definition-of-Done checklist.

---

### Week 2: Phase 2 — Vector Retrieval & pgvector Setup
*Goal: Index ticket embeddings in Supabase PostgreSQL and evaluate duplicate/similar retrieval.*

- **Day 7: Supabase PostgreSQL & pgvector Setup**
  - Create free-tier Supabase project.
  - Enable `vector` extension in PostgreSQL.
  - Create `users` and `tickets` tables via SQL editor.
  - Create HNSW index on `tickets(embedding)` using `vector_cosine_ops`.
- **Day 8: Batch Ingestion Script**
  - Write `scripts/ingest_historical_tickets.py` using `SQLAlchemy` and `pgvector.sqlalchemy`.
  - Encode \(\ge 1,000\) historical tickets from `train.csv` and insert them into Supabase.
  - Verify row count, column constraints, and vector dimensions (384).
- **Day 9: SQL Similarity Search Testing**
  - Open `notebooks/04_pgvector_retrieval_and_eval.ipynb`.
  - Implement raw SQL and SQLAlchemy queries computing cosine similarity:
    \[
    \text{similarity} = 1 - (\text{embedding} \Leftrightarrow \text{query\_vector})
    \]
  - Test queries with varying filters (`status = 'Resolved'`) and similarity thresholds (\(\ge 0.65\)).
- **Day 10: Benchmark Suite Setup**
  - Load the 100 held-out evaluation tickets (`eval_100_heldout.csv`).
  - Formulate automated queries using the ticket description as search input.
- **Day 11: Retrieval Evaluation (Hit@3 Calculation)**
  - Execute top-3 retrieval for all 100 evaluation tickets.
  - Calculate **Hit@3**: query is a "hit" if at least one of the top-3 results shares the ground-truth category and addresses a related issue.
  - Record average vector query latency across the 100 queries.
- **Day 12: Index Tuning & Phase 2 Sign-Off**
  - Verify HNSW query performance with `EXPLAIN ANALYZE`.
  - Ensure query execution time remains \(< 100\text{ ms}\).
  - Complete Phase 2 Definition-of-Done checklist.

---

### Week 3: Phase 3 — RAG Resolution Chain & Core FastAPI Service (MVP)
*Goal: Assemble LangChain RAG pipeline and complete the production-ready FastAPI service.*

- **Day 13: LangChain Gemini Integration**
  - Obtain Google AI Studio API key for Gemini 1.5 Flash.
  - Install `langchain` and `langchain-google-genai`.
  - Define Pydantic output schema `ResolutionResponse(suggested_fix, sources, confidence_note)`.
  - Test LLM generation using `with_structured_output(ResolutionResponse)`.
- **Day 14: RAG Chain Assembly**
  - Build `app/services/ml/rag_chain.py`:
    - Retrieve top-3 historical resolved tickets from Supabase.
    - Format prompt: strictly instruct LLM to synthesize only from retrieved resolutions.
    - If top similarity \(< 0.65\), return fallback response without calling Gemini.
  - Verify zero hallucination on out-of-domain queries.
- **Day 15: FastAPI Foundation & Auth Engine**
  - Scaffold `backend/app/` structure (`core`, `db`, `models`, `schemas`, `api`).
  - Configure SQLAlchemy async/sync session and Alembic migrations.
  - Implement JWT authentication with password hashing (`passlib`/`bcrypt`) and role-based dependency (`get_current_active_user`, `require_role`).
- **Day 16: Ticket Management CRUD Endpoints**
  - Implement `POST /api/v1/tickets`: auto-predicts Category & Priority via Phase 1 models, generates embedding, stores ticket.
  - Implement `GET /api/v1/tickets`, `GET /api/v1/tickets/{id}`, `PATCH /api/v1/tickets/{id}`.
- **Day 17: ML Endpoints Implementation**
  - Implement `POST /api/v1/ml/predict`: standalone category/priority prediction with class probabilities.
  - Implement `POST /api/v1/ml/similar`: top-K semantic search.
  - Implement `POST /api/v1/ml/suggest`: full RAG resolution chain.
- **Day 18: Automated Pytest Suite & MVP Sign-Off**
  - Write test suite in `backend/tests/`:
    - `test_auth.py`: login, token validation, RBAC restrictions.
    - `test_tickets.py`: CRUD operations and auto-triage insertion.
    - `test_classifier.py`: prediction outputs and schema validation.
    - `test_rag_chain.py`: RAG logic with mocked Gemini client.
  - Verify 100% test pass rate with `pytest -v`.
  - **Complete Phase 3 Definition-of-Done (End-of-MVP).**

---

### Week 4: Phase 4 & Phase 5 — Flutter Dashboard & Cloud Deployment

- **Day 19: Flutter Web Setup & Auth Flow**
  - Initialize Flutter project: `flutter create --platforms=web ticketiq_dashboard`.
  - Implement API client using `http` package with JWT storage.
  - Build Login & Registration screen.
- **Day 20: Ticket Queue Dashboard**
  - Build main queue UI: list view displaying ticket cards.
  - Add filter chips for Category, Priority, and Status.
  - Display color-coded badges for priority (*Critical: red, High: orange, Medium: blue, Low: grey*).
- **Day 21: Ticket Detail & Triage Inspector**
  - Build detailed view showing requester info, description, and status.
  - Show "AI Predicted Triage" badge with confidence score.
  - Add "Similar Tickets" collapsible drawer showing top-3 matches.
- **Day 22: AI Resolution Assistant Widget**
  - Build "AI Resolution Assistant" card on the ticket detail screen.
  - Add "Generate Fix" button calling `POST /api/v1/ml/suggest`.
  - Render structured Markdown resolution steps and cited source ticket IDs.
  - Add "Apply to Resolution Notes" button that copies the fix and updates status to "Resolved".
- **Day 23: Frontend Polish & Phase 4 Sign-Off**
  - Handle loading spinners, error banners, and network timeouts.
  - Test production web build: `flutter build web --release`.
  - Complete Phase 4 Definition-of-Done checklist.
- **Day 24: Docker Containerization**
  - Write multi-stage `Dockerfile` for FastAPI backend.
  - Pre-download `all-MiniLM-L6-v2` during container build to ensure instant container startup.
  - Verify local container execution with `docker run`.
- **Day 25: Render & Supabase Cloud Configuration**
  - Connect GitHub repository to Render.
  - Create Render Web Service for FastAPI.
  - Configure Supabase Connection Pooler (Transaction Mode, port 6543) in `DATABASE_URL`.
  - Set production environment variables on Render.
- **Day 26: Frontend Hosting & CORS Integration**
  - Deploy Flutter Web build (Render Static Site, Vercel, or GitHub Pages).
  - Configure CORS origins in FastAPI to allow frontend domain.
  - Verify live API communication between frontend and backend.
- **Day 27: Production Latency & Smoke Testing**
  - Execute end-to-end user workflow on the live production URL.
  - Measure live endpoint latencies:
    - `/predict`: \(< 50\text{ ms}\)
    - `/similar`: \(< 120\text{ ms}\)
    - `/suggest`: \(< 2.5\text{ s}\)
- **Day 28: Final Polish, Documentation & Project Wrap-Up**
  - Record 2-minute demo video/GIF for project showcase.
  - Polish README with architecture diagram, API documentation, and live links.
  - Complete Phase 5 Definition-of-Done checklist.

---

## 2. Git Branching Strategy

To maintain a clean, professional commit history for placement portfolios:

### Branch Structure
- `main`: Production-ready code only. Deploys directly to Render.
- `dev`: Integration branch where all completed features merge.
- `feature/*`: Short-lived branches dedicated to individual phase components.

### Feature Branch Roadmap
```text
main
 └── dev
      ├── feature/phase1-triage-classifier
      ├── feature/phase2-pgvector-retrieval
      ├── feature/phase3-rag-fastapi-backend
      ├── feature/phase4-flutter-web-dashboard
      └── feature/phase5-deployment-hardening
```

### Commit Message Conventions
Use the **Conventional Commits** standard:
- `feat(ml)`: New machine learning feature or model training script
- `feat(api)`: New FastAPI endpoint or service logic
- `feat(ui)`: New Flutter screen or component
- `fix(retrieval)`: Bugfix in vector query or database logic
- `test(api)`: Adding or updating Pytest test cases
- `docs`: Documentation updates or architecture notes
- `chore`: Dependency updates, Docker configuration, or CI changes

*Example*: `feat(ml): train sentence-embeddings logistic regression for category classification`

---

## 3. Experiment & Metric Logging Protocol

Every ML and retrieval experiment must be recorded in `data/experiments_log.csv` and summarized in `docs/experiments_summary.md`.

### Experiment Log Schema (`data/experiments_log.csv`)
| Column Name | Type | Description |
| :--- | :--- | :--- |
| `exp_id` | String | e.g. `EXP-01-TFIDF`, `EXP-02-MINILM` |
| `date` | Date | YYYY-MM-DD |
| `target` | String | `category` or `priority` |
| `representation` | String | `TF-IDF (5000 feats)` or `all-MiniLM-L6-v2 (384-dim)` |
| `model` | String | `LogisticRegression` |
| `hyperparameters` | String | e.g. `C=1.0, class_weight=balanced, solver=lbfgs` |
| `macro_f1` | Float | Unweighted mean of per-class F1 scores |
| `precision` | Float | Macro-averaged precision |
| `recall` | Float | Macro-averaged recall |
| `inference_ms` | Float | Average latency per sample in milliseconds |
| `notes` | String | Key qualitative observations |

---

## 4. Definition-of-Done (DoD) Checklists

### Phase 1 DoD Checklist
- [ ] Raw dataset cleaned and split into 80/20 train/test split.
- [ ] 100-ticket held-out evaluation set saved to `eval_100_heldout.csv`.
- [ ] TF-IDF baseline and dense embedding models trained and logged in `experiments_log.csv`.
- [ ] Category classifier achieves \(\ge 0.75\) Macro-F1.
- [ ] Priority classifier achieves \(\ge 0.65\) Macro-F1.
- [ ] Model artifacts exported to `data/models/` and verified with a standalone Python loading script.

### Phase 2 DoD Checklist
- [ ] Supabase PostgreSQL instance has `vector` extension and HNSW index active.
- [ ] Batch ingestion script successfully indexes \(\ge 1,000\) historical tickets.
- [ ] Cosine similarity retrieval query runs in \(< 100\text{ ms}\).
- [ ] Hit@3 evaluation on the 100-ticket held-out set achieves \(\ge 80\%\).

### Phase 3 DoD Checklist (End of MVP)
- [ ] LangChain RAG pipeline integrates with Gemini 1.5 Flash using structured Pydantic output.
- [ ] Out-of-distribution queries with similarity \(< 0.65\) trigger fallback without calling LLM.
- [ ] FastAPI backend implements JWT auth, RBAC (`user`, `agent`, `admin`), CRUD, and `/ml` endpoints.
- [ ] All Pytest unit and integration tests pass with 100% success rate.
- [ ] Swagger documentation at `/docs` tested and verified manually.

### Phase 4 DoD Checklist
- [ ] Flutter Web app runs locally and connects to FastAPI backend.
- [ ] Support agent can log in and view ticket queue with category/priority/status filters.
- [ ] Ticket detail screen displays auto-triage badges, similar tickets, and AI resolution generator.
- [ ] Agent can apply the AI suggestion to resolution notes with a single click.

### Phase 5 DoD Checklist
- [ ] Multi-stage Dockerfile builds and runs locally without runtime model downloads.
- [ ] Backend deployed on Render Web Service, database hosted on Supabase with connection pooling.
- [ ] Flutter Web dashboard deployed and communicating with backend with zero CORS errors.
- [ ] Live response latencies verified: `/predict` \(< 50\text{ ms}\), `/similar` \(< 120\text{ ms}\), `/suggest` \(< 2.5\text{ s}\).
- [ ] Final README complete with architecture diagrams, setup instructions, and demo GIF.
