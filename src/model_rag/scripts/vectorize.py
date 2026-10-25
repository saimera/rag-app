from sqlalchemy import select

from ..db.chroma import get_collection
from ..db.models import Chunks
from ..db.session import SessionLocal
from ..services.embedding import embed_texts

BATCH_SIZE = 32


def vectorize_chunks():
    collection = get_collection()

    with SessionLocal() as session:
        chunks = session.scalars(
            select(Chunks).where(Chunks.status == "ready_to_vectorize")
        ).all()
        print(f"Chunks to vectorize: {len(chunks)}")

        for start in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[start : start + BATCH_SIZE]
            vectors = embed_texts([c.text for c in batch])

            collection.upsert(
                ids=[str(c.id) for c in batch],
                embeddings=vectors,
                metadatas=[
                    {"document_id": str(c.document_id), "page_no": c.page_no}
                    for c in batch
                ],
            )

            for c in batch:
                c.status = "vectorized"
            session.commit()

            print(f"Done {min(start + BATCH_SIZE, len(chunks))}/{len(chunks)}")


if __name__ == "__main__":
    vectorize_chunks()