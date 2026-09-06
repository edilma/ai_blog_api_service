# AI Blog API & RAG Pipeline Service

A FastAPI backend that generates original, fact-grounded content from source documents — product articles from manufacturer spec sheets, unique listing descriptions from property details.

Upload PDFs, Word files, or slide decks; the service parses them, indexes them into a vector database, and writes from what those documents actually say rather than from whatever the model happens to know.

---

## Why I built it

Two industries I worked in have the same content problem, and it isn't a lack of information — it's that everyone has the *same* information.

**E-commerce.** The manufacturer supplies a spec sheet and a paragraph of copy. Every store selling that product publishes that same paragraph. Search engines see duplicate content, nothing distinguishes one storefront from another, and hand-writing original copy across a few thousand SKUs isn't realistic.

**Real estate.** The listing agent writes one description and it syndicates unchanged to every portal. It's often thin, sometimes poor, and it's identical everywhere a buyer might encounter the property.

In both cases the raw material already exists — manufacturer documentation, property details, spec sheets — it just needs to become original writing, per item, at volume.

That's what this service does. It ingests the source documents, retrieves the passages relevant to a given topic, and generates content grounded in them. Facts come from the document, so specifications and details stay accurate; the writing is new every time.

Multilingual support (English and Spanish) was a deliberate choice rather than a technical flourish — both markets matter in South Florida, where I did this work.

---

## Architecture

The service is deliberately decoupled — ingestion, indexing, and generation are separate stages that can be run and debugged independently.

```text
Document (PDF/DOCX/PPTX/HTML/MD)
          │
          ▼
   Document Parser          unstructured + Tesseract OCR + Poppler
   app/routers/parsing.py   → structured JSON (titles, paragraphs, tables)
          │
          ▼
   Indexing Service         chunk-by-title → multilingual embeddings
   app/services/indexing.py → Qdrant (binary quantization)
          │
          ▼
   Generation Service       semantic retrieval + metadata filtering
   app/services/orchestrator.py
          │
          ▼
   ai-blog-app              multi-agent writing pipeline (my library)
          │
          ▼
   SQLite (blog.db)         generated posts
```

| Component | Role |
|---|---|
| **FastAPI Server** (`app/`) | Exposes all API endpoints |
| **Document Parser** (`app/routers/parsing.py`) | Handles uploads, parses with `unstructured`, serializes to JSON |
| **Indexing Service** (`app/services/indexing.py`) | Chunks content, creates embeddings, loads into Qdrant |
| **Generation Service** (`app/services/orchestrator.py`) | Retrieves context and calls the generation library |
| **Qdrant** | Vector database, running in Docker |
| **SQLite + SQLModel** | Persists generated posts |

### Built on my own library

Generation is handled by [**`ai-blog-app`**](https://github.com/edilma/ai-blog-app) — an open-source Python library I wrote and published to [PyPI](https://pypi.org/project/ai-blog-app/). It runs a multi-agent pipeline in which a writer, a critic, and three specialized reviewers (SEO, content marketing, clarity and ethics) refine the draft collaboratively.

Keeping generation in a separate installable package means this service handles retrieval and the library handles writing, and either can be improved without touching the other.

---

## Features

**Document ingestion**

- Accepts PDF, DOCX, PPTX, HTML, and Markdown
- Parses with `unstructured`, using Tesseract OCR and Poppler layout detection to partition documents into titles, paragraphs, and tables
- Serializes parsed output to reusable JSON, creating a standardized knowledge base

**Vector indexing**

- **Chunk-by-title** strategy produces semantically coherent chunks instead of arbitrary fixed-size splits
- **Multilingual embeddings** via a local `SentenceTransformer` model (`paraphrase-multilingual-MiniLM-L12-v2`), supporting English and Spanish
- **Multi-representation indexing** generates AI summaries for tables, which retrieve poorly when embedded as raw text
- **Binary quantization** in Qdrant for memory-efficient storage and fast search

**Generation**

- Retrieves the most relevant context for a given topic
- **Metadata filtering** constrains retrieval to specified source documents, so output can be traced to a known set of inputs
- Passes context to `ai-blog-app` for grounded, non-hallucinated generation
- Persists results to SQLite via SQLModel

**Tooling**

- A web-based **Document Parser Inspector** for visually verifying what the parser extracted before indexing

---

## Prerequisites

- **Python 3.12+**
- **Docker Desktop** — runs the Qdrant vector database
- **Poppler** — required by `unstructured` for PDF processing
- **Tesseract** — OCR engine for the `hi_res` parsing strategy

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/edilma/ai_blog_api_service.git
cd ai_blog_api_service
```

**2. Create and activate the virtual environment**

This project uses `uv` for package management.

```powershell
uv venv
.\.venv\Scripts\Activate.ps1
```

**3. Install dependencies**

```powershell
uv sync
```

**4. Set up environment variables**

Create a `.env` file in the project root:

```env
OPENAI_API_KEY="your-key-here"
GEMINI_API_KEY="your-key-here"
```

---

## Running the Application

Two services run in two terminals.

**Terminal 1 — Qdrant**

```powershell
docker run -p 6333:6333 -p 6334:6334 -v "${PWD}/qdrant_storage:/qdrant/storage" qdrant/qdrant
```

**Terminal 2 — FastAPI**

```powershell
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`, with interactive docs at `/docs`.

---

## Usage

**1. Parse a document**

Open the Document Parser Inspector at `http://127.0.0.1:8000/api/tools/parser-tool` and upload a file. The parsed result is saved as `TIMESTAMP_my_document.json` in `data/processed`, and the tool shows you exactly what was extracted — worth checking before indexing, since parsing is where most quality problems originate.

**2. Index the document**

Open `app/services/indexing.py`, set the `test_file` variable in the `__main__` block to your JSON filename, choose an indexing strategy (`smart_indexing=True` or `False`), then run:

```powershell
uv run app/services/indexing.py
```

**3. Generate an article**

At `http://127.0.0.1:8000/docs`, call `POST /api/generate-blog` with a `topic` and the JSON filename in `source_files`. The generated post is saved to `blog.db`.

---

## Notes and Limitations

- **Indexing is triggered by editing a variable in `indexing.py`** rather than through an API endpoint. It works, but it's the clearest thing to lift into a proper endpoint next.
- **Parsing quality sets the ceiling on output quality.** Documents with complex multi-column layouts or scanned tables extract less reliably, which is why the Parser Inspector exists.
- **Chunk-by-title assumes documents have real structure.** Content without clear titles and sections chunks less coherently.
- **No automated evaluation.** Output quality was assessed by reading it against the source documents.
- **Single-user, local deployment.** No authentication, rate limiting, or multi-tenancy — this was built as a working prototype, not a hosted service.

---

## License

MIT — see [LICENSE](LICENSE).
