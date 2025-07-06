"""Run nmap for service enumeration."""

import argparse
import os
import subprocess
import sys
from typing import List

from analysis_db.db_api import log_scan_result
from analysis_db.chat_analyzer import analyze_result


def build_nmap_cmd(target: str, options: str = "-sV") -> List[str]:
    script = os.path.join(os.path.dirname(__file__), "..", "github_scanners", "nmap", "run.sh")
    cmd = ["bash", script, target]
    if options:
        cmd += options.split()
    return cmd


def main(argv: List[str] | None = None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Run nmap")
    parser.add_argument("target")
    parser.add_argument("--options", default="-sV")
    args = parser.parse_args(argv)

    cmd = build_nmap_cmd(args.target, options=args.options)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    result = {"target": args.target, "output": proc.stdout.strip()}
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "nmap_scan", **result})
        except Exception:
            pass
    return result


if __name__ == "__main__":
    main()
