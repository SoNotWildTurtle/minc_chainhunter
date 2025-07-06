"""Run nmap for service enumeration."""

import argparse
import os
import re
import subprocess
import sys
from typing import List

from analysis_db.db_api import log_scan_result
from analysis_db.chat_analyzer import analyze_result


def build_nmap_cmd(target: str, options: str = "-sV") -> List[str]:
    script = os.path.join(os.path.dirname(__file__), "..", "github_scanners", "nmap", "run.sh")
    cmd = ["bash", script, target]
    if options:
        cmd += options.split()
    return cmd


def _parse_ports(output: str) -> List[int]:
    ports: List[int] = []
    for line in output.splitlines():
        parts = line.split()
        if not parts:
            continue
        if '/' in parts[0] and len(parts) > 1 and parts[1] == 'open':
            try:
                ports.append(int(parts[0].split('/')[0]))
            except ValueError:
                continue
    return sorted(set(ports))


def main(argv: List[str] | None = None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Run nmap")
    parser.add_argument("target")
    parser.add_argument("--options", default="-sV")
    args = parser.parse_args(argv)

    cmd = build_nmap_cmd(args.target, options=args.options)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    out = proc.stdout.strip()
    result = {"target": args.target, "output": out}
    ports = _parse_ports(out)
    if ports:
        result["ports"] = ports
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "nmap_scan", **result})
        except Exception:
            pass
    return result


if __name__ == "__main__":
    main()

