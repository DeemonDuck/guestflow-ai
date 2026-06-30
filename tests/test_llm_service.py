import llm_service
from config import LLM_FALLBACK_MESSAGE


class _FakeResp:
    def __init__(self, content):
        self.content = content


class _FakeLLM:
    def __init__(self, content=None, exc=None):
        self._content = content
        self._exc = exc

    def invoke(self, prompt):
        if self._exc:
            raise self._exc
        return _FakeResp(self._content)


def test_returns_model_content_on_success(monkeypatch):
    monkeypatch.setattr(llm_service, "llm", _FakeLLM(content="hello guest"))
    assert llm_service.generate_guest_response("hi") == "hello guest"


def test_falls_back_when_model_unavailable(monkeypatch):
    monkeypatch.setattr(llm_service, "llm", _FakeLLM(exc=ConnectionError("ollama is down")))
    # Must not raise — returns the safe fallback message instead
    assert llm_service.generate_guest_response("hi") == LLM_FALLBACK_MESSAGE
