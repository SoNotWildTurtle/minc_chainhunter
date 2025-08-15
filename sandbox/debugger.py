#!/usr/bin/env python3
"""Sandboxed debugger for testing code evolutions."""
import shutil
import subprocess
import tempfile
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def apply_evolution(patch_func, repo_dir: str | None = None, run_tests: bool = True) -> bool:
    """Copy repo to a temp dir, apply patch_func, optionally run tests."""
    src = Path(repo_dir) if repo_dir else ROOT
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        shutil.copytree(src, tmp_path, dirs_exist_ok=True)
        patch_func(tmp_path)
        if run_tests:
            env = os.environ.copy()
            env.setdefault("SKIP_INSTALL", "1")
            res = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=tmp_path, env=env)
            if res.returncode != 0:
                print("[!] Tests failed in sandbox")
                return False
        print("[+] Evolution succeeded in sandbox")
        return True


def main():
    if len(sys.argv) < 2:
        print("Usage: debugger.py <script.py>")
        return
    script = Path(sys.argv[1]).resolve()
    def patch(repo: Path):
        subprocess.run([sys.executable, str(script)], cwd=repo, check=False)
    success = apply_evolution(patch)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
