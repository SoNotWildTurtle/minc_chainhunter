"""Run ffuf web fuzzer."""

import argparse
import os
import subprocess
import sys
from typing import List

from analysis_db.chat_analyzer import analyze_result
from analysis_db.db_api import log_scan_result


def build_ffuf_cmd(url: str, wordlist: str | None = None) -> List[str]:
    script = os.path.join(
        os.path.dirname(__file__), "..", "github_scanners", "ffuf", "run.sh"
    )
    cmd = ["bash", script, "-u", url]
    if wordlist:
        cmd += ["-w", wordlist]
    return cmd


def main(argv: List[str] | None = None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Run ffuf")
    parser.add_argument("url")
    parser.add_argument("-w", "--wordlist", help="Wordlist file")
    args = parser.parse_args(argv)

    cmd = build_ffuf_cmd(args.url, wordlist=args.wordlist)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    result = {"target": args.url, "output": proc.stdout.strip()}
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "ffuf_scan", **result})
        except Exception:
            pass
    return result


if __name__ == "__main__":
    main()
