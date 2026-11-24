# TicketIQ — Syllabus & Learning Map

This learning map outlines exactly which concepts from your syllabus apply to each phase of the project.

- **Category A (Already known)**: Topics from your ML notes to revise and defend mathematically.
- **Category B (CampusX LangChain)**: Topics from your Generative AI coursework to learn and apply.
- **Small Extras**: Minimal, industry-standard tools outside A and B, each with a 1–2 line explanation and one short resource.

> **Zero Outside Scope Rule**: No deep learning architectures (CNN/RNN/LSTM), no transformer training or fine-tuning, no LangGraph, no agents, no tool calling, and no Ollama.

---

## Phase-by-Phase Syllabus Mapping

### Phase 1: Standalone Classifier & Experimentation Notebook

#### Concepts from Syllabus A to Revise
- **Types of Data**:
  - *Nominal categorical*: Ticket `Category` (*Hardware, Software, Network, Access*) — no natural ordering.
  - *Ordinal categorical*: Ticket `Priority` (*Low < Medium < High < Critical*) — ordered priority levels.
- **Supervised Learning & Logistic Regression**:
  - Multiclass classification using One-vs-Rest (OvR) and Multinomial Softmax loss.
  - Decision boundaries in high-dimensional feature spaces.
- **Cost Function & Gradient Descent**:
  - Log-loss / Cross-entropy cost function.
  - Optimization via gradient descent; convergence and learning rate dynamics.
- **Overfitting & Underfitting**:
  - L2 Regularization penalty (\(C = \frac{1}{\lambda}\)) to control model variance and prevent overfitting on sparse text features.
- **Evaluation Metrics**:
  - Train/test split (80/20 stratified split to preserve class ratios).
  - Accuracy vs Precision vs Recall vs F1-Score.
  - **Macro-F1 Score**: Unweighted arithmetic mean of F1 scores across classes (critical for diagnosing performance on minority classes).
  - **Confusion Matrix**: Identifying off-diagonal errors (e.g., mistaking *Critical* for *Medium*).

#### Concepts from Syllabus B to Learn
- *None required for Phase 1* (Pure classical ML phase).

#### Small Extras Needed in Phase 1
1. **TF-IDF (Term Frequency – Inverse Document Frequency)**:
   - *Explanation*: A statistical representation that converts text strings into numerical vectors by weighing how frequently a term appears in a document against how common it is across the entire corpus.
   - *Resource*: [Scikit-learn User Guide: TF-IDF Term Weighting](https://scikit-learn.org/stable/modules/feature_extraction.html#tfidf-term-weighting) (5-minute read).
2. **Pretrained Sentence Embeddings (`sentence-transformers: all-MiniLM-L6-v2`)**:
   - *Explanation*: An off-the-shelf, frozen embedding model used strictly as a deterministic feature extractor to map raw text into a 384-dimensional dense vector space without training any neural network.
   - *Resource*: [SBERT.net: Pretrained Models & Quickstart](https://www.sbert.net/docs/quickstart.html).
3. **Model Serialization (`joblib`)**:
   - *Explanation*: A standard Python library optimized for dumping and reloading fitted Scikit-Learn estimators and vectorizers to disk for production inference.
   - *Resource*: [Scikit-learn Guide: Model Persistence](https://scikit-learn.org/stable/model_persistence.html).

---

### Phase 2: Vector Retrieval & pgvector Setup

#### Concepts from Syllabus A to Revise
- **ML Basics & Vector Spaces**:
  - Representing unstructured textual tickets as vectors \(\mathbf{x} \in \mathbb{R}^{384}\).
- **Cosine Similarity (Linear Algebra)**:
  - Mathematical definition:
    \[
    \cos(\theta) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}
    \]
  - For \(L_2\)-normalized vectors, cosine similarity equals the dot product \(\mathbf{u} \cdot \mathbf{v}\), bounded in \([-1, 1]\).
- **Evaluation Principles**:
  - Held-out test evaluation: using a dedicated 100-ticket benchmark set to objectively validate retrieval performance.

#### Concepts from Syllabus B to Learn
- **Vector Stores and Retrievers**:
  - Concept of storing vector embeddings alongside metadata in an index.
  - Querying the index using vector distance metrics to retrieve the top-K nearest neighbors.

#### Small Extras Needed in Phase 2
1. **PostgreSQL `pgvector` Extension**:
   - *Explanation*: An open-source extension that adds a native `VECTOR` data type and exact/approximate nearest neighbor distance operators (such as `<=>` for cosine distance) directly inside PostgreSQL.
   - *Resource*: [Supabase pgvector Official Guide](https://supabase.com/docs/guides/database/extensions/pgvector).
2. **Hit@K Evaluation Metric**:
   - *Explanation*: An information retrieval metric that measures the proportion of test queries for which at least one relevant, ground-truth match appears within the top-K retrieved results.
   - *Resource*: [Google ML Guide: Retrieval Metrics (Hit Rate / Precision@K)](https://developers.google.com/machine-learning/recommendation/dnn/retrieval).

---

### Phase 3: RAG Resolution Chain & Core FastAPI Service (MVP)

#### Concepts from Syllabus A to Revise
- **Supervised Inference & Probability Distributions**:
  - Extracting class probability distributions (`predict_proba`) from Logistic Regression models to feed confidence scores into API responses.

#### Concepts from Syllabus B to Learn
- **LangChain Components and Models**:
  - Initializing and invoking a hosted LLM (`ChatGoogleGenerativeAI`).
- **Prompt Templates**:
  - Building parameterized prompts that dynamically inject retrieved historical resolutions as context into the instructions.
- **Structured Output and Output Parsers**:
  - Constraining LLM generation to return strictly formatted, typed JSON conforming to a Pydantic schema (`suggested_fix`, `sources`, `confidence_note`).
- **Chains (Retrieve \(\to\) Prompt \(\to\) LLM)**:
  - Composing the sequential pipeline: ticket input \(\to\) vector retrieval \(\to\) prompt formatting \(\to\) LLM execution \(\to\) JSON parsing.
- **RAG Concept**:
  - Retrieval-Augmented Generation: using external retrieved factual context to ground an LLM's response, mitigating hallucinations.

#### Small Extras Needed in Phase 3
1. **LangChain `with_structured_output` for Pydantic**:
   - *Explanation*: A high-level LangChain method that binds a Pydantic class to an LLM call, guaranteeing a validated, strongly-typed Python dictionary/object response.
   - *Resource*: [LangChain Documentation: Structured Outputs](https://python.langchain.com/docs/how_to/structured_output/).

---

### Phase 4: Flutter Web Agent Dashboard

#### Concepts from Syllabus A & B
- *No new ML or LangChain theory.* This phase focuses on front-end software engineering, state management, and API consumption.

#### Small Extras Needed in Phase 4
1. **JWT Auth & HTTP Client in Flutter**:
   - *Explanation*: Handling asynchronous HTTP requests in Dart using the `http` package and attaching the JWT `Authorization: Bearer <token>` header to protected requests.
   - *Resource*: [Flutter Documentation: Fetch Data from the Internet](https://docs.flutter.dev/cookbook/networking/fetch-data).

---

### Phase 5: Testing, Hardening & Cloud Deployment

#### Concepts from Syllabus A to Revise
- **Evaluation & Verification**:
  - Re-running automated metric evaluations and test suites (`pytest`) to verify regression-free deployment.
- **Confusion Matrix in Production**:
  - Logging misclassified live samples for future continuous improvement.

#### Concepts from Syllabus B to Revise
- **RAG Latency & Guardrails**:
  - Measuring latency breakdown across vector search versus LLM generation.
  - Enforcing similarity score thresholding (\(\ge 0.65\)) to abort LLM calls when historical context is weak.

#### Small Extras Needed in Phase 5
1. **Multi-Stage Dockerfile for ML Applications**:
   - *Explanation*: Containerizing a Python application while caching HuggingFace embedding weights during image build time to prevent slow cold starts.
   - *Resource*: [Docker Guide: Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/).
2. **Supabase Connection Pooling (PgBouncer)**:
   - *Explanation*: Connecting to PostgreSQL through a transaction-mode connection pooler (port 6543) to prevent backend containers from exhausting available database sockets.
   - *Resource*: [Supabase Guide: Connection Management & PgBouncer](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler).
