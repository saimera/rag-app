import os

import requests
from dotenv import load_dotenv

load_dotenv()

response = requests.post(
    "https://api.jina.ai/v1/embeddings",
    headers={"Authorization": f"Bearer {os.getenv('JINA_API_KEY')}"},
     json={
        "model": "jina-embeddings-v5-text-nano",
        "task": "retrieval.query",
        "input": [{"text": "Hello world"}],
    },
)

print("Status:", response.status_code)

if response.status_code != 200:
    print(response.text)
else:
    vector = response.json()["data"][0]["embedding"]
    print("Vector length:", len(vector))
    print("First 5 numbers:", vector[:5])
