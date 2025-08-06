"""Utility to analyze scanner results using ChatGPT if available."""

import json
import os
from typing import Dict, List


def analyze_result(result: Dict) -> Dict:
    """Return analysis summary and tags. Uses OpenAI API if configured."""
    try:
        import openai  # type: ignore
    except Exception:
        return {"summary": "ChatGPT unavailable", "tags": []}

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"summary": "OPENAI_API_KEY not set", "tags": []}

    openai.api_key = api_key
    prompt = (
        "Summarize the following vulnerability scan result and suggest up to 3 short tags:\n"
        + json.dumps(result)
    )
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
        )
        text = resp["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return {"summary": f"analysis failed: {e}", "tags": []}

    lines = text.splitlines()
    summary = lines[0] if lines else text
    tags: List[str] = []
    if len(lines) > 1:
        tags = [t.strip() for t in lines[1].split()] if lines[1] else []
    return {"summary": summary, "tags": tags}
