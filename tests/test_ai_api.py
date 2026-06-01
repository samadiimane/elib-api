from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app.main import app


class _FakeRagResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return None

    def read(self) -> bytes:
        return json.dumps(
            {
                "answer_markdown": "Mocked answer",
                "sources": [{"title": "Source 1"}],
            }
        ).encode("utf-8")


def test_ai_chat_proxies_public_request(monkeypatch) -> None:
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return _FakeRagResponse()

    monkeypatch.setattr("app.api.routes.ai.urlopen", fake_urlopen)

    client = TestClient(app)
    response = client.post(
        "/v1/ai/chat",
        json={"question": "What is in the library?", "lang": "EN", "access": "admin"},
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        "answer_markdown": "Mocked answer",
        "sources": [{"title": "Source 1"}],
    }
    assert captured == {
        "url": "http://rag-api:8001/chat",
        "timeout": 60,
        "body": {
            "question": "What is in the library?",
            "lang": "EN",
            "access": "public",
        },
    }
