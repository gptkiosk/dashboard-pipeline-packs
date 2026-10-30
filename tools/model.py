"""One call to a model through OpenRouter's chat completions API, for the store's label-gated gates (rehearsal and model review).

The key comes from OPENROUTER_API_KEY and is sent only to openrouter.ai. Standard library only, so the gates add no dependency.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"


class ModelError(RuntimeError):
    pass


def ask(model: str, prompt: str, max_tokens: int, system: str | None = None, timeout: int = 300) -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        raise ModelError("OPENROUTER_API_KEY is not set.")
    if not model:
        raise ModelError("No model is configured.")
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    request = urllib.request.Request(ENDPOINT, method="POST", data=json.dumps({"model": model, "messages": messages, "max_tokens": max_tokens}).encode(),
                                     headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                              "X-Title": "dashboard template store"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:      # noqa: S310 - fixed https endpoint
            body = json.loads(response.read(4_000_000))
    except urllib.error.HTTPError as exc:
        raise ModelError(f"The model service answered {exc.code}.") from None
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise ModelError(f"The model service could not be reached ({type(exc).__name__}).") from None
    try:
        return body["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError):
        raise ModelError("The model service returned no answer.") from None
