import os

import requests
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

EMBED_URL = os.environ["EMBED_NGROK_URL"]
qdrant = QdrantClient(host="localhost", port=6333)

qdrant.recreate_collection(
    collection_name="documents",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)


def embed_and_store(records: list[dict]):
    response = requests.post(
        f"{EMBED_URL}/embed",
        headers={"ngrok-skip-browser-warning": "true"},
        json={"texts": [record["text"] for record in records]},
        timeout=30,
    )
    response.raise_for_status()
    embeddings = response.json()["embeddings"]

    points = [
        PointStruct(id=index, vector=embedding, payload=record)
        for index, (embedding, record) in enumerate(zip(embeddings, records))
    ]
    qdrant.upsert(collection_name="documents", points=points)
    print(f"Integration 5 OK: {len(points)} vectors stored in Qdrant")


embed_and_store(
    [
        {"id": "doc_001", "text": "AI platform integration test"},
        {"id": "doc_002", "text": "Kafka to Airflow pipeline"},
    ]
)
