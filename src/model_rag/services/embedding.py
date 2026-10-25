import os

import requests
from dotenv import load_dotenv

load_dotenv()

JINA_URL = "https://api.jina.ai/v1/embeddings"
JINA_MODEL = "jina-embeddings-v5-text-nano"


def embed_texts(texts: list[str], task: str = "retrieval.passage") -> list[list[float]]:
    response = requests.post(
        JINA_URL,
        headers={"Authorization": f"Bearer {os.getenv('JINA_API_KEY')}"},
        json={
            "model": JINA_MODEL,
            "task": "retrieval.query",
            "input": [{"text": t} for t in texts],
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()["data"]
    return [item["embedding"] for item in data]


if __name__ == "__main__":
    vectors = embed_texts(["Hello world", "Claude Opus 5.5"])
    print("Vectors:", len(vectors), "| Length each:", len(vectors[0]))