# RAG Job Assistant

A production-grade Retrieval-Augmented Generation (RAG) application that lets you query thousands of real job listings using natural language. Ask questions like *"Which fintech companies have remote AI engineer roles that sponsor visas?"* and get precise, cited answers backed by a local vector database.

Built as a demonstration of end-to-end RAG architecture — from data ingestion and vector embedding to semantic retrieval and LLM-powered answer generation.

---

## What It Does

Most job boards offer keyword search. This app offers **semantic search** — it understands the *meaning* of your query and matches it against job descriptions, not just surface-level keywords.

Under the hood:
- 5,000+ job postings are embedded into a local vector database using a sentence transformer model
- At query time, your question is embedded and matched against all job vectors using cosine similarity
- The top matches are passed as context to a large language model (Llama 3.3 70B via Groq)
- The LLM synthesises a precise, cited answer using only the retrieved jobs — no hallucination

---

## Architecture

```
SQLite Database (job postings)
        |
        v
[ Ingest Pipeline ]
  - Strip HTML from descriptions
  - Build structured text document per job
  - Embed with all-MiniLM-L6-v2 (runs locally, no API needed)
  - Store vectors + metadata in ChromaDB (persisted to disk)
        |
        v
[ Query Engine ]
  User question --> Embed question --> Vector similarity search
        |
        v
  Top-K job matches --> Build context prompt --> Groq LLM (Llama 3.3 70B)
        |
        v
  Natural language answer with citations and job URLs
```

---

## Features

- **Semantic search** — finds jobs by meaning, not keywords. "ML position" matches "machine learning role"
- **Natural language Q&A** — ask in plain English, get cited answers with direct job links
- **Animated Streamlit UI** — chat interface with job cards, hover effects, and staggered animations
- **Raw search mode** — bypass the LLM for instant vector similarity results
- **Sidebar filters** — filter by remote, active listings, or experience level before searching
- **Incremental ingestion** — re-run `ingest.py` any time to pick up new jobs without re-indexing existing ones
- **CLI mode** — terminal interface for quick queries without launching the web app
- **Zero cloud dependency for embeddings** — the sentence transformer model runs fully locally (ONNX)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Vector database | [ChromaDB](https://www.trychroma.com/) |
| Embedding model | `all-MiniLM-L6-v2` (ONNX, local) |
| LLM | Llama 3.3 70B via [Groq](https://console.groq.com) |
| Web UI | [Streamlit](https://streamlit.io) |
| Data source | SQLite (via your job scraping pipeline) |
| Language | Python 3.11 |

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/OzSpidey/RAG-Job-Assistant.git
cd RAG-Job-Assistant
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in:

```env
GROQ_API_KEY=your_groq_api_key_here   # free at console.groq.com
JOB_DB_PATH=/path/to/your/jobs.db     # SQLite DB with a 'jobs' table
```

**Getting a free Groq API key:** Sign up at [console.groq.com](https://console.groq.com) — no credit card required. The free tier allows 14,400 requests per day.

### 4. Build the vector index

```bash
python ingest.py
```

This reads your SQLite database, embeds all job postings, and stores them in ChromaDB. Run time is roughly 1-2 minutes for 5,000 jobs on first run. Subsequent runs are incremental.

### 5. Launch the web app

```bash
python -m streamlit run app.py
```

Opens at `http://localhost:8501`.

Or use the terminal CLI:

```bash
python cli.py
```

---

## Database Schema

The app expects a SQLite `jobs` table with these columns:

| Column | Type | Description |
|---|---|---|
| `id` | VARCHAR | Unique job ID |
| `title` | VARCHAR | Job title |
| `company_name` | VARCHAR | Company name |
| `location` | VARCHAR | Job location |
| `department` | VARCHAR | Department or team |
| `description` | TEXT | Full job description (HTML or plain text) |
| `url` | VARCHAR | Direct application URL |
| `ats` | VARCHAR | ATS platform (greenhouse, lever, ashby, etc.) |
| `is_remote` | BOOLEAN | Remote-friendly flag |
| `is_active` | BOOLEAN | Whether the listing is currently open |
| `experience_level` | VARCHAR | entry / mid / senior / unknown |
| `visa_sponsorship` | VARCHAR | yes / maybe / no / unknown |
| `scraped_at` | DATETIME | When the job was scraped |

---

## Example Queries

**Natural language questions (Chat tab):**

```
Which companies have AI Engineer or ML Engineer roles that are remote?
Show me entry level data engineering jobs that offer visa sponsorship
What skills does Anthropic require for their engineering roles?
Compare the requirements for software engineer roles at Stripe vs Dropbox
Which companies are hiring the most right now?
Jobs that mention RAG, LLM, or vector databases in the description
```

**Raw semantic search (Search tab):**

```
machine learning infrastructure python
remote fintech backend engineer
data pipeline spark dbt
```

---

## How RAG Works (Simple Explanation)

Traditional search matches your query to keywords. RAG does something smarter:

1. **Embed** — every job description is converted into a list of numbers (a vector) that captures its *meaning*. Similar jobs produce similar numbers.
2. **Search** — your question is converted the same way. ChromaDB finds the stored jobs whose vectors are closest to your question's vector.
3. **Generate** — the top matching jobs are handed to an LLM as context. The LLM reads only those jobs and writes a precise answer. It cannot make up jobs that aren't there.

The result: you get answers grounded in real data, not hallucinations.

---

## Project Structure

```
RAG-Job-Assistant/
├── app.py            # Streamlit web UI (chat + search tabs, animated cards)
├── cli.py            # Terminal interface
├── config.py         # Paths, model settings, constants
├── ingest.py         # SQLite -> ChromaDB ingestion pipeline
├── query.py          # Vector search + Groq LLM generation
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Author

**Osborne Lopes**
[LinkedIn](https://www.linkedin.com/in/osborne-lopes/) | [GitHub](https://github.com/OzSpidey)
