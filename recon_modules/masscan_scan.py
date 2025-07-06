"""Run masscan for fast port scanning."""

import argparse
import os
import subprocess
import sys
from typing import List

from analysis_db.db_api import log_scan_result
from analysis_db.chat_analyzer import analyze_result


def build_masscan_cmd(target: str, ports: str = "0-65535", rate: int = 1000) -> List[str]:
    script = os.path.join(os.path.dirname(__file__), "..", "github_scanners", "masscan", "run.sh")
    return ["bash", script, target, "-p", ports, "--rate", str(rate)]


def main(argv: List[str] | None = None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Run masscan")
    parser.add_argument("target")
    parser.add_argument("--ports", default="0-65535")
    parser.add_argument("--rate", type=int, default=1000)
    args = parser.parse_args(argv)

    cmd = build_masscan_cmd(args.target, ports=args.ports, rate=args.rate)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    result = {"target": args.target, "output": proc.stdout.strip()}
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "masscan_scan", **result})
        except Exception:
            pass
    return result


if __name__ == "__main__":
    main()
