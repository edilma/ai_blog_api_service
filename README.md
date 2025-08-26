# AI Blog API & RAG Pipeline Service

This project is a sophisticated FastAPI application that serves as a flexible backend for a powerful, multi-stage content generation system. It leverages a Retrieval-Augmented Generation (RAG) pipeline to create fact-based blog posts from user-provided narrative and semi-structured documents.

The system is designed to excel at processing content with a clear, logical flow, such as articles, reports, and web pages that are organized with titles and sections. It serves as a robust foundation that can be extended and specialized for more complex, domain-specific tasks (e.g., real estate or financial analysis).

The architecture is clean and decoupled, separating data ingestion, processing, and content generation into distinct, manageable services.

---

## Features

* **Multi-Format Document Ingestion:** Accepts a wide variety of document formats, including PDF, DOCX, PPTX, HTML, and Markdown.
* **Advanced Document Parsing:** Uses the `unstructured` library with OCR (`Tesseract`) and layout detection (`Poppler`) to intelligently partition complex documents into structured elements like titles, paragraphs, and tables.
* **Data Serialization:** The parsed output from documents is saved as a clean, reusable JSON format, creating a standardized knowledge base.
* **Vector Indexing:**
    * **Smart Chunking:** Implements an advanced "chunk-by-title" strategy to create semantically coherent text chunks.
    * **Multilingual Embeddings:** Uses a local `SentenceTransformer` model (`paraphrase-multilingual-MiniLM-L12-v2`) to support both English and Spanish content.
    * **Multi-Representation Indexing:** For complex elements like tables, it generates AI-powered summaries to improve retrieval accuracy.
* **High-Performance Vector Database:** Uses **Qdrant** with Binary Quantization enabled for efficient, memory-optimized vector storage and fast semantic search.
* **RAG-Based Content Generation:**
    * Retrieves the most relevant context from the vector database based on a user's topic.
    * Uses **metadata filtering** to ensure context is only pulled from specified source documents.
    * Passes the retrieved context to an external agentic library (`ai_blog_app`) to generate a fact-based, non-hallucinated blog post.
* **Persistent Storage:** Saves all generated blog posts to a local SQLite database using SQLModel.
* **Diagnostic Tools:** Includes a web-based "Document Parser Inspector" to visually test and verify the document parsing pipeline.

---

## Architecture Overview

The service is composed of several key components that work together:

1.  **FastAPI Server (`app/`):** The main application that exposes all API endpoints.
2.  **Document Parser (`app/routers/parsing.py`):** An endpoint that handles file uploads, uses `unstructured` to parse them, and saves the output as JSON.
3.  **Indexing Service (`app/services/indexing.py`):** A script that reads the processed JSON files, chunks the content, creates embeddings, and uploads everything to the Qdrant database.
4.  **Generation Service (`app/services/orchestrator.py`):** The core RAG workflow that retrieves context from Qdrant and calls the external `ai_blog_app` library to generate content.
5.  **Qdrant Database:** A Docker container running the Qdrant vector database for storing and searching document embeddings.
6.  **SQLite Database:** A local file-based database for storing the final generated blog posts.

---

## Prerequisites

Before you begin, ensure you have the following system-level dependencies installed:

1.  **Python** (>=3.12)
2.  **Docker Desktop:** To run the Qdrant vector database.
3.  **Poppler:** Required by `unstructured` for PDF processing.
4.  **Tesseract:** The OCR engine required for the `hi_res` parsing strategy.

---

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd ai_blog_api_service
    ```

2.  **Create and activate the virtual environment:**
    This project uses `uv` for package management.
    ```bash
    # Create the virtual environment
    uv venv

    # Activate the environment (PowerShell)
    .\.venv\Scripts\Activate.ps1
    ```

3.  **Install dependencies:**
    This command will read the `pyproject.toml` file, create a `uv.lock` file, and install all necessary packages.
    ```bash
    uv sync
    ```

4.  **Set up environment variables:**
    Create a file named `.env` in the project's root directory and add your API keys:
    ```env
    OPENAI_API_KEY="sk-..."
    GEMINI_API_KEY="..."
    ```

---

## Running the Application

The application requires two separate services to be running in two different terminals.

1.  **Start the Qdrant Database:**
    Open a terminal in the project root and run the following Docker command. This will start the Qdrant container and create a `qdrant_storage` folder to persist your data.
    ```bash
    docker run -p 6333:6333 -p 6334:6334 -v "$(pwd)/qdrant_storage:/qdrant/storage" qdrant/qdrant
    ```

2.  **Start the FastAPI Server:**
    Open a **second terminal**, activate the virtual environment, and run the Uvicorn server.
    ```bash
    uvicorn app.main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.

---

## Usage Workflow

The system is designed to be used in a three-step process:

1.  **Parse a Document:**
    * Navigate to the Document Parser Inspector tool at `http://127.0.0.1:8000/api/tools/parser-tool`.
    * Upload a document (e.g., `my_document.pdf`).
    * This will process the file and save a corresponding `TIMESTAMP_my_document.json` file in the `data/processed` directory.

2.  **Index the Document:**
    * Open the `app/services/indexing.py` file.
    * Update the `test_file` variable in the `if __name__ == "__main__"` block to the name of the JSON file you just created.
    * Choose your indexing strategy (`smart_indexing=True` or `False`).
    * Run the script from a **new terminal**:
        ```bash
        uv run app/services/indexing.py
        ```
    * This will load the document's content into the Qdrant database.

3.  **Generate a Blog Post:**
    * Navigate to the API documentation at `http://127.0.0.1:8000/docs`.
    * Use the `POST /api/generate-blog` endpoint.
    * Provide a `topic` for your blog post.
    * In the `source_files` field, provide the name of the JSON file you want to use as context.
    * Execute the request. The generated blog post will be saved to the `blog.db` database.