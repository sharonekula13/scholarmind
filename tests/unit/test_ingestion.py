import pytest
import os
from src.ingestion.pdf_loader import load_pdf
from src.ingestion.chunker import chunk_pages


class TestPDFLoader:
    def test_load_valid_pdf(self):
        if not os.path.exists("data/pdfs/test.pdf"):
            pytest.skip("No test PDF available")
        pages, metadata = load_pdf("data/pdfs/test.pdf")
        assert len(pages) > 0
        assert "text" in pages[0]
        assert "page_number" in pages[0]

    def test_load_nonexistent_pdf(self):
        with pytest.raises(FileNotFoundError):
            load_pdf("data/pdfs/nonexistent.pdf")

    def test_metadata_extraction(self):
        if not os.path.exists("data/pdfs/test.pdf"):
            pytest.skip("No test PDF available")
        pages, metadata = load_pdf("data/pdfs/test.pdf")
        assert "title" in metadata
        assert "total_pages" in metadata
        assert "file_name" in metadata
        assert metadata["total_pages"] > 0


class TestChunker:
    def test_chunk_pages(self):
        if not os.path.exists("data/pdfs/test.pdf"):
            pytest.skip("No test PDF available")
        pages, metadata = load_pdf("data/pdfs/test.pdf")
        chunks = chunk_pages(pages)
        assert len(chunks) > len(pages)
        assert "text" in chunks[0]
        assert "page_number" in chunks[0]
        assert "chunk_index" in chunks[0]

    def test_chunk_size(self):
        if not os.path.exists("data/pdfs/test.pdf"):
            pytest.skip("No test PDF available")
        pages, metadata = load_pdf("data/pdfs/test.pdf")
        chunks = chunk_pages(pages, chunk_size=200)
        for chunk in chunks:
            assert len(chunk["text"]) <= 250

    def test_empty_input(self):
        chunks = chunk_pages([])
        assert chunks == []
