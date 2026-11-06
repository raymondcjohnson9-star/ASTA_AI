"""Optional language-model adapter for ASTA_AI.

Supports a local Ollama server (no API key) and OpenAI-compatible chat
completion servers. No provider is contacted unless explicitly configured.
"""
from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class LanguageEngineError(RuntimeError):
    """Raised when a configured language model cannot answer."""


class LanguageEngine:
    def __init__(self, provider, base_url, model, api_key=None, timeout=45):
        self.provider = str(provider).strip().lower()
        self.base_url = str(base_url).rstrip("/")
        self.model = str(model).strip()
        self.api_key = api_key
        self.timeout = timeout
        if self.provider not in {"ollama", "openai"}:
            raise ValueError("provider must be 'ollama' or 'openai'")
        if not self.base_url or not self.model:
            raise ValueError("base_url and model are required")

    @classmethod
    def from_environment(cls):
        provider = os.getenv("ASTA_LLM_PROVIDER", "").strip().lower()
        if not provider:
            return None
        defaults = {
            "ollama": "http://127.0.0.1:11434",
            "openai": "https://api.openai.com",
        }
        base_url = os.getenv("ASTA_LLM_BASE_URL", defaults.get(provider, ""))
        model = os.getenv("ASTA_LLM_MODEL", "")
        api_key = os.getenv("ASTA_LLM_API_KEY") or None
        if provider == "openai" and not api_key:
            raise ValueError("ASTA_LLM_API_KEY is required for the hosted OpenAI-compatible provider")
        return cls(provider, base_url, model, api_key)

    def _post(self, url, payload):
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.provider == "openai" and self.api_key:
            headers["Authorization"] = "Bearer " + self.api_key
        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read(2_000_000)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise LanguageEngineError("The configured language model could not be reached.") from exc
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise LanguageEngineError("The language model returned an invalid response.") from exc

    def complete(self, messages):
        if not isinstance(messages, list) or not messages:
            raise ValueError("messages must be a non-empty list")
        if self.provider == "ollama":
            data = self._post(
                self.base_url + "/api/chat",
                {"model": self.model, "messages": messages, "stream": False},
            )
            answer = data.get("message", {}).get("content", "")
        else:
            data = self._post(
                self.base_url + "/v1/chat/completions",
                {"model": self.model, "messages": messages, "temperature": 0.4},
            )
            choices = data.get("choices") or []
            answer = choices[0].get("message", {}).get("content", "") if choices else ""
        if not isinstance(answer, str) or not answer.strip():
            raise LanguageEngineError("The language model returned an empty answer.")
        return answer.strip()
