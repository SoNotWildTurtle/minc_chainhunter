#!/usr/bin/env python3
"""Trigger Codex-based self evolution with self-healing."""
import os
import os
import sys
import subprocess
from pathlib import Path

from .self_heal import run_self_heal
from analysis_db.db_api import get_results
from analysis_db.neural_analyzer import suggest_pipeline, suggest_modules
from sandbox.debugger import apply_evolution


def _decide_pipeline(repo: Path, limit: int = 10) -> str:
    """Return the pipeline recommended for self-evolution."""
    sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
    try:
        resp = get_results(sock, limit=limit)
        if resp.get("status") == "ok":
            results = resp.get("results", [])
            if results:
                return suggest_pipeline(results)
    except Exception:
        pass
    return "bug_hunt"


def _run_pipeline(pipeline: str, target: str, repo: Path, workers: int) -> None:
    """Run the selected pipeline with a worker limit."""
    cmd = [
        sys.executable,
        "cli/main.py",
        "run",
        pipeline,
        target,
        "--workers",
        str(workers),
    ]
    subprocess.run(cmd, cwd=repo, check=False)


def _run_module(module: str, target: str, repo: Path, workers: int) -> None:
    """Run a single module with a worker limit."""
    cmd = [
        sys.executable,
        "cli/main.py",
        "run",
        module,
        target,
        "--workers",
        str(workers),
    ]
    subprocess.run(cmd, cwd=repo, check=False)


def _apply_patch(script: str, repo: Path) -> bool:
    """Run patch SCRIPT in sandbox then apply to repo if tests pass."""
    def patch(tmp_repo: Path) -> None:
        subprocess.run([sys.executable, script], cwd=tmp_repo, check=False)

    print(f"[*] Testing patch {script} in sandbox")
    if not apply_evolution(patch, repo_dir=str(repo)):
        print("[!] Patch failed in sandbox")
        return False
    subprocess.run([sys.executable, script], cwd=repo, check=False)
    print("[+] Applied patch script")
    return True




def run_self_evolve(
    repo_dir: str | None = None,
    target: str = "127.0.0.1",
    heal: bool = False,
    patch_script: str | None = None,
    iterations: int = 1,
) -> bool:
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

    ratio = float(os.environ.get("MINC_SELF_RATIO", "0.2"))
    workers = max(1, int((os.cpu_count() or 1) * ratio))

    for i in range(iterations):
        print(f"[*] Evolution iteration {i + 1}/{iterations}")
        pipeline = _decide_pipeline(repo)
        print(f"[*] Running {pipeline} pipeline for self-evolution with {workers} workers")
        _run_pipeline(pipeline, target, repo, workers)

        try:
            sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
            resp = get_results(sock, limit=50)
            if resp.get("status") == "ok":
                mods = suggest_modules(resp.get("results", []), top_n=1)
                if mods:
                    print(f"[*] Running recommended module {mods[0]} for further learning")
                    _run_module(mods[0], target, repo, workers)
        except Exception:
            pass

    if patch_script:
        if not _apply_patch(patch_script, repo):
            return False

    if heal:
        print("[*] Performing self-healing routine")
        return run_self_heal(str(repo))
    return True


if __name__ == "__main__":
    success = run_self_evolve()
    sys.exit(0 if success else 1)
