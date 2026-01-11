import os
import requests
import time
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_SECRET = os.getenv("GEMINI_API_SECRET")  # optional
GEMINI_API_URL = os.getenv("GEMINI_API_URL")  # e.g. https://api.gemini.example/v1/generate
DEFAULT_TIMEOUT = int(os.getenv("GEMINI_TIMEOUT", "15"))
RETRY_DELAY = float(os.getenv("GEMINI_RETRY_DELAY", "1.0"))
MAX_RETRIES = int(os.getenv("GEMINI_MAX_RETRIES", "2"))


class GeminiError(Exception):
    pass


def _parse_response_for_text(resp_json: dict) -> str:
    """
    Try common response shapes and return human text output.
    This keeps the client generic so you can plug any LLM/Gemini-like endpoint.
    """
    # Common shapes:
    # { "text": "..." }
    if isinstance(resp_json, dict):
        if "text" in resp_json and isinstance(resp_json["text"], str):
            return resp_json["text"].strip()
        # e.g., { "output": "..." }
        if "output" in resp_json and isinstance(resp_json["output"], str):
            return resp_json["output"].strip()
        # e.g., { "choices": [{"text": "..."}] }
        if "choices" in resp_json and isinstance(resp_json["choices"], list):
            first = resp_json["choices"][0]
            if isinstance(first, dict) and "text" in first:
                return first["text"].strip()
        # nested common: { "result": {"content": "..." } }
        if "result" in resp_json and isinstance(resp_json["result"], dict):
            for key in ("content", "text", "output"):
                if key in resp_json["result"]:
                    return str(resp_json["result"][key]).strip()
    # fallback: stringify
    return str(resp_json)


def generate_text(prompt: str,
                  model: Optional[str] = None,
                  max_tokens: int = 256,
                  timeout: Optional[int] = None) -> str:
    """
    Generic wrapper to call a Gemini-like HTTP endpoint.
    Must set GEMINI_API_URL and GEMINI_API_KEY in environment variables.

    The function returns a text string (or raises GeminiError on failure).

    NOTE: Adjust headers/payload to match the real API you will call.
    """
    if not GEMINI_API_URL:
        raise GeminiError("GEMINI_API_URL not set in environment")
    if not GEMINI_API_KEY:
        raise GeminiError("GEMINI_API_KEY not set in environment")

    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens,
    }
    if model:
        payload["model"] = model

    t_out = timeout or DEFAULT_TIMEOUT

    last_exc = None
    for attempt in range(0, MAX_RETRIES + 1):
        try:
            resp = requests.post(GEMINI_API_URL, json=payload, headers=headers, timeout=t_out)
            resp.raise_for_status()
            resp_json = resp.json()
            return _parse_response_for_text(resp_json)
        except Exception as e:
            last_exc = e
            # simple backoff
            time.sleep(RETRY_DELAY * (1 + attempt))
            continue

    raise GeminiError(f"Failed to call Gemini API after retries: {last_exc}")
