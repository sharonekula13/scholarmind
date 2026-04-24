import ollama


def generate_answer(query, context_chunks, model_name="llama3.2"):
    context = ""
    for i, chunk in enumerate(context_chunks):
        context += f"\n[Source: Page {chunk['page_number']}]\n{chunk['text']}\n"

    prompt = f"""You are a helpful research assistant. Answer the question based ONLY on the provided context. 
If the context doesn't contain enough information to answer, say "I don't have enough information to answer this."
Always cite which page the information came from.

Context:
{context}

Question: {query}

Answer:"""

    response = ollama.chat(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response["message"]["content"]

    sources = []
    for chunk in context_chunks:
        page = chunk["page_number"]
        if page not in sources:
            sources.append(page)

    return {
        "answer": answer,
        "sources": sources,
        "query": query
    }