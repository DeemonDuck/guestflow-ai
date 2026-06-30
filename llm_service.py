"""LLM access with a graceful fallback.

Prefers the maintained `langchain-ollama` package, falling back to the older
`langchain_community` import if it isn't installed. If the model is unreachable
(e.g. Ollama isn't running), guest responses degrade to a safe fallback message
instead of crashing the whole workflow — the ticket and email still go through.
"""
try:  # maintained package (no deprecation warning)
    from langchain_ollama import ChatOllama
except ImportError:  # graceful fallback for older installs
    from langchain_community.chat_models import ChatOllama

from config import LLM_MODEL, LLM_TEMPERATURE, LLM_FALLBACK_MESSAGE

llm = ChatOllama(
    model=LLM_MODEL,
    temperature=LLM_TEMPERATURE,
)


def generate_guest_response(prompt):
    try:
        return llm.invoke(prompt).content
    except Exception as e:
        # Never let a model outage break the request path.
        print(f"LLM ERROR ({type(e).__name__}): {e}")
        return LLM_FALLBACK_MESSAGE
