# app/llm.py
import os
import requests
import time
from typing import List, Dict, Any, Optional

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "mistralai/mistral-7b-instruct"

def _get_api_key() -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY not set. Set it as an environment variable (do NOT commit it)."
        )
    return api_key

def _parse_openrouter_response(resp_json: Dict[str, Any]) -> Optional[str]:
    """
    Parse typical OpenRouter-like chat response shapes robustly.
    """
    # common shape: {"choices":[{"message":{"role":"assistant","content":"..."}}, ...], ...}
    try:
        choices = resp_json.get("choices") or []
        if choices:
            first = choices[0]
            if isinstance(first, dict):
                msg = first.get("message") or {}
                if isinstance(msg, dict) and "content" in msg:
                    return msg["content"]
                # fallback: maybe direct 'text' or 'content'
                if "text" in first:
                    return first["text"]
                if "content" in first:
                    return first["content"]
    except Exception:
        pass
    # last resort: look for top-level 'result' or 'data'
    return None

def call_openrouter_chat(
    messages: List[Dict[str, str]],
    model: str = DEFAULT_MODEL,
    max_tokens: int = 512,
    timeout: int = 15,
    retries: int = 2,
    backoff: float = 1.0,
) -> Dict[str, Any]:
    """
    Call OpenRouter chat completions endpoint.

    messages: List[{"role": "system"/"user"/"assistant", "content": "..."}]
    Returns a dict: {"ok": True, "content": "<assistant text>"} on success,
    or {"ok": False, "error": "...", "code": <http_code or 'rate_limit'>}.
    """
    api_key = _get_api_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "StudentCareerChatbot",
    }

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }

    attempt = 0
    while attempt <= retries:
        try:
            resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=timeout)
        except requests.Timeout:
            attempt += 1
            if attempt > retries:
                return {"ok": False, "error": "timeout", "code": "timeout"}
            time.sleep(backoff * attempt)
            continue
        except requests.RequestException as e:
            return {"ok": False, "error": f"request_exception: {str(e)}", "code": "request_exception"}

        # handle HTTP status
        if resp.status_code == 200:
            try:
                data = resp.json()
            except ValueError:
                return {"ok": False, "error": "invalid_json", "code": resp.status_code}
            parsed = _parse_openrouter_response(data)
            if parsed is not None:
                return {"ok": True, "content": parsed, "raw": data}
            else:
                return {"ok": False, "error": "unparsed_response", "raw": data, "code": resp.status_code}

        # rate limiting
        if resp.status_code in (429, 503):
            # give a friendly code indicating rate limit/backpressure
            attempt += 1
            if attempt > retries:
                return {"ok": False, "error": "rate_limited", "code": resp.status_code}
            # exponential backoff
            time.sleep(backoff * (2 ** (attempt - 1)))
            continue

        # other errors
        try:
            err = resp.json()
        except ValueError:
            err = resp.text
        return {"ok": False, "error": "http_error", "detail": err, "code": resp.status_code}

    return {"ok": False, "error": "unknown_failure"}
