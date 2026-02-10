"""Global configuration utilities for the project."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class OllamaConfig:
    base_url: str
    model: str
    timeout: float

    def validate(self) -> "OllamaConfig":
        if not self.base_url.strip():
            raise ValueError("OLLAMA_BASE_URL must be set")
        if self.timeout <= 0:
            raise ValueError("OLLAMA_TIMEOUT must be > 0")
        if not self.model.strip():
            raise ValueError("OLLAMA_MODEL must be set")
        return self


def load_ollama_config() -> OllamaConfig:
    """Load Ollama configuration from environment variables with defaults."""
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "mistral")
    timeout_str = os.getenv("OLLAMA_TIMEOUT", "180")

    try:
        timeout = float(timeout_str)
    except ValueError as exc:
        raise ValueError("OLLAMA_TIMEOUT must be a number") from exc

    return OllamaConfig(base_url=base_url, model=model, timeout=timeout).validate()
