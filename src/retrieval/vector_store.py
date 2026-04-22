import faiss
import numpy as np


def create_vector_store(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype("float32"))
    return index


def search_vector_store(index, query_embedding, top_k=5):
    query_vector = np.array([query_embedding]).astype("float32")
    distances, indices = index.search(query_vector, top_k)
    return distances[0], indices[0]