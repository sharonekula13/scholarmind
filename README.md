cat > README.md << 'ENDOFFILE'
# ScholarMind

AI-powered research paper assistant using Retrieval-Augmented Generation (RAG). Upload academic papers and ask questions — get citation-backed answers grounded in the actual source text.

## Features

- PDF Ingestion — Upload multiple research papers with automatic text extraction and recursive chunking
- Hybrid Search — Combines dense semantic search (Sentence-Transformers + FAISS) with sparse BM25 keyword search
- Local LLM — Runs Llama 3.2 locally via Ollama for cost-free, privacy-preserving inference
- Citation Tracking — Every answer includes page-level source citations
- Evaluation Framework — Built-in retrieval quality measurement using Recall@K and MRR metrics
- REST API — FastAPI backend with OpenAPI documentation
- Chat UI — Streamlit-based conversational interface

## Architecture

User uploads PDF → PyMuPDF extracts text → LangChain chunks with overlap → Sentence-Transformers generates embeddings → FAISS indexes vectors

User asks question → Question embedded with same model → Hybrid search (semantic + BM25) finds top chunks → Chunks + question sent to Llama 3.2 via Ollama → Answer generated with page citations → Displayed in Streamlit UI

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12 |
| LLM Framework | LangChain |
| Embeddings | Sentence-Transformers (all-MiniLM-L6-v2) |
| Vector Store | FAISS |
| Keyword Search | BM25 (rank-bm25) |
| LLM | Llama 3.2 via Ollama |
| Backend | FastAPI |
| Frontend | Streamlit |
| Containerization | Docker |

## Setup

Prerequisites: Python 3.10+, Ollama installed (brew install ollama)

Installation:

    git clone https://github.com/sharonekula13/scholarmind.git
    cd scholarmind
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Download LLM Model:

    ollama serve &
    ollama pull llama3.2

Run the API:

    PYTHONPATH=. uvicorn src.api.server:app --reload --port 8000

Run the UI (new terminal):

    streamlit run ui/app.py

Open http://localhost:8501 in your browser.

API docs available at http://localhost:8000/docs

## Evaluation

Run retrieval evaluation:

    PYTHONPATH=. python scripts/test_weights.py

Results on a curated 8-question test set:

| Metric | Score |
|--------|-------|
| Recall@5 | 75.00% |
| MRR | 47.92% |
| Best semantic weight | 0.3 (keyword-heavy) |

## Testing

    PYTHONPATH=. pytest tests/ -v

## Project Structure

    scholarmind/
    ├── src/
    │   ├── api/            # FastAPI endpoints
    │   ├── core/           # Configuration
    │   ├── evaluation/     # Retrieval quality metrics
    │   ├── generation/     # LLM answer generation
    │   ├── ingestion/      # PDF loading and chunking
    │   ├── retrieval/      # Embeddings, FAISS, hybrid search
    │   └── utils/          # Helpers
    ├── tests/              # Unit and integration tests
    ├── ui/                 # Streamlit frontend
    ├── data/               # PDFs and vector store
    ├── scripts/            # Evaluation scripts
    ├── Dockerfile          # Container configuration
    └── requirements.txt    # Dependencies

## License

MIT
ENDOFFILE