"""gem.py - talks to the class proxy using direct HTTP calls."""
import time

import requests
import config


_session = requests.Session()


def _post_json(url: str, body: dict, timeout: int = 60, retries: int = 6):
    headers = {
        "Authorization": f"Bearer {config.GEMINI_API_KEY}",
        "Content-Type": "application/json",
    }
    delay = 2.0
    last_error = None

    for attempt in range(retries):
        try:
            response = _session.post(url, headers=headers, json=body, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as exc:
            last_error = exc
            status = getattr(exc.response, "status_code", None)
            if status == 429 and attempt < retries - 1:
                time.sleep(delay)
                delay = min(delay * 2, 30.0)
                continue
            raise
        except requests.RequestException as exc:
            last_error = exc
            if attempt < retries - 1:
                time.sleep(delay)
                delay = min(delay * 2, 30.0)
                continue
            raise

    raise last_error


def chat(prompt: str) -> str:
    url = "https://saidazam-litellm-proxy.hf.space/v1/chat/completions"
    body = {
        "model": config.CHAT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }
    data = _post_json(url, body)
    return data["choices"][0]["message"]["content"].strip()


def embed(text: str):
    url = "https://saidazam-litellm-proxy.hf.space/v1/embeddings"
    body = {
        "model": config.EMBED_MODEL,
        "input": text,
    }
    data = _post_json(url, body)
    return data["data"][0]["embedding"]
