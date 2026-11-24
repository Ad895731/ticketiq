# TicketIQ — Resume Bullets & Interview Defense Guide

This guide provides interview-ready resume bullet points formatted according to Google's **XYZ formula** (*Accomplished [X], as measured by [Y], by doing [Z]*), complete with realistic metric placeholders and an interview defense cheat-sheet.

---

## 1. Google XYZ Resume Bullets

### Variant 1: General Software Engineer / Backend Focus
> **TicketIQ — AI IT-Helpdesk Triage & Resolution Platform**
> - Architected a high-throughput IT service desk backend in **FastAPI** and **PostgreSQL (pgvector)**, reducing ticket resolution turnaround by **[60%]** through automated auto-triage and semantic duplicate detection.
> - Implemented role-based access control (**JWT / RBAC**) across user, agent, and admin tiers; constructed a complete **Pytest** automated testing suite achieving **[92%]** code coverage across auth, CRUD, and ML inference pipelines.
> - Optimized database vector queries using **HNSW indexing** on **384-dimensional** sentence embeddings, sustaining **[<100 ms]** retrieval latency across **[5,000+]** historical support records on Supabase.
> - Containerized the backend with multi-stage **Docker** builds and deployed on **Render** with connection pooling (PgBouncer), eliminating cold-start model download overhead.

---

### Variant 2: Applied Machine Learning / Triage Focus
> **TicketIQ — Intelligent Ticket Classification & Routing System**
> - Developed an explainable multi-class text classification pipeline in **Scikit-Learn** predicting IT ticket category and priority, improving baseline TF-IDF performance by **[+14%]** to achieve **[81%] Category Macro-F1** and **[71%] Priority Macro-F1**.
> - Extracted semantic representations using pretrained **all-MiniLM-L6-v2** sentence transformers and trained balanced **Logistic Regression** classifiers, mitigating heavy 70:1 class imbalance using inverse-frequency loss weighting.
> - Formulated an offline evaluation benchmark on a **100-ticket held-out set**, validating a **[86%] Hit@3** duplicate retrieval rate using cosine similarity over dense vector embeddings.
> - Serialized trained models via **Joblib** and engineered an in-memory caching layer, delivering single-ticket inference in **[<25 ms]** on CPU.

---

### Variant 3: RAG & Generative AI Systems Focus
> **TicketIQ — Grounded RAG IT Resolution Assistant**
> - Designed a grounded **Retrieval-Augmented Generation (RAG)** pipeline using **LangChain** and **Google Gemini 1.5 Flash**, synthesizing verified step-by-step IT troubleshooting guidance from historical resolutions in **[<2.2 s]**.
> - Enforced strict hallucination guardrails via cosine similarity thresholding (**threshold = 0.65**) and **Pydantic structured output parsing**, guaranteeing validated JSON schema responses with cited source ticket IDs.
> - Integrated vector search directly into relational PostgreSQL via **pgvector**, unifying relational ticket metadata with dense vector embeddings into a single ACID-compliant database architecture.

---

### Variant 4: Full-Stack / End-to-End Product Focus
> **TicketIQ — End-to-End AI Helpdesk Web Application**
> - Engineered an end-to-end IT support suite comprising a **FastAPI** microservice, **PostgreSQL/pgvector** storage, and a responsive **Flutter Web** agent dashboard.
> - Integrated real-time AI triage badges, similar ticket recommendation drawers, and a one-click resolution applicator, enabling support agents to review and accept AI-generated fixes in one action.
> - Deployed the production system to **Render** and **Supabase**, ensuring resilient continuous integration through automated end-to-end tests and zero CORS latency.

---

## 2. Interview Defense Cheat-Sheet (High-Yield Q&A)

Here are the 5 questions interviewers will ask about this project, along with exact, mathematically defensible answers tailored to your background.

---

### Q1: "Why did you use Logistic Regression with sentence embeddings instead of fine-tuning a BERT model or calling an LLM for classification?"

**Your Answer**:
> *"I deliberately chose Logistic Regression on top of frozen sentence embeddings (`all-MiniLM-L6-v2`) for three engineering reasons:*
> 1. ***Inference Latency & Cost***: *Calling an LLM for triage adds 1–2 seconds of network latency and token costs per ticket. A Logistic Regression model runs in under 25 milliseconds directly on CPU with zero API costs.*
> 2. ***Explainability & Probabilities***: *Logistic Regression outputs well-calibrated class probability distributions via the Softmax function. This allows our backend to assign confidence scores to predictions and flag low-confidence tickets for manual agent review.*
> 3. ***Sample Efficiency & Defense***: *Fine-tuning a full transformer with limited IT helpdesk data easily leads to overfitting. Using a high-quality pretrained sentence encoder as a fixed feature extractor and fitting a convex loss function (cross-entropy with L2 regularization) guaranteed fast convergence, explainable decision boundaries, and no GPU requirements.*"

---

### Q2: "How did you handle the severe class imbalance in ticket priorities?"

**Your Answer**:
> *"Priority distribution in helpdesk logs is naturally skewed—Low and Medium tickets account for over 85% of samples, while Critical tickets are under 3%. If you optimize for standard accuracy, a trivial model predicting 'Low' achieves high accuracy while failing completely on critical outages.*
> *I addressed this systematically:*
> 1. *I used **Stratified Splitting** (`StratifiedShuffleSplit`) to ensure both train and test partitions reflected the true distribution.*
> 2. *I configured **balanced class weighting** in the Logistic Regression cost function. This weights the cross-entropy loss inversely proportional to class frequencies: \(w_j = \frac{N}{K \cdot n_j}\). Penalizing errors on minority classes heavily during gradient descent prevented the decision boundaries from collapsing toward the majority class.*
> 3. *I evaluated the model using **Macro-averaged F1** rather than accuracy or Micro-F1, giving equal importance to Critical and Low classes.*"

---

### Q3: "Why did you store embeddings in PostgreSQL with pgvector instead of using a standalone vector DB like Pinecone, Chroma, or Weaviate?"

**Your Answer**:
> *"In a production IT helpdesk system, tickets are relational entities with foreign keys (requesters, assignees), audit logs, and strict state transitions (Open \(\to\) In Progress \(\to\) Resolved).*
> *Using a dedicated vector database creates an **operational two-system problem**: you have to synchronize relational updates in PostgreSQL with vector updates in Pinecone, risking data drift and requiring distributed transaction handling.*
> *With `pgvector`, our embeddings live directly inside the `tickets` table as a `vector(384)` column. We can execute a single ACID transaction that updates a ticket's status and re-indexes its embedding simultaneously, and perform filtered nearest-neighbor queries using standard SQL with HNSW index performance."*

---

### Q4: "How did you objectively evaluate your retrieval system before feeding context into the LLM?"

**Your Answer**:
> *"I did not rely on subjective inspection. I constructed a dedicated **100-ticket held-out evaluation set** (`eval_100_heldout.csv`) from historical resolved tickets.*
> *I evaluated the retriever using **Hit@3**: for each test ticket description, we executed an automated vector query retrieving the top-3 historical matches and checked whether at least one retrieved ticket matched the ground-truth root cause category and had an actionable resolution.*
> *TicketIQ achieved an **[86%] Hit@3** rate. Furthermore, we benchmarked retrieval latency using `EXPLAIN ANALYZE` on Supabase to verify that HNSW index searches executed in under 100 milliseconds."*

---

### Q5: "How did you guarantee that the LLM wouldn't hallucinate fake terminal commands or dangerous IT procedures in the resolution suggestion?"

**Your Answer**:
> *"We implemented a 3-layer defense against hallucinations:*
> 1. ***Pre-LLM Similarity Gating***: *Before calling the LLM, we check the cosine similarity of the top retrieved historical ticket. If it is below `0.65`, we abort the LLM call entirely and return a deterministic message advising human escalation. We never ask an LLM to generate answers when historical context is absent.*
> 2. ***Strict Grounding Prompt***: *Our system prompt explicitly defines the LLM as a synthesizer of provided records, strictly forbidding the introduction of outside facts or unverified commands.*
> 3. ***Pydantic Schema Validation***: *Using LangChain's `with_structured_output`, the model is forced to return a JSON object containing a `sources` array citing the exact historical ticket IDs used. If the model fails schema validation or cannot cite sources, the response is rejected.*"
