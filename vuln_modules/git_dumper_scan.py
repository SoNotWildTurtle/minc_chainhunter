"""Dump exposed .git directories using git-dumper."""

import argparse
import os
import subprocess
import sys
from typing import List

from analysis_db.db_api import log_scan_result
from analysis_db.chat_analyzer import analyze_result


def build_git_dumper_cmd(url: str, out_dir: str = "dump") -> List[str]:
    script = os.path.join(os.path.dirname(__file__), "..", "github_scanners", "git_dumper", "run.sh")
    return ["bash", script, url, out_dir]


def main(argv: List[str] | None = None) -> dict:
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Run git-dumper")
    parser.add_argument("url")
    parser.add_argument("out_dir", nargs="?", default="dump")
    args = parser.parse_args(argv)

    cmd = build_git_dumper_cmd(args.url, out_dir=args.out_dir)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    result = {"target": args.url, "output": proc.stdout.strip()}
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "git_dumper_scan", **result})
        except Exception:
            pass
    return result


if __name__ == "__main__":
    main()
