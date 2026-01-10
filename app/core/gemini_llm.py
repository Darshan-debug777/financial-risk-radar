"""
Simple Gemini (LLM) client wrapper.

Provides:
 - init(api_key) to configure client
 - summarize_transactions(transactions) -> str: produce short highlights

Uses the official google.generativeai client when available, otherwise falls back to an HTTP endpoint specified by GENAI_HTTP_ENDPOINT.
"""

import os
from typing import List, Dict, Any

try:
    import google.generativeai as genai
    _HAS_GENAI = True
except Exception:
    import requests
    _HAS_GENAI = False

API_KEY = os.getenv("GEMINI_API_KEY", "")


def init_api(api_key: str = None):
    """Initialize the client (call at app startup)."""
    global API_KEY
    API_KEY = api_key or API_KEY
    if _HAS_GENAI and API_KEY:
        try:
            genai.configure(api_key=API_KEY)
        except Exception:
            pass


def _make_prompt(transactions: List[Dict[str, Any]]) -> str:
    examples = []
    for t in transactions[:30]:
        date = t.get("date", "")
        desc = t.get("description", "")
        amount = t.get("amount", "")
        ttype = t.get("type", "")
        examples.append(f"{date} | {desc} | {ttype} | {amount}")
    body = "\n".join(examples)
    prompt = (
        "You are a financial assistant. Given the following recent transactions (date | description | type | amount),\n"
        "produce a short bullet list of up to 6 highlights. Include any high-value or suspicious transactions,\n"
        "top spending categories, and one recommendation to mitigate financial risks.\n\n"
        f"Transactions:\n{body}\n\n"
        "Return the answer as a plain text bullet list."
    )
    return prompt


def summarize_transactions(transactions: List[Dict[str, Any]], model: str = "models/text-bison-001") -> str:
    """Summarize transactions using Gemini/Generative API. Returns plain text highlights."""
    if not API_KEY:
        raise RuntimeError("GEMINI_API_KEY not configured")

    prompt = _make_prompt(transactions)

    if _HAS_GENAI:
        try:
            response = genai.generate_text(model=model, prompt=prompt, temperature=0.2, max_output_tokens=512)
            return getattr(response, "text", str(response))
        except Exception as e:
            raise RuntimeError(f"LLM request failed: {e}")
    else:
        endpoint = os.getenv("GENAI_HTTP_ENDPOINT")
        if not endpoint:
            raise RuntimeError("No LLM client available and GENAI_HTTP_ENDPOINT not set")
        resp = requests.post(endpoint, json={"prompt": prompt, "max_tokens": 512}, headers={"Authorization": f"Bearer {API_KEY}"})
        resp.raise_for_status()
        data = resp.json()
        return data.get("text") or data.get("output") or str(data)