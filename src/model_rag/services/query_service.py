import re
import uuid

from sqlalchemy import select

from ..db.models import Chunks, Document
from ..db.session import SessionLocal

from ..db.chroma import get_collection
from .embedding import embed_texts
from .llm import generate


TOP_K = 5


def search_chunk_ids(query: str, top_k: int = TOP_K):
    query_vector = embed_texts([query], task="retrieval.query")[0]

    collection = get_collection()
    result = collection.query(query_embeddings=[query_vector], n_results=top_k)

    return [
        {"id": id_, "distance": distance, "page_no": meta["page_no"]}
        for id_, distance, meta in zip(
            result["ids"][0], result["distances"][0], result["metadatas"][0]
        )
    ]

def fetch_chunks(hits):
    ids = [uuid.UUID(h["id"]) for h in hits]

    with SessionLocal() as session:
        rows = session.execute(
            select(Chunks, Document)
            .join(Document, Chunks.document_id == Document.id)
            .where(Chunks.id.in_(ids))
        ).all()

        by_id = {str(chunk.id): (chunk, doc) for chunk, doc in rows}

        results = []
        for hit in hits:
            chunk, doc = by_id[hit["id"]]
            results.append(
                {
                    "text": chunk.text,
                    "page_no": chunk.page_no,
                    "title": doc.title,
                    "source_url": doc.source_url,
                    "distance": hit["distance"],
                }
            )
    return results

SYSTEM_PROMPT = """You are an assistant that answers questions about documents.
Answer ONLY using the sources provided below.
If the sources do not contain the answer, say that you could not find it in the documents.
After each claim, cite the source number in square brackets, like [1] or [2]."""

def build_prompt(query: str, chunks: list[dict]) -> str:
    sources = "\n\n".join(
        f"[{i}] (page {c['page_no']})\n{c['text']}" for i, c in enumerate(chunks, 1)
    )
    return f"{SYSTEM_PROMPT}\n\nSources:\n{sources}\n\nQuestion: {query}\n\nAnswer:"

 
def answer_question(query: str):
    hits = search_chunk_ids(query)
    chunks = fetch_chunks(hits)
    answer = generate(build_prompt(query, chunks))
    return answer, chunks


def get_cited_chunks(answer: str, chunks: list[dict]):
    numbers = set()
    for group in re.findall(r"\[([\d,\s]+)\]", answer):
        for part in group.split(","):
            if part.strip().isdigit():
                numbers.add(int(part))
    return [(n, chunks[n - 1]) for n in sorted(numbers) if 1 <= n <= len(chunks)]

if __name__ == "__main__":
    query = "When was the Claude Opus 5.5 system card published?"
    answer, chunks = answer_question(query)

    print(answer)
    print("\nReferences:")
    for n, c in get_cited_chunks(answer, chunks):
        print(f"[{n}] {c['title']}, page {c['page_no']}: {c['source_url']}#page={c['page_no']}")
        