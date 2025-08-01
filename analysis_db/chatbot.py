"""Chatbot utility for answering questions about stored scan results."""

from __future__ import annotations

import json
import os
from typing import List, Dict

from .report_gen import load_results


def answer_question(question: str, results: List[Dict]) -> str:
    """Return an answer using ChatGPT if available."""
    try:
        import openai  # type: ignore
    except Exception:
        return "ChatGPT unavailable"

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "OPENAI_API_KEY not set"

    openai.api_key = api_key
    context = json.dumps(results, indent=2)
    prompt = (
        "You are ChainHunter, a cybersecurity assistant. "
        "Use the following scan results to answer the user's question.\n" + context +
        "\nQuestion: " + question
    )
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        return resp["choices"][0]["message"]["content"].strip()
    except Exception as e:  # pragma: no cover - network
        return f"failed: {e}"


def load_context(db_dir: str, limit: int = 5) -> List[Dict]:
    data = load_results(db_dir)
    if limit > 0:
        data = data[-limit:]
    return data


def recommend_pipeline(results: List[Dict]) -> str:
    """Return a recommended pipeline using ChatGPT if available."""
    try:
        import openai  # type: ignore
    except Exception:
        return "ChatGPT unavailable"

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "OPENAI_API_KEY not set"

    openai.api_key = api_key
    prompt = (
        "Given these scan results, recommend the best ChainHunter pipeline to run "
        "next.\nOptions: bug_hunt, extended_hunt, repo_hunt, smart_hunt.\n" +
        json.dumps(results)
    )
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
        )
        return resp["choices"][0]["message"]["content"].strip()
    except Exception as e:  # pragma: no cover - network
        return f"failed: {e}"


def explore_commands(doc: str, limit: int = 3) -> List[str]:
    """Return example commands for a module using ChatGPT if available."""
    try:
        import openai  # type: ignore
    except Exception:
        return ["ChatGPT unavailable"]

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return ["OPENAI_API_KEY not set"]

    openai.api_key = api_key
    prompt = (
        f"Suggest {limit} example commands to run this module effectively:\n" + doc
    )
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
        )
        text = resp["choices"][0]["message"]["content"].strip()
        return text.splitlines()
    except Exception as e:  # pragma: no cover - network
        return [f"failed: {e}"]
