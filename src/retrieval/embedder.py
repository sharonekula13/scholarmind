from sentence_transformers import SentenceTransformer


def create_embedder(model_name="all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    return model


def embed_chunks(chunks, model=None):
    if model is None:
        model = create_embedder()

    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    return embeddings