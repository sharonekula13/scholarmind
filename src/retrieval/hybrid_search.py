from rank_bm25 import BM25Okapi
import numpy as np
from src.retrieval.embedder import create_embedder
from src.retrieval.vector_store import create_vector_store, search_vector_store


class HybridRetriever:
    def __init__(self):
        self.model = create_embedder()
        self.index = None
        self.chunks = []
        self.bm25 = None

    def build_index(self, chunks):
        self.chunks = chunks
        texts = [chunk["text"] for chunk in chunks]

        # Build semantic index (FAISS)
        embeddings = self.model.encode(texts, show_progress_bar=True)
        self.index = create_vector_store(embeddings)

        # Build BM25 keyword index
        tokenized = [text.lower().split() for text in texts]
        self.bm25 = BM25Okapi(tokenized)

        return len(chunks)

    def search(self, query, top_k=5, semantic_weight=0.3):
        if self.index is None or self.bm25 is None:
            raise ValueError("No index built yet. Call build_index first.")

        # Semantic search scores
        query_embedding = self.model.encode([query])[0]
        distances, indices = search_vector_store(self.index, query_embedding, top_k=len(self.chunks))

        max_dist = max(distances) if max(distances) > 0 else 1
        semantic_scores = np.array([1 - (d / max_dist) for d in distances])

        # BM25 keyword scores
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)

        max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1
        bm25_scores = bm25_scores / max_bm25

        # Combine scores
        combined_scores = []
        for i in range(len(self.chunks)):
            sem_score = semantic_scores[i] if i < len(semantic_scores) else 0
            bm25_score = bm25_scores[i] if i < len(bm25_scores) else 0
            combined = (semantic_weight * sem_score) + ((1 - semantic_weight) * bm25_score)
            combined_scores.append((i, combined))

        # Sort by combined score (highest first)
        combined_scores.sort(key=lambda x: x[1], reverse=True)

        # Return top_k results
        results = []
        for idx, score in combined_scores[:top_k]:
            results.append({
                "text": self.chunks[idx]["text"],
                "page_number": self.chunks[idx]["page_number"],
                "chunk_index": self.chunks[idx]["chunk_index"],
                "score": float(score)
            })

        return results