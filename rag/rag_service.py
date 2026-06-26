import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

_client = chromadb.Client()
_embed_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
_collection = _client.get_or_create_collection("hotel_faq", embedding_function=_embed_fn)

# Load FAQ into ChromaDB on first use
def _load_faq():
    if _collection.count() > 0:
        return
    with open("rag/hotel_faq.txt", "r") as f:
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
