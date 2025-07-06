#!/usr/bin/env python3
"""Trigger Codex-based self evolution with self-healing."""
import os
import sys
import subprocess
from pathlib import Path


def _run_bug_hunt(target: str, repo: Path) -> None:
    """Run a lightweight bug hunting pipeline."""
    subprocess.run([
        sys.executable,
        "cli/main.py",
        "run",
        "bug_hunt",
        target,
    ], cwd=repo, check=False)


def _self_heal(repo: Path) -> bool:
    """Reinstall scanners and run tests."""
    env = os.environ.copy()
    env["SKIP_CLONE"] = "1"
    subprocess.run(["bash", "scripts/install_scanner_repos.sh"], cwd=repo, env=env, check=False)
    try:
        subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=repo, check=True)
        return True
    except subprocess.CalledProcessError:
        print("[!] Self-heal tests failed")
        return False


def run_self_evolve(repo_dir: str | None = None, target: str = "127.0.0.1", heal: bool = False) -> bool:
    repo = Path(repo_dir) if repo_dir else Path(__file__).resolve().parents[1]
    print(f"[*] Starting self-evolution in {repo}")
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            import openai
            openai.api_key = api_key
            goals = (repo / "GOALS.txt").read_text()
            prompt = f"Improve the project based on these goals:\n{goals}\n"[:2000]
            openai.Completion.create(model="code-davinci-002", prompt=prompt, max_tokens=50)
            print("[+] Codex executed successfully (no changes applied in this demo).")
        except Exception as e:
            print(f"[!] Codex execution failed: {e}")
    else:
        print("[!] OPENAI_API_KEY not set. Skipping Codex execution.")

    print("[*] Running bug hunt pipeline for self-evolution")
    _run_bug_hunt(target, repo)

    if heal:
        print("[*] Performing self-healing routine")
        return _self_heal(repo)
    return True


if __name__ == "__main__":
    success = run_self_evolve()
    sys.exit(0 if success else 1)
