"""Run hydra login cracker."""

import argparse
import os
import subprocess
import sys
from typing import List

from analysis_db.chat_analyzer import analyze_result
from analysis_db.db_api import log_scan_result


def build_hydra_cmd(
    target: str,
    service: str,
    user: str | None = None,
    password: str | None = None,
) -> List[str]:
    script = os.path.join(
        os.path.dirname(__file__), "..", "github_scanners", "hydra", "run.sh"
    )
    cmd = ["bash", script, target, service]
    if user:
        cmd += ["-l", user]
    if password:
        cmd += ["-p", password]
    return cmd


def main(argv: List[str] | None = None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Run hydra")
    parser.add_argument("target")
    parser.add_argument("service")
    parser.add_argument("-l", "--user", help="Username")
    parser.add_argument("-p", "--password", help="Password")
    args = parser.parse_args(argv)

    cmd = build_hydra_cmd(
        args.target, args.service, user=args.user, password=args.password
    )
    proc = subprocess.run(cmd, capture_output=True, text=True)
    result = {"target": args.target, "output": proc.stdout.strip()}
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "hydra_scan", **result})
        except Exception:
            pass
    return result


if __name__ == "__main__":
    main()
