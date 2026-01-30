from __future__ import annotations

import json
from types import SimpleNamespace
from urllib import error as url_error

import pytest

from ai.ollama_client import OllamaClient
from config import OllamaConfig


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_generate_success(monkeypatch):
    def _fake_urlopen(req, timeout=None):
        return _FakeResponse({"response": "ok"})

    monkeypatch.setattr("urllib.request.urlopen", _fake_urlopen)

    cfg = OllamaConfig(base_url="http://localhost:11434", model="mistral", timeout=5)
    client = OllamaClient(cfg)
    result = client.generate("hello")

    assert result.response == "ok"
    assert result.raw["response"] == "ok"


def test_list_models_success(monkeypatch):
    def _fake_urlopen(req, timeout=None):
        return _FakeResponse({"models": [{"name": "mistral"}, {"name": "llama3"}]})

    monkeypatch.setattr("urllib.request.urlopen", _fake_urlopen)

    cfg = OllamaConfig(base_url="http://localhost:11434", model="mistral", timeout=5)
    client = OllamaClient(cfg)

    assert client.list_models() == ["mistral", "llama3"]


def test_connection_error(monkeypatch):
    def _fake_urlopen(req, timeout=None):
        raise url_error.URLError("boom")

    monkeypatch.setattr("urllib.request.urlopen", _fake_urlopen)

    cfg = OllamaConfig(base_url="http://localhost:11434", model="mistral", timeout=5)
    client = OllamaClient(cfg)

    with pytest.raises(ConnectionError):
        client.generate("hello")
