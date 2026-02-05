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


def check_ollama_availability(config: Optional[OllamaConfig] = None) -> tuple[bool, str]:
    """
    Check if Ollama is running and has available models.
    
    Returns:
        tuple: (is_available: bool, message: str)
    """
    config = config or load_ollama_config()
    
    try:
        # Test connection to Ollama
        url = config.base_url.rstrip("/") + "/api/tags"
        req = url_request.Request(url, headers={"Accept": "application/json"})
        
        with url_request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body)
            
        models = data.get("models", [])
        if not models:
            return False, "Ollama est lancé mais aucun modèle n'est disponible"
            
        # Check if configured model is available
        model_names = [m.get("name", "") for m in models if m.get("name")]
        if config.model not in model_names:
            # Also check if model name without tag matches (e.g., "mistral" matches "mistral:latest")
            base_model_name = config.model.split(':')[0]
            matching_models = [name for name in model_names if name.startswith(base_model_name)]
            
            if not matching_models:
                available_models = ", ".join(model_names[:3])
                return False, f"Modèle '{config.model}' non trouvé. Modèles disponibles: {available_models}"
            
        return True, "Ollama est disponible"
        
    except url_error.HTTPError as exc:
        return False, f"Erreur HTTP Ollama: {exc.code}"
    except url_error.URLError:
        return False, f"Impossible de se connecter à Ollama sur {config.base_url}"
    except json.JSONDecodeError:
        return False, "Réponse invalide d'Ollama"
    except Exception as e:
        return False, f"Erreur inconnue: {str(e)}"


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
