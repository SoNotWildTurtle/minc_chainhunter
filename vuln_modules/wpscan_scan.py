"""Run WPScan for WordPress vulnerability detection."""

import argparse
import os
import subprocess
import sys
from typing import List

from analysis_db.db_api import log_scan_result
from analysis_db.chat_analyzer import analyze_result


def build_wpscan_cmd(url: str, options: str | None = None) -> List[str]:
    script = os.path.join(os.path.dirname(__file__), "..", "github_scanners", "wpscan", "run.sh")
    cmd = ["bash", script, "--url", url]
    if options:
        cmd += options.split()
    return cmd


def main(argv: List[str] | None = None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Run WPScan")
    parser.add_argument("url")
    parser.add_argument("--options", help="Additional WPScan options")
    args = parser.parse_args(argv)

    cmd = build_wpscan_cmd(args.url, options=args.options)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    result = {"target": args.url, "output": proc.stdout.strip()}
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "wpscan_scan", **result})
        except Exception:
            pass
    return result


if __name__ == "__main__":
    main()
