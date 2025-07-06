#!/usr/bin/env python3
"""Self-healing utility for ChainHunter."""
import os
import subprocess
import sys
from pathlib import Path


def run_self_heal(repo_dir: str | None = None) -> bool:
    """Reinstall scanner repos and run the test suite."""
    repo = Path(repo_dir) if repo_dir else Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env["SKIP_CLONE"] = "1"
    subprocess.run([
        "bash",
        "scripts/install_scanner_repos.sh",
    ], cwd=repo, env=env, check=False)
    if os.environ.get("FAST_HEAL"):
        print("[*] FAST_HEAL enabled - skipping test suite")
        return True
    try:
        subprocess.run([
            sys.executable,
            "-m",
            "pytest",
            "-q",
        ], cwd=repo, check=True)
        print("[+] Self-heal successful")
        return True
    except subprocess.CalledProcessError:
        print("[!] Self-heal tests failed")
        return False


if __name__ == "__main__":
    ok = run_self_heal()
    sys.exit(0 if ok else 1)
