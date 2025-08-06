import argparse
import os
import subprocess
import sys
from typing import List

from analysis_db.db_api import log_scan_result
from analysis_db.chat_analyzer import analyze_result


def build_covenant_cmd(action: str) -> List[str]:
    script = os.path.join(
        os.path.dirname(__file__), "..", "github_scanners", "covenant", "run.sh"
    )
    return ["bash", script, action]


def main(argv: List[str] | None = None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Manage Covenant C2 framework (offensive pentesting)"
    )
    parser.add_argument(
        "action",
        choices=["install", "start", "stop"],
        help="Action to perform",
    )
    args = parser.parse_args(argv)

    cmd = build_covenant_cmd(args.action)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    result = {"action": args.action, "output": proc.stdout.strip()}
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "covenant_control", **result})
        except Exception:
            pass
    return result


if __name__ == "__main__":
    main()
