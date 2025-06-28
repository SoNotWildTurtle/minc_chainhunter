#!/usr/bin/env python3
# MINC - bin/github_scanners/repo_launcher.py
"""
Unified launcher for GitHub-based recon/vuln scanning modules.
Loads all tool subdirs, validates config, executes with passed arguments, and saves result logs.
"""

import os
import subprocess
import sys
from datetime import datetime

SCANNER_ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(SCANNER_ROOT, "../../log_manager/logs/recon/")
TOOLS = [name for name in os.listdir(SCANNER_ROOT) if os.path.isdir(os.path.join(SCANNER_ROOT, name)) and name != "__pycache__" and name != "repo_launcher.py"]

def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)

def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def run_tool(tool, args):
    tool_dir = os.path.join(SCANNER_ROOT, tool)
    entry = os.path.join(tool_dir, "run.sh")
    if not os.path.isfile(entry):
        print(f"[!] Tool {tool} missing run.sh. Skipping.")
        return None
    cmd = ["bash", entry] + args
    print(f"[+] Launching {tool}: {' '.join(cmd)}")
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = proc.stdout.decode(errors="replace") + "\n" + proc.stderr.decode(errors="replace")
    return result

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in TOOLS:
        print(f"Usage: {sys.argv[0]} <tool> [tool args]")
        print(f"Available tools: {', '.join(TOOLS)}")
        sys.exit(1)
    tool = sys.argv[1]
    args = sys.argv[2:]
    ensure_log_dir()
    output = run_tool(tool, args)
    if output:
        ts = get_timestamp()
        log_path = os.path.join(LOG_DIR, f"{tool}_{ts}.log")
        with open(log_path, "w") as f:
            f.write(output)
        print(f"[+] Output saved to {log_path}")

if __name__ == "__main__":
    main()
