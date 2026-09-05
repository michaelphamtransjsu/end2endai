import os
from pathlib import Path

from fastapi.testclient import TestClient

import app
from nano_llm import CharTokenizer, ModelConfig, NanoLM
from nano_llm.checkpoint import save_checkpoint


def test_tokenizer_round_trip():
    tokenizer = CharTokenizer.from_text("hello")
    assert tokenizer.decode(tokenizer.encode("hello")) == "hello"


def test_api_and_chat_smoke(tmp_path, monkeypatch):
    tokenizer = CharTokenizer.from_text("User: hello\nBot:")
    checkpoint = tmp_path / "model.pt"
    save_checkpoint(checkpoint, NanoLM(ModelConfig(tokenizer.vocab_size, 16, 1, 2, 16)), tokenizer)
    monkeypatch.setattr(app, "CHECKPOINT", str(checkpoint))
    client = TestClient(app.app)
    assert client.get("/health").json()["checkpoint"] == "ready"
    assert "Nano LLM Chat" in client.get("/").text
    response = client.post("/generate", json={"prompt": "User:", "max_new_tokens": 2})
    assert response.status_code == 200
    assert response.json()["text"].startswith("User:")
