"""Run theHarvester for email and subdomain enumeration."""

import argparse
import os
import subprocess
import sys
from typing import List

from analysis_db.db_api import log_scan_result
from analysis_db.chat_analyzer import analyze_result


def build_theharvester_cmd(domain: str, sources: str | None = None, limit: int = 100) -> List[str]:
    script = os.path.join(os.path.dirname(__file__), "..", "github_scanners", "theharvester", "run.sh")
    cmd = ["bash", script, "-d", domain, "-l", str(limit)]
    if sources:
        cmd += ["-s", sources]
    return cmd


def main(argv: List[str] | None = None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Run theHarvester")
    parser.add_argument("domain")
    parser.add_argument("-s", "--sources", help="Comma-separated data sources")
    parser.add_argument("-l", "--limit", type=int, default=100)
    args = parser.parse_args(argv)

    cmd = build_theharvester_cmd(args.domain, sources=args.sources, limit=args.limit)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    result = {"target": args.domain, "output": proc.stdout.strip()}
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "theharvester_scan", **result})
        except Exception:
            pass
    return result


if __name__ == "__main__":
    main()
