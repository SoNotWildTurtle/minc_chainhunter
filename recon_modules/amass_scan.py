"""Run Amass for subdomain enumeration."""

import argparse
import os
import subprocess
import sys
from typing import List

from analysis_db.db_api import log_scan_result
from analysis_db.chat_analyzer import analyze_result


def build_amass_cmd(domain: str) -> List[str]:
    script = os.path.join(os.path.dirname(__file__), "..", "github_scanners", "amass", "run.sh")
    return ["bash", script, "enum", "-d", domain]


def main(argv: List[str] | None = None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Run Amass")
    parser.add_argument("domain")
    args = parser.parse_args(argv)

    cmd = build_amass_cmd(args.domain)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    result = {"target": args.domain, "output": proc.stdout.strip()}
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "amass_scan", **result})
        except Exception:
            pass
    return result


if __name__ == "__main__":
    main()
