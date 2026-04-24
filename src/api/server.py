from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import shutil
import os

from src.ingestion.pdf_loader import load_pdf
from src.ingestion.chunker import chunk_pages
from src.retrieval.retriever import Retriever
from src.generation.generator import generate_answer

app = FastAPI(title="ScholarMind API", version="1.0.0")

retriever = Retriever()
uploaded_files = []


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

    pages = load_pdf(file_path)
    chunks = chunk_pages(pages)

    for chunk in chunks:
        chunk["source"] = file.filename

    all_chunks = retriever.chunks + chunks
    count = retriever.build_index(all_chunks)

    uploaded_files.append(file.filename)

    return {
        "message": f"Successfully processed {file.filename}",
        "pages": len(pages),
        "chunks": len(chunks),
        "total_indexed": count
    }


@app.post("/query")
def query_documents(request: QueryRequest):
    if len(retriever.chunks) == 0:
        return {"error": "No documents uploaded yet. Upload a PDF first."}

    results = retriever.search(request.question, top_k=request.top_k)
    response = generate_answer(request.question, results)

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