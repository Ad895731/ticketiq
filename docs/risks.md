# TicketIQ — Production Risks & Mitigation Strategies

This document identifies the 5 primary risks in building TicketIQ — spanning dataset quality, statistical class imbalance, LLM hallucinations, free-tier limits, and vector dimensional integrity — alongside concrete engineering mitigations.

---

## Risk Matrix Summary

| # | Risk Area | Severity | Likelihood | Key Mitigation |
| :- | :--- | :--- | :--- | :--- |
| **1** | **Dataset Quality & Noisy Resolutions** | High | High | Strict data cleaning pipeline: length thresholding & removal of boilerplate resolutions |
| **2** | **Class Imbalance in Category & Priority** | High | High | Stratified train/test splitting, `class_weight='balanced'`, and Macro-F1 evaluation |
| **3** | **LLM Hallucination in Technical Fixes** | Critical | Medium | Similarity gating (\(\ge 0.65\)), strict prompt grounding, and Pydantic structured output |
| **4** | **Free-Tier API & Cloud Rate Limits** | Medium | High | In-memory LRU caching, Supabase transaction pooling, and graceful backoff |
| **5** | **Vector Dimension & Distance Metric Mismatch** | High | Low | Explicit DDL constraints (`vector(384)`), \(L_2\) normalization, and cosine distance `<=>` |

---

## Detailed Risk Analysis & Mitigations

### 1. Dataset Quality & Missing Ticket Resolution Text

#### The Risk
Public IT support datasets from Kaggle often contain incomplete rows, placeholder descriptions (*"Help, my screen is blue"*), or meaningless resolution notes (*"Resolved by user"*, *"Issue closed"*, *"N/A"*). If these low-quality records are indexed in the vector store, similarity searches will retrieve irrelevant records, and the RAG model will generate useless or corrupt recommendations.

#### Engineering Mitigations
1. **Resolution Quality Filter**:
   - In Day 2 preprocessing, discard any historical ticket where `resolution_notes` is null, has fewer than 25 characters, or matches common boilerplate regexes:
     ```python
     boilerplate_patterns = [r"^resolved", r"^fixed", r"^closed", r"^ticket closed", r"^n/a$"]
     ```
2. **Text Normalization Pipeline**:
   - Clean both titles and descriptions: strip HTML tags, normalize whitespace, lowercase text, and remove non-informative ticket IDs or automated email headers.
3. **Curated Historical Index**:
   - Only index tickets marked with `status = 'Resolved'` that have verified, substantive resolution notes.

---

### 2. Severe Class Imbalance (Category & Priority)

#### The Risk
In real helpdesk data, categories and priorities are heavily skewed:
- Priorities: ~65% *Low*, ~25% *Medium*, ~8% *High*, ~2% *Critical*.
- Categories: ~50% *Software*, ~30% *Hardware*, ~15% *Network*, ~5% *Access*.

A standard classifier optimizing for naive accuracy will predict the majority class (*Low* / *Software*) for all tickets, achieving ~65% accuracy while completely failing on *Critical* or *Access* tickets.

#### Engineering Mitigations
1. **Stratified Splitting**:
   - Use `StratifiedShuffleSplit` in Scikit-Learn to ensure that train and test partitions maintain identical class distributions for both Category and Priority.
2. **Class-Weighted Loss Optimization**:
   - Configure Scikit-Learn's `LogisticRegression(class_weight='balanced')`. This automatically adjusts weights inversely proportional to class frequencies:
     \[
     w_j = \frac{N}{K \cdot n_j}
     \]
     where \(N\) is total samples, \(K\) is number of classes, and \(n_j\) is the sample count of class \(j\). Errors on minority classes (*Critical*) are penalized far more heavily during gradient descent.
3. **Metric Alignment**:
   - Reject accuracy as a primary metric. Use **Macro-averaged F1 Score**, which computes the arithmetic mean of F1 scores across each class independently, treating minority and majority classes with equal weight.

---

### 3. LLM Hallucination & Ungrounded Resolutions

#### The Risk
LLMs given loose prompts will attempt to be helpful by inventing IT procedures, non-existent terminal commands, or insecure password reset links. In an IT enterprise setting, an invented or incorrect command can cause system downtime or data loss.

#### Engineering Mitigations
1. **Similarity Score Gating (Pre-LLM Guardrail)**:
   - Before invoking Gemini, inspect the cosine similarity score of the top retrieved historical ticket.
   - If `top_similarity < 0.65`, do **not** invoke the LLM. Immediately return a deterministic fallback response:
     ```json
     {
       "suggested_fix": "No sufficiently similar historical resolution found (similarity < 0.65). Please escalate this ticket to a Tier-2 IT Specialist.",
       "sources": [],
       "confidence_note": "Below automated resolution threshold."
     }
     ```
2. **Strict Grounding Prompt Template**:
   - Instruct the LLM that it is an administrative assistant summarizing verified records, strictly forbidding external facts:
     ```text
     You are an IT resolution assistant. You are provided with 3 historically resolved tickets.
     Synthesize a clear, step-by-step fix ONLY using the historical resolutions provided.
     Do NOT add outside knowledge, do NOT invent commands, and do NOT assume software versions.
     If the provided resolutions do not clearly solve the user's issue, state: "Historical data is insufficient to resolve this issue."
     ```
3. **Structured Pydantic Enforcement**:
   - Use `with_structured_output` to require the LLM to return source ticket IDs in the `sources` field. If the model cannot cite an ID from the context, the response is rejected.

---

### 4. Free-Tier API Rate Limits & Cloud Resource Constraints

#### The Risk
- **Google Gemini API**: Free tier enforces a strict limit of 15 Requests Per Minute (RPM). Rapid testing or multi-user interaction can trigger HTTP 429 errors.
- **Supabase Free Tier**: Free compute allows limited concurrent direct database connections (often 60 pooler / direct connections).
- **Render Web Service Free Tier**: Free web services spin down after 15 minutes of inactivity, resulting in a 30–50 second cold start delay.

#### Engineering Mitigations
1. **In-Memory Embedding Caching**:
   - Implement an LRU cache (`@lru_cache(maxsize=1024)`) in the embedding service so repetitive queries (e.g. duplicate search terms) return cached 384-dim vectors without recomputing.
2. **Local Model Inference**:
   - All classification (`LogisticRegression`) and sentence encoding (`all-MiniLM-L6-v2`) runs locally on the CPU in Python. No external API quotas are consumed for classification or vector generation.
3. **Exponential Backoff for Gemini Calls**:
   - Wrap the LangChain Gemini call with retry logic (using `tenacity`) that handles HTTP 429 rate limits gracefully with exponential backoff and jitter.
4. **Supabase Connection Pooling (Transaction Mode)**:
   - Direct all backend database queries through Supabase PgBouncer (port 6543) instead of direct port 5432. This reuses database connections across stateless FastAPI requests.

---

### 5. Vector Dimension & Distance Metric Mismatch

#### The Risk
A common defect in vector applications is initializing the database column with the wrong dimension (e.g. `vector(1536)` intended for OpenAI models instead of `vector(384)` for `all-MiniLM-L6-v2`), or querying with Euclidean distance (`<->`) when the vectors are compared using cosine similarity.

#### Engineering Mitigations
1. **Explicit Schema Typing**:
   - Define the PostgreSQL column strictly as `embedding vector(384)` in Alembic migrations.
2. **Vector Normalization**:
   - Ensure `sentence-transformers` generates \(L_2\)-normalized vectors:
     ```python
     model.encode(text, normalize_embeddings=True)
     ```
   - When vectors have unit length (\(\|\mathbf{u}\|_2 = 1\)), Cosine Distance is directly proportional to Euclidean distance:
     \[
     \|\mathbf{u} - \mathbf{v}\|_2^2 = 2(1 - \mathbf{u} \cdot \mathbf{v})
     \]
3. **Dedicated Unit Tests**:
   - Include an automated Pytest verifying that the vector output of `encoder.py` always returns an array of shape `(384,)` with unit magnitude before inserting into the database.
