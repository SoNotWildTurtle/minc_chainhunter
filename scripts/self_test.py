#!/usr/bin/env python3
"""Run ChainHunter test suite for self-verification."""
import os
import subprocess
import sys
from pathlib import Path


def run_self_test(repo_dir: str | None = None) -> bool:
    """Execute pytest in the repository and return success."""
    repo = Path(repo_dir) if repo_dir else Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env.setdefault("SKIP_CLONE", "1")
    try:
        subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=repo, env=env, check=True)
        print("[+] Tests passed")
        return True
    except subprocess.CalledProcessError:
        print("[!] Tests failed")
        return False


if __name__ == "__main__":
    ok = run_self_test()
    sys.exit(0 if ok else 1)
