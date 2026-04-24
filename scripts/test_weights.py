from src.ingestion.pdf_loader import load_pdf
from src.ingestion.chunker import chunk_pages
from src.retrieval.hybrid_search import HybridRetriever
import json

pages, metadata = load_pdf("data/pdfs/test.pdf")
chunks = chunk_pages(pages)

retriever = HybridRetriever()
retriever.build_index(chunks)

with open("data/evaluation/test_cases.json", "r") as f:
    test_cases = json.load(f)

for weight in [0.3, 0.5, 0.7]:
    print(f"\n--- Semantic Weight: {weight} ---")
    recall_hits = 0
    mrr_sum = 0
    for case in test_cases:
        results = retriever.search(case["question"], top_k=5, semantic_weight=weight)
        pages_found = [r["page_number"] for r in results]
        if case["expected_page"] in pages_found:
            recall_hits += 1
            rank = pages_found.index(case["expected_page"]) + 1
            mrr_sum += 1.0 / rank
    recall = recall_hits / len(test_cases)
    mrr = mrr_sum / len(test_cases)
    print(f"Recall@5: {recall:.2%}")
    print(f"MRR: {mrr:.2%}")