from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import uuid

client = QdrantClient("localhost", port=6333)

model = SentenceTransformer("all-MiniLM-L6-v2")

# Collections

client.recreate_collection(
    collection_name="guest_memory",
    vectors_config=VectorParams(
        size=384,
        distance=Distance.COSINE
    )
)

# Memory STorage Function
def store_memory(user_id, text):
    embedding = model.encode(text).tolist()

    client.upsert(
        collection_name="guest_memory",
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "user_id": user_id,
                    "memory": text
                }
            )
        ]
    )

    print("Memory stored successfully!")

# Retrieval Function

def retrieve_memory(query):
    embedding = model.encode(query).tolist()

    results = client.query_points(
        collection_name="guest_memory",
        query=embedding,
        limit=3
    )

    return results

