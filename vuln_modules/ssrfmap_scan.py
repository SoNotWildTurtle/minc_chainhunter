"""Run SSRFmap on the provided URL."""

import argparse
import os
import subprocess
import sys
from analysis_db.db_api import log_scan_result
from typing import List

from analysis_db.chat_analyzer import analyze_result


def build_ssrfmap_cmd(
    url: str,
    param: str = "url",
    data: str | None = None,
) -> List[str]:
    """Construct the command list for ssrfmap."""
    script = os.path.join(
        os.path.dirname(__file__), "..", "github_scanners", "ssrfmap", "run.sh"
    )
    cmd = ["bash", script, url, "-p", param]
    if data:
        cmd += ["-d", data]
    return cmd


def main(argv: List[str] | None = None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Run ssrfmap")
    parser.add_argument("url")
    parser.add_argument("-p", "--param", default="url", help="Parameter name")
    parser.add_argument("-d", "--data", help="POST data")
    args = parser.parse_args(argv)

    cmd = build_ssrfmap_cmd(args.url, param=args.param, data=args.data)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    result = {"target": args.url, "output": proc.stdout.strip()}
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "ssrfmap_scan", **result})
        except Exception:
            pass
    return result


if __name__ == "__main__":
    main()
