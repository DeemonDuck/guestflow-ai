import os

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# Paths resolved relative to this file so they work regardless of the current
# working directory (and match the real filename casing on case-sensitive OSes).
_HERE = os.path.dirname(os.path.abspath(__file__))
_FAQ_PATH = os.path.join(_HERE, "hotel_FAQ.txt")
_STORAGE_PATH = os.path.join(_HERE, "chroma_storage")

# Persist embeddings to disk so the FAQ is not re-embedded on every startup
_client = chromadb.PersistentClient(path=_STORAGE_PATH)
_embed_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
_collection = _client.get_or_create_collection(
    "hotel_faq",
    embedding_function=_embed_fn
)


def _load_faq():
    # Already populated (persisted from a previous run) -> nothing to do
    if _collection.count() > 0:
        return
    with open(_FAQ_PATH, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    _collection.add(
        documents=lines,
        ids=[str(i) for i in range(len(lines))]
    )


def retrieve_faq(query: str) -> str:
    _load_faq()
    results = _collection.query(query_texts=[query], n_results=1)
    docs = results.get("documents", [[]])[0]
    return docs[0] if docs else "Sorry, no relevant hotel information found."
