# TicketIQ — 5-Phase Implementation Plan

This roadmap organizes the development of TicketIQ into **5 distinct phases** designed for a 4-week timeline (2–3 hours/day).

> **Core MVP Milestone**: **Phases 1 through 3 form a complete, end-to-end functioning MVP.** You will have a trained explainable classifier, a functional vector search system in PostgreSQL, and an authenticated FastAPI backend serving RAG resolutions before building the frontend or deploying to the cloud.

---

## Phase Summary Table

| Phase | Title | Focus Area | Estimated Duration | Milestone Deliverable |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1** | **Standalone Classifier & Experiments** | ML Modeling & Evaluation | Days 1 – 6 (6 days) | Standalone Jupyter Notebooks + Model `.joblib` artifacts |
| **Phase 2** | **Vector Retrieval & pgvector Setup** | DB Vectors & Similarity Search | Days 7 – 12 (6 days) | Supabase pgvector schema + Hit@3 evaluation benchmark |
| **Phase 3** | **RAG Chain & FastAPI Backend (MVP)** | LangChain & API Engineering | Days 13 – 18 (6 days) | Fully functional, authenticated REST API with Pytest suite |
| **Phase 4** | **Flutter Web Agent Dashboard** | Frontend & User Experience | Days 19 – 23 (5 days) | Interactive web UI for IT support agents |
| **Phase 5** | **Testing, Hardening & Cloud Deploy** | Containerization & Cloud Launch | Days 24 – 28 (5 days) | Live Render + Supabase deployment with verified latency |

---

## Detailed Phase Breakdown

---

### Phase 1: Standalone ML Classifier & Experimentation Notebook
*Estimated Timeline: Days 1 – 6*

#### Goal
Build, rigorously evaluate, and compare an explainable text classification pipeline predicting ticket **Category** (multiclass) and **Priority** (multiclass/ordinal) from textual descriptions using Scikit-Learn.

#### Tasks
1. **Data Acquisition & EDA**:
   - Download the IT/Customer Support Ticket dataset from Kaggle into `data/raw/`.
   - Perform exploratory data analysis: inspect distributions of ticket lengths, class frequencies for Category (*Hardware, Software, Network, Access*) and Priority (*Low, Medium, High, Critical*).
   - Clean text: lowercase conversion, whitespace normalization, removal of HTML tags/system artifacts.
2. **Train/Test Splitting**:
   - Create a clean 80/20 train/test split using `StratifiedShuffleSplit` to preserve class distributions across both Category and Priority.
   - Set aside a 100-ticket held-out set specifically for future retrieval benchmarking in Phase 2.
3. **Baseline Model (TF-IDF + Logistic Regression)**:
   - Fit `TfidfVectorizer` (max_features=5000, n-gram range=(1, 2), stop_words='english') on training text.
   - Train `LogisticRegression(max_iter=1000, class_weight='balanced')` for Category and Priority.
   - Evaluate with `classification_report` (precision, recall, macro-F1) and confusion matrices.
4. **Embedding-Based Model (`all-MiniLM-L6-v2` + Logistic Regression)**:
   - Generate 384-dimensional dense sentence embeddings using `sentence-transformers`.
   - Train `LogisticRegression` on the dense embeddings.
   - Compare performance against the TF-IDF baseline using Macro-F1.
5. **Model Serialization**:
   - Save the fitted vectorizer/embedder config and trained Logistic Regression estimators using `joblib` into `data/models/`.

#### Deliverables
- `notebooks/01_eda_and_cleaning.ipynb`
- `notebooks/02_baseline_tfidf_logistic_regression.ipynb`
- `notebooks/03_embeddings_logistic_regression.ipynb`
- Serialized artifacts: `data/models/embedding_category_lr.joblib`, `data/models/embedding_priority_lr.joblib`, `data/models/label_encoders.joblib`.
- Experiment log table comparing TF-IDF vs Dense Embeddings.

#### Acceptance Criteria
- [ ] Category classifier achieves \(\ge 0.75\) Macro-F1 on the test set.
- [ ] Priority classifier achieves \(\ge 0.65\) Macro-F1 on the test set.
- [ ] Embedding-based classifier matches or outperforms the TF-IDF baseline.
- [ ] Confusion matrices generated and analyzed for systematic confusion (e.g. Medium vs High priority).
- [ ] Serialized `.joblib` models can be loaded into a clean Python session and produce predictions on raw strings in \(< 25\text{ ms}\).

---

### Phase 2: Vector Search & Grounded Retrieval with pgvector
*Estimated Timeline: Days 7 – 12*

#### Goal
Set up Supabase PostgreSQL with the `pgvector` extension, batch-index ticket embeddings, and build an explainable similarity search pipeline evaluated on a held-out benchmark.

#### Tasks
1. **Database Vector Initialization**:
   - Enable `vector` extension in Supabase PostgreSQL instance.
   - Define table schema for `tickets` with column `embedding vector(384)`.
   - Create an HNSW index using cosine distance: `USING hnsw (embedding vector_cosine_ops)`.
2. **Batch Ingestion Script**:
   - Write a standalone Python script `scripts/ingest_historical_tickets.py` to embed historical resolved tickets and bulk-insert them into Supabase via SQLAlchemy.
3. **Similarity Search Implementation**:
   - Write SQL queries computing Cosine Similarity from Cosine Distance:
     \[
     \text{Cosine Similarity} = 1 - (\mathbf{u} \cdot \mathbf{v}) = 1 - (\text{embedding} \Leftrightarrow \text{query\_vector})
     \]
   - Implement filtering by `status = 'Resolved'` and similarity thresholding (\(\ge 0.65\)).
4. **Retrieval Evaluation (Hit@3 Benchmark)**:
   - Run retrieval against the 100 held-out evaluation tickets.
   - For each evaluation ticket, retrieve top-3 similar tickets.
   - Compute **Hit@3**: percentage of queries where at least one of the top-3 retrieved tickets addresses the same root cause category.

#### Deliverables
- `notebooks/04_pgvector_retrieval_and_eval.ipynb`
- `scripts/ingest_historical_tickets.py`
- Supabase SQL schema migration script.
- Retrieval evaluation report documenting Hit@3 and average query latency.

#### Acceptance Criteria
- [ ] Supabase table populated with \(\ge 1,000\) embedded historical tickets.
- [ ] HNSW vector index active and functional.
- [ ] Retrieval query latency \(< 100\text{ ms}\) for top-3 nearest neighbors.
- [ ] Hit@3 metric on the 100-ticket held-out set achieves \(\ge 80\%\).

---

### Phase 3: RAG Resolution Chain & Core FastAPI Service (MVP Completion)
*Estimated Timeline: Days 13 – 18*

#### Goal
Build the LangChain-orchestrated RAG resolution pipeline with Google Gemini 1.5 Flash and wrap the entire system in a production-ready FastAPI application with JWT RBAC.

#### Tasks
1. **LangChain Grounded Resolution Chain**:
   - Create a clean wrapper for Google Gemini 1.5 Flash using `langchain-google-genai`.
   - Write a strict prompt template enforcing **grounded generation**: the model must ONLY generate recommendations derived from the retrieved historical resolutions.
   - Enforce Pydantic structured output (`with_structured_output`) returning:
     - `suggested_fix`: Step-by-step guidance.
     - `sources`: Array of ticket IDs used as evidence.
     - `confidence_note`: Brief justification.
2. **FastAPI Application Architecture**:
   - Implement application layout (`app/api`, `app/models`, `app/schemas`, `app/services`).
   - Implement JWT authentication with role-based access control (`user`, `agent`, `admin`).
3. **Endpoint Development**:
   - `POST /api/v1/auth/login`, `POST /api/v1/auth/register`
   - `POST /api/v1/tickets` (Auto-triages category and priority upon creation).
   - `GET /api/v1/tickets`, `GET /api/v1/tickets/{id}`, `PATCH /api/v1/tickets/{id}`
   - `POST /api/v1/ml/predict` (Standalone prediction without saving).
   - `POST /api/v1/ml/similar` (Top-K duplicate/similar search).
   - `POST /api/v1/ml/suggest` (Top-3 retrieval + Gemini structured RAG resolution).
4. **Automated Testing Suite**:
   - Write unit and integration tests using `pytest` and `httpx.AsyncClient`.
   - Mock external Gemini API calls in test suite to ensure deterministic, zero-cost CI testing.

#### Deliverables
- Complete backend codebase in `backend/app/`.
- Alembic database migration scripts.
- Pytest test suite in `backend/tests/` covering Auth, CRUD, ML inference, and RAG chains.
- Interactive Swagger documentation accessible at `/docs`.

#### Acceptance Criteria
- [ ] **Full MVP Works End-to-End**: A user can create a ticket via API, the system auto-assigns category/priority, and an agent can call `/suggest` to receive a validated JSON resolution grounded in top-3 historical tickets.
- [ ] All Pytest unit and integration tests pass with 100% green status.
- [ ] RAG endpoint returns HTTP 422 or fallback response if no historical tickets exceed the 0.65 similarity threshold (no ungrounded hallucination).
- [ ] RBAC enforcement verified: Standard `user` cannot access agent-only resolution endpoints.

---

### Phase 4: Flutter Web Agent Dashboard
*Estimated Timeline: Days 19 – 23*

#### Goal
Build a clean, responsive Flutter Web dashboard for IT support agents to triage incoming tickets, inspect similarity search results, and accept AI-generated resolution suggestions.

#### Tasks
1. **Flutter Web Project Setup**:
   - Initialize Flutter Web project in `frontend/ticketiq_dashboard/`.
   - Configure HTTP client service with secure JWT token storage (via `shared_preferences` or browser storage).
2. **Authentication & Queue Management**:
   - Build Login & Registration screen.
   - Build Support Queue Dashboard: tabular or card view of open tickets with filter chips (Status, Priority, Category).
3. **Ticket Detail & Triage View**:
   - Display ticket title, description, requester, and timestamps.
   - Show "AI Predicted Triage" badge with confidence level. Allow agent to override if needed.
4. **Interactive AI Assistance Panel**:
   - "Similar Tickets" tab displaying top-3 historical matches with similarity percentage and resolution notes.
   - "Generate Resolution" button that triggers `POST /suggest` and displays the structured fix with citations.
   - "Insert into Resolution Notes" button that copies the AI fix into the ticket's resolution field and marks status as "Resolved".

#### Deliverables
- Complete Flutter Web application in `frontend/ticketiq_dashboard/`.
- Production web bundle build (`flutter build web --release`).

#### Acceptance Criteria
- [ ] Agent can log in, view live tickets from FastAPI backend, and filter by priority/status.
- [ ] Ticket detail screen displays auto-triage category and priority badges.
- [ ] Clicking "Generate Resolution" triggers RAG chain and renders structured steps with source ticket links within \(< 3\text{ seconds}\).
- [ ] One-click action allows agent to approve/edit the AI fix and update ticket to "Resolved".

---

### Phase 5: Testing, Hardening & Cloud Deployment
*Estimated Timeline: Days 24 – 28*

#### Goal
Containerize the FastAPI backend, configure connection pooling on Supabase, deploy backend and frontend to Render, and verify live performance and stability.

#### Tasks
1. **Containerization & Optimization**:
   - Write a multi-stage `Dockerfile` for FastAPI that downloads `all-MiniLM-L6-v2` during Docker build to eliminate runtime download delays.
   - Configure production server using `uvicorn` with multiple workers.
2. **Supabase Production Configuration**:
   - Configure Supabase Connection Pooler (Transaction Mode / PgBouncer on port 6543) to prevent connection exhaustion on free tiers.
3. **Render Deployment**:
   - Deploy FastAPI backend as a Render Web Service.
   - Configure environment variables (`DATABASE_URL`, `GEMINI_API_KEY`, `JWT_SECRET_KEY`).
   - Host Flutter Web build (via Render Static Site, Vercel, or GitHub Pages).
4. **End-to-End Verification & Documentation**:
   - Run smoke tests against live public URL.
   - Measure live response latencies:
     - `/predict`: \(< 50\text{ ms}\)
     - `/similar`: \(< 120\text{ ms}\)
     - `/suggest`: \(< 2.5\text{ s}\) (including Gemini generation)
   - Finalize project README with architectural diagrams, API docs, and demo video/GIF.

#### Deliverables
- Production `Dockerfile` and `docker-compose.yml`.
- Live, publicly accessible backend on Render and database on Supabase.
- Live hosted Flutter Web dashboard.
- Verification test run report documenting latencies and uptime.

#### Acceptance Criteria
- [ ] Public HTTPS API responds successfully to health check `GET /health`.
- [ ] Live Flutter Web UI communicates seamlessly with Render backend with zero CORS issues.
- [ ] Database queries utilize HNSW index without exceeding Supabase free-tier RAM limits.
- [ ] End-to-end user story works on production: Create Ticket \(\to\) Auto-Triage \(\to\) Similar Search \(\to\) AI Suggest \(\to\) Resolve Ticket.
