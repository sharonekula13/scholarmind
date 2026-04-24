import fitz
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
    
    # Extract metadata from first page
    metadata = {
        "title": pages[0]["text"].split("\n")[0].strip() if pages else "Unknown",
        "total_pages": len(pages),
        "file_name": os.path.basename(file_path)
    }
    
    doc.close()
    return pages, metadata