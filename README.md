# AI_BLOG-API_Service
Service to consume the AI_Blog and creation of the rag

## Ojo:

gpt-3.5-turbo has a 16k token limit ( about 12 words) le request.

OpenAI: gpt-4-turbo has a 128,000 token window.

Gemini: gemini-1.5-pro has a 1 million token window.

The project works when launched locally with `uvicorn app.main:app --reload`.


### **Project Status & Next Steps**

Hello\! Here's where we left off:

#### **What We've Accomplished (The "Ingestion" Phase is Complete)**

You have successfully built a complete, end-to-end data ingestion and indexing pipeline. This is the hardest part, and it's fully functional.

  * **Document Parsing:** Your API has a powerful tool (`/api/tools/parser-tool`) that can take multiple file types (PDF, DOCX, etc.), parse them using `unstructured`, and correctly extract complex tables into HTML.
  * **Data Serialization:** The parsed output is saved as a clean, reusable JSON file in the `data/processed` folder.
  * **Indexing Pipeline:** Your script (`app/services/indexing.py`) can take any of these JSON files and load them into the vector database. This includes:
      * **Smart Chunking:** Grouping text by titles to create meaningful chunks.
      * **Multilingual Embeddings:** Using a local model to create vectors for both English and Spanish content.
      * **Vector Storage:** Storing the chunks, their metadata, and their embeddings in a Qdrant database that is optimized with Binary Quantization.

-----

### **What to Do Next (The "Retrieval" Phase)**

The entire data preparation stage is done. Your next and final step is to **use this indexed data to generate a blog post**.

You will need to modify your main blog generation workflow, which is primarily located in **`app/services/orchestrator.py`**.

Your task is to change the `run_generation_workflow` function to perform these steps:

1.  **Get the user's `topic`** from the API call.
2.  **Create an embedding** for that `topic` using the same `SentenceTransformer` model.
3.  **Search Qdrant** using this new embedding to find the most relevant text chunks from your documents.
4.  **Combine the text** from the search results into a single `context` string.
5.  **Pass this `context` string** to your `AI-Blog-App` library to generate the final, fact-based blog post.

-----

### **Quick Start Checklist for Next Time**

1.  Start the **Qdrant Docker container** in a terminal:
    ```bash
    docker run -p 6333:6333 -p 6334:6334 -v "$(pwd)/qdrant_storage:/qdrant/storage" qdrant/qdrant
    ```
2.  In a second terminal, start your **API server**:
    ```bash
    uvicorn app.main:app --reload
    ```
3.  The main file you'll be working in is **`app/services/orchestrator.py`**.