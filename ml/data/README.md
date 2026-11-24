# IT Support Ticket Dataset Documentation

This directory documents the dataset schema, source, and preprocessing pipeline used for training TicketIQ's auto-triage classifier and indexing historical resolutions for vector similarity search.

---

## 1. Dataset Overview

- **Problem Domain**: Enterprise IT Helpdesk & Customer Support Incident Triage.
- **Source**: Kaggle IT Support / Customer Service Ticket Dataset (`customer_support_tickets.csv` / `all_tickets.csv`).
- **Primary Objectives**:
  1. Multiclass Classification: Predict ticket **Category** (*Hardware, Software, Network, Access*).
  2. Multiclass / Ordinal Classification: Predict ticket **Priority** (*Low, Medium, High, Critical*).
  3. Grounded Vector Retrieval: Retrieve top-3 semantically similar historical resolved tickets using cosine similarity on sentence embeddings.

---

## 2. Expected Schema

| Field Name | Type | Description | Role in TicketIQ |
| :--- | :--- | :--- | :--- |
| `ticket_id` | String / Int | Unique identifier of the ticket | Primary Key |
| `ticket_title` | String | Short subject line describing the problem | Feature text component |
| `ticket_description` | String | Detailed user narrative describing the error / fault | Primary feature text for embeddings & classification |
| `ticket_category` | String | Target label (*Hardware, Software, Network, Access*) | Classification Target 1 |
| `ticket_priority` | String | Target label (*Low, Medium, High, Critical*) | Classification Target 2 |
| `ticket_status` | String | Lifecycle state (*Open, In Progress, Resolved, Closed*) | Filter for vector retrieval (`Resolved` only) |
| `resolution_notes` | String | Concrete technician steps that resolved the issue | Grounding context for RAG generation |

---

## 3. Data Cleaning & Hygiene Rules

1. **Length Thresholding**: Exclude ticket descriptions shorter than 15 characters (e.g., *"help"*, *"broken"*) as they lack semantic signal.
2. **Boilerplate Filtering**: Strip out auto-generated email disclaimers, headers (*"From:", "Sent:"*), and signatures.
3. **Missing Resolution Filtering**: Historical records indexed for vector retrieval MUST have non-empty, actionable `resolution_notes` (excluding boilerplate placeholders like *"Closed by user"*, *"N/A"*).
4. **Stratified Splitting**: Use `StratifiedShuffleSplit` (80% Train, 20% Test) to ensure identical class distributions across both train and test partitions.
5. **Held-Out Retrieval Benchmark**: Reserve 100 historical queries with verified resolutions strictly for the Phase 2 Hit@3 evaluation benchmark.

---

## 4. How to Download

Raw dataset files are gitignored to prevent repository bloat. To acquire the dataset:

1. Download the customer support ticket CSV from Kaggle:
   - [Customer Support Ticket Dataset on Kaggle](https://www.kaggle.com/)
2. Place the downloaded CSV file into:
   ```text
   ml/data/raw/customer_support_tickets.csv
   ```
3. Run the exploratory data analysis notebook at `ml/notebooks/01_eda_and_baseline.ipynb`.
