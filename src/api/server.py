from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import shutil
import os

from src.ingestion.pdf_loader import load_pdf
from src.ingestion.chunker import chunk_pages
from src.retrieval.hybrid_search import HybridRetriever as Retriever
from src.generation.generator import generate_answer

app = FastAPI(title="ScholarMind API", version="1.0.0")

retriever = Retriever()
uploaded_files = []
doc_metadata = []


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


@app.get("/health")
def health_check():
    return {"status": "healthy", "indexed_chunks": len(retriever.chunks)}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    os.makedirs("data/pdfs", exist_ok=True)
    file_path = f"data/pdfs/{file.filename}"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    pages, metadata = load_pdf(file_path)
    chunks = chunk_pages(pages)

    for chunk in chunks:
        chunk["source"] = file.filename

    all_chunks = retriever.chunks + chunks
    count = retriever.build_index(all_chunks)

    uploaded_files.append(file.filename)
    doc_metadata.append(metadata)

    return {
        "message": f"Successfully processed {file.filename}",
        "title": metadata["title"],
        "pages": len(pages),
        "chunks": len(chunks),
        "total_indexed": count
    }


@app.post("/query")
def query_documents(request: QueryRequest):
    if len(retriever.chunks) == 0:
        return {"error": "No documents uploaded yet. Upload a PDF first."}

    results = retriever.search(request.question, top_k=request.top_k)
    
    # Add metadata context for metadata-type questions
    meta_context = ""
    for m in doc_metadata:
        meta_context += f"Document: {m['file_name']}, Title: {m['title']}, Pages: {m['total_pages']}\n"
    
    response = generate_answer(request.question, results, meta_context=meta_context)

    return {
        "question": response["query"],
        "answer": response["answer"],
        "sources": response["sources"],
        "uploaded_files": uploaded_files
    }


@app.get("/documents")
def list_documents():
    return {
        "uploaded_files": uploaded_files,
        "total_chunks": len(retriever.chunks)
    }
@app.post("/clear")
def clear_documents():
    retriever.chunks = []
    retriever.index = None
    uploaded_files.clear()
    return {"message": "All documents cleared", "total_chunks": 0}