import fitz #library is pymupdf but its import name is fitz
import os

def load_pdf(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF not found: {file_path}")
    doc = fitz.open(file_path)
    pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        if text.strip():
            pages.append({
                "page_number": page_num + 1,
                "text": text.strip()
            })
    doc.close()
    return pages