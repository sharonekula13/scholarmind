from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_pages(pages, chunk_size=500, chunk_overlap=50):
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = []

    for page in pages:
        page_chunks = text_splitter.split_text(page["text"])

        for i, chunk_text in enumerate(page_chunks):
            chunks.append({
                "text": chunk_text,
                "page_number": page["page_number"],
                "chunk_index": i
            })

    return chunks