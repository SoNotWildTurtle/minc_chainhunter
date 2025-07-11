#!/usr/bin/env python3
"""Install ChainHunter Python dependencies and module requirements."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQ_FILE = ROOT / "requirements.txt"
SCANNER_DIR = ROOT / "github_scanners"


def run_pip(args):
    cmd = [sys.executable, "-m", "pip"] + args
    print("[+]", " ".join(cmd))
    if os.environ.get("SKIP_INSTALL"):
        return
    subprocess.check_call(cmd)


def install_root_requirements():
    if REQ_FILE.is_file():
        run_pip(["install", "-r", str(REQ_FILE)])


def install_scanner_requirements():
    if not SCANNER_DIR.is_dir():
        return
    for scanner in SCANNER_DIR.iterdir():
        src = scanner / "src"
        if not src.is_dir():
            continue
        # common patterns
        reqs = [src / "requirements.txt", src / "requirements" / "base.txt"]
        for req in reqs:
            if req.is_file():
                run_pip(["install", "-r", str(req)])


def main():
    install_root_requirements()
    install_scanner_requirements()
    print("[+] Requirements installation complete")


if __name__ == "__main__":
    main()
