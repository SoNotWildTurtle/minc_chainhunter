"""Perform a WHOIS lookup for a domain."""

import os
import subprocess
import sys

from analysis_db.db_api import log_scan_result
from analysis_db.chat_analyzer import analyze_result


def build_whois_cmd(target: str):
    """Return the command list to run a WHOIS lookup."""
    return ["whois", target]


def run_whois(target: str):
    """Execute the WHOIS command and return stdout and stderr."""
    cmd = build_whois_cmd(target)
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return proc.stdout.strip(), proc.stderr.strip()


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: whois_scan.py <domain>")
        return False
    target = argv[0]
    stdout, stderr = run_whois(target)
    raw = {"cmd": " ".join(build_whois_cmd(target)), "stdout": stdout}
    if stderr:
        raw["stderr"] = stderr
    result = {"target": target, "whois": stdout, "raw": raw}
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "whois_scan", **result})
        except Exception:
            pass
    if stdout:
        print(stdout.splitlines()[0])
    return result


if __name__ == "__main__":
    main()
