import chromadb


CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "chunks"

client = chromadb.PersistentClient(path=CHROMA_PATH)

def get_collection():
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

if __name__ == "__main__":
    collection = get_collection()
    print("Collection:", collection.name)
    print("Items:", collection.count())

    result = collection.get(limit=3, include=["metadatas", "embeddings"])
    for i, id_ in enumerate(result["ids"]):
        print("\nID:", id_)
        print("Metadata:", result["metadatas"][i])
        print("Vector length:", len(result["embeddings"][i]))
        print("First 5 numbers:", result["embeddings"][i][:5])