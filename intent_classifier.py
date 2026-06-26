from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

_model = SentenceTransformer("all-MiniLM-L6-v2")

# Reference phrases per intent
_INTENTS = {
    "booking_confirmed": [
        "I made a booking",
        "I have a reservation",
        "I am checking in soon",
        "confirm my booking",
        "arriving at the hotel",
        "new reservation",
    ],
    "guest_request": [
        "I need help with something",
        "room service please",
        "I have a complaint",
        "wifi is not working",
        "I want a refund",
        "can I get late checkout",
        "there is an issue in my room",
    ],
    "checkout_complete": [
        "I have checked out",
        "I just left the hotel",
        "my stay is over",
        "I want to leave feedback",
        "please send my invoice",
        "I already checked out",
    ],
}

# Pre-compute reference embeddings once at import
_reference_embeddings = {
    intent: _model.encode(phrases)
    for intent, phrases in _INTENTS.items()
}


def classify_intent(text: str) -> str:
    query_embedding = _model.encode([text])

    best_intent = None
    best_score = -1

    for intent, ref_embeddings in _reference_embeddings.items():
        scores = cosine_similarity(query_embedding, ref_embeddings)
        score = float(np.max(scores))
        if score > best_score:
            best_score = score
            best_intent = intent

    return best_intent
