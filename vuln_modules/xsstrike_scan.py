import argparse
import os
import subprocess
import sys
from typing import List

from analysis_db.db_api import log_scan_result
from analysis_db.chat_analyzer import analyze_result


def build_xsstrike_cmd(url: str, crawl: bool = False) -> List[str]:
    """Construct the command list for XSStrike."""
    script = os.path.join(
        os.path.dirname(__file__), "..", "github_scanners", "xsstrike", "run.sh"
    )
    cmd = ["bash", script, "-u", url]
    if crawl:
        cmd.append("--crawl")
    return cmd


def main(argv: List[str] | None = None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Run XSStrike for XSS detection")
    parser.add_argument("url")
    parser.add_argument("--crawl", action="store_true", help="Enable crawler")
    args = parser.parse_args(argv)

    cmd = build_xsstrike_cmd(args.url, crawl=args.crawl)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    result = {"target": args.url, "output": proc.stdout.strip()}
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "xsstrike_scan", **result})
        except Exception:
            pass
    return result


if __name__ == "__main__":
    main()
