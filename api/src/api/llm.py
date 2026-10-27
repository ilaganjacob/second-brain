"""The provider interface. The parser only knows about LLMProvider, so swapping
OpenRouter for another service touches nothing outside this file."""

import json
from typing import Any, Protocol

import httpx

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class LLMError(Exception):
    """The provider failed or returned something that isn't JSON."""


class LLMProvider(Protocol):
    def complete_json(
        self, system: str, user: str, schema: dict[str, Any], schema_name: str
    ) -> dict[str, Any]: ...


class OpenRouterProvider:
    def __init__(self, api_key: str, model: str, timeout: float = 30.0):
        if not api_key:
            raise LLMError("OPENROUTER_API_KEY is not set")
        self.model = model
        self._client = httpx.Client(
            timeout=timeout, headers={"Authorization": f"Bearer {api_key}"}
        )

    def complete_json(self, system, user, schema, schema_name):
        body = {
            "model": self.model,
            # No temperature: current models don't accept it, and with
            # require_parameters an unsupported parameter means no host at all.
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": schema_name, "strict": True, "schema": schema},
            },
            "provider": {
                # Only route to hosts that honour response_format...
                "require_parameters": True,
                # ...and that don't keep or train on what you log.
                "data_collection": "deny",
            },
        }
        try:
            response = self._client.post(OPENROUTER_URL, json=body)
            if response.is_error:
                raise LLMError(f"{self.model}: {response.status_code} {response.text[:300]}")
            content = response.json()["choices"][0]["message"]["content"]
            return json.loads(content)
        except (httpx.HTTPError, KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise LLMError(f"{self.model}: {exc}") from exc


class FakeProvider:
    """Returns canned replies in order, and records what it was asked."""

    def __init__(self, *replies: dict[str, Any] | Exception):
        self.replies = list(replies)
        self.calls: list[dict[str, Any]] = []

    def complete_json(self, system, user, schema, schema_name):
        self.calls.append({"system": system, "user": user, "schema": schema})
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply
