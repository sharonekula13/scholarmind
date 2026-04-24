from src.retrieval.embedder import create_embedder, embed_chunks
from src.retrieval.vector_store import create_vector_store, search_vector_store


class Retriever:
    def __init__(self):
        self.model = create_embedder()
        self.index = None
        self.chunks = []

    def build_index(self, chunks):
        self.chunks = chunks
        embeddings = embed_chunks(chunks, self.model)
        self.index = create_vector_store(embeddings)
        return len(chunks)

    def search(self, query, top_k=5):
        if self.index is None:
            raise ValueError("No index built yet. Call build_index first.")
        query_embedding = self.model.encode([query])[0]
        distances, indices = search_vector_store(self.index, query_embedding, top_k)
        results = []
        for i, idx in enumerate(indices):
            if idx < len(self.chunks):
                results.append({
                    "text": self.chunks[idx]["text"],
                    "page_number": self.chunks[idx]["page_number"],
                    "chunk_index": self.chunks[idx]["chunk_index"],
                    "distance": float(distances[i])
                })
        return results