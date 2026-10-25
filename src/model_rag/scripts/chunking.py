import os
import uuid

from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..db.models import Chunks, Document
from ..db.session import SessionLocal
from .document_loader import load_pdf

PDF_PATH = "Claude Opus 5.5 System Card.pdf"
TITLE = "Claude Opus 5.5 System Card"
SOURCE_URL = "https://www-cdn.anthropic.com/fc1b44717c85dc068bc6ba5024219938094694bd/Claude%20Opus%205.5%20System%20Card.pdf"

def chunk_documents(docs, chunk_size=1000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_documents(docs)

def chunk_and_store(pdf_path: str, title: str, source_url: str):
    docs = load_pdf(pdf_path)
    chunks = chunk_documents(docs)

    document = Document(
    id=uuid.uuid4(),
    title=title,
    file_name=os.path.basename(pdf_path),
    source_url=source_url,
    total_pages=len(docs),
    )
    rows = [
        Chunks(
        document_id=document.id,
        chunk_index=i,
        page_no=chunk.metadata["page"] + 1,
        text=chunk.page_content,
        status="ready_to_vectorize",
        )
        for i, chunk in enumerate(chunks)
    ]
    with SessionLocal() as session:
        session.add(document)
        session.flush() 
        session.add_all(rows)
        session.commit()
    print(f"Saved 1 document and {len(rows)} chunks")


if __name__ == "__main__":
    chunk_and_store(PDF_PATH, TITLE, SOURCE_URL)