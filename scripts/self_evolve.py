#!/usr/bin/env python3
"""Trigger Codex-based self evolution."""
import os
import sys
from pathlib import Path


def run_self_evolve(repo_dir: str | None = None) -> bool:
    repo = Path(repo_dir) if repo_dir else Path(__file__).resolve().parents[1]
    print(f"[*] Starting self-evolution in {repo}")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[!] OPENAI_API_KEY not set. Skipping Codex execution.")
        return True
    try:
        import openai
        openai.api_key = api_key
        goals = (repo / "GOALS.txt").read_text()
        prompt = f"Improve the project based on these goals:\n{goals}\n"[:2000]
        openai.Completion.create(model="code-davinci-002", prompt=prompt, max_tokens=50)
        print("[+] Codex executed successfully (no changes applied in this demo).")
        return True
    except Exception as e:
        print(f"[!] Codex execution failed: {e}")
        return False


if __name__ == "__main__":
    success = run_self_evolve()
    sys.exit(0 if success else 1)
