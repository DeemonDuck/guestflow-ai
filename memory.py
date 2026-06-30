from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import uuid

# Runs in-process, persists to disk — no separate Qdrant server needed
client = QdrantClient(path="./qdrant_storage")

model = SentenceTransformer("all-MiniLM-L6-v2")

COLLECTION = "guest_memory"

# Create collection only if it doesn't exist
existing = [c.name for c in client.get_collections().collections]
if COLLECTION not in existing:
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )


def store_memory(user_id: str, text: str):
    embedding = model.encode(text).tolist()
    client.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={"user_id": user_id, "memory": text}
            )
        ]
    )
    print("Memory stored successfully!")


def retrieve_memory(query: str):
    embedding = model.encode(query).tolist()
    return client.query_points(
        collection_name=COLLECTION,
        query=embedding,
        limit=3
    )
