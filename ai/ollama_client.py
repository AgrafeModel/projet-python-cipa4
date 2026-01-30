"""Minimal Ollama HTTP client (no external dependencies)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional
from urllib import error as url_error
from urllib import request as url_request

from config import OllamaConfig, load_ollama_config


@dataclass(frozen=True)
class OllamaResponse:
    response: str
    raw: dict[str, Any]


class OllamaClient:
    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or load_ollama_config()

    def generate(self, prompt: str, model: Optional[str] = None, options: Optional[dict[str, Any]] = None) -> OllamaResponse:
        payload: dict[str, Any] = {
            "model": model or self.config.model,
            "prompt": prompt,
            "stream": False,
        }
        if options:
            payload["options"] = options

        data = self._post_json("/api/generate", payload)
        return OllamaResponse(response=data.get("response", ""), raw=data)

    def list_models(self) -> list[str]:
        data = self._get_json("/api/tags")
        models = data.get("models", [])
        return [m.get("name", "") for m in models if m.get("name")]

    def _get_json(self, path: str) -> dict[str, Any]:
        url = self._build_url(path)
        req = url_request.Request(url, headers={"Accept": "application/json"})
        return self._read_json(req)

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = self._build_url(path)
        data = json.dumps(payload).encode("utf-8")
        req = url_request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        return self._read_json(req)

    def _build_url(self, path: str) -> str:
        return self.config.base_url.rstrip("/") + path

    def _read_json(self, req: url_request.Request) -> dict[str, Any]:
        try:
            with url_request.urlopen(req, timeout=self.config.timeout) as resp:
                body = resp.read().decode("utf-8")
        except url_error.HTTPError as exc:
            raise ConnectionError(f"Ollama HTTP error: {exc.code}") from exc
        except url_error.URLError as exc:
            raise ConnectionError("Ollama connection failed") from exc

        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON response from Ollama") from exc
