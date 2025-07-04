"""Run dirsearch to discover directories."""

import argparse
import os
import subprocess
import sys
from analysis_db.db_api import log_scan_result
from typing import List

from analysis_db.chat_analyzer import analyze_result


def build_dirsearch_cmd(
    url: str,
    wordlist: str | None = None,
    threads: int = 20,
    extensions: str | None = None,
) -> List[str]:
    """Construct the command list for dirsearch."""
    script = os.path.join(
        os.path.dirname(__file__), "..", "github_scanners", "dirsearch", "run.sh"
    )
    cmd = ["bash", script, "-u", url]
    if wordlist:
        cmd += ["-w", wordlist]
    if threads:
        cmd += ["-t", str(threads)]
    if extensions:
        cmd += ["-e", extensions]
    return cmd


def main(argv: List[str] | None = None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Run dirsearch")
    parser.add_argument("url")
    parser.add_argument("-w", "--wordlist", help="Custom wordlist")
    parser.add_argument("-t", "--threads", type=int, default=20)
    parser.add_argument("-e", "--extensions", help="File extensions list")
    args = parser.parse_args(argv)

    cmd = build_dirsearch_cmd(
        args.url, wordlist=args.wordlist, threads=args.threads, extensions=args.extensions
    )
    proc = subprocess.run(cmd, capture_output=True, text=True)
    result = {"target": args.url, "output": proc.stdout.strip()}
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "dirsearch_scan", **result})
        except Exception:
            pass
    return result


if __name__ == "__main__":
    main()
