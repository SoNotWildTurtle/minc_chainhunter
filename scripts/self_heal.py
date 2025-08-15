#!/usr/bin/env python3
"""Self-healing utility for ChainHunter."""
import os
import subprocess
import sys
from pathlib import Path

from analysis_db.report_gen import load_results, save_results


def _repair_db(db_dir: Path) -> None:
    """Ensure results file passes HMAC verification, backing up corrupt data."""
    path = db_dir / "results.json"
    if not path.exists():
        return
    data = load_results(str(db_dir))
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        text = ""
    if not data and text:
        backup = path.with_suffix(".json.bak")
        path.rename(backup)
        save_results([], str(db_dir))
        print(f"[!] Repaired corrupt results.json, backup at {backup}")


def run_self_heal(repo_dir: str | None = None) -> bool:
    """Reinstall scanner repos and run the test suite."""
    repo = Path(repo_dir) if repo_dir else Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env["SKIP_CLONE"] = "1"
    subprocess.run(
        [sys.executable, "scripts/install_requirements.py"],
        cwd=repo,
        env=env,
        check=False,
    )
    subprocess.run(
        ["bash", "scripts/install_scanner_repos.sh"],
        cwd=repo,
        env=env,
        check=False,
    )
    _repair_db(repo / "db_data")
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
