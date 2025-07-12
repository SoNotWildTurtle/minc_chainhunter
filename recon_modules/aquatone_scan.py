"""Capture screenshots of HTTP services using aquatone."""

import argparse
import os
import subprocess
import sys
from typing import List

from analysis_db.db_api import log_scan_result
from analysis_db.chat_analyzer import analyze_result


def build_aquatone_cmd(domain: str, out_dir: str = "aquatone_out") -> List[str]:
    script = os.path.join(os.path.dirname(__file__), "..", "github_scanners", "aquatone", "run.sh")
    return ["bash", script, domain, out_dir]


def main(argv: List[str] | None = None) -> dict:
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Run aquatone")
    parser.add_argument("domain")
    parser.add_argument("--out", dest="out_dir", default="aquatone_out")
    args = parser.parse_args(argv)

    cmd = build_aquatone_cmd(args.domain, out_dir=args.out_dir)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    result = {"target": args.domain, "output": proc.stdout.strip()}
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "aquatone_scan", **result})
        except Exception:
            pass
    return result


if __name__ == "__main__":
    main()
