"""Run Nikto for web server vulnerability scanning."""

import argparse
import os
import subprocess
import sys
from typing import List

from analysis_db.db_api import log_scan_result
from analysis_db.chat_analyzer import analyze_result


def build_nikto_cmd(host: str, options: str | None = None) -> List[str]:
    script = os.path.join(os.path.dirname(__file__), "..", "github_scanners", "nikto", "run.sh")
    cmd = ["bash", script, "-host", host]
    if options:
        cmd += options.split()
    return cmd


def main(argv: List[str] | None = None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Run Nikto web scanner")
    parser.add_argument("host", help="Target host or URL")
    parser.add_argument("--options", help="Additional Nikto options")
    args = parser.parse_args(argv)

    cmd = build_nikto_cmd(args.host, options=args.options)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    result = {"target": args.host, "output": proc.stdout.strip()}
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "nikto_scan", **result})
        except Exception:
            pass
    return result


if __name__ == "__main__":
    main()
