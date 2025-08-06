"""Run httpx for HTTP probing."""

import argparse
import json
import os
import subprocess
import sys
from typing import List

from analysis_db.db_api import log_scan_result
from analysis_db.chat_analyzer import analyze_result


def build_httpx_cmd(target: str) -> List[str]:
    """Build the command used to invoke httpx.

    The wrapper enables JSON output, status codes, titles, and technology
    detection so results can be parsed and stored in structured form.
    """

    script = os.path.join(
        os.path.dirname(__file__), "..", "github_scanners", "httpx", "run.sh"
    )
    return [
        "bash",
        script,
        "-json",
        "-status-code",
        "-title",
        "-tech-detect",
        "-silent",
        "-u",
        target,
    ]


def _parse_httpx_output(output: str) -> List[dict]:
    """Parse JSON lines emitted by httpx.

    Keys that contain hyphens are normalised to use underscores for easier
    access in Python code. Lines that cannot be parsed are ignored.
    """

    entries: List[dict] = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        data = {k.replace("-", "_"): v for k, v in data.items()}
        entries.append(data)
    return entries


def main(argv: List[str] | None = None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Run httpx")
    parser.add_argument("target", help="URL or host to probe")
    args = parser.parse_args(argv)

    cmd = build_httpx_cmd(args.target)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    parsed = _parse_httpx_output(proc.stdout)
    result = {
        "target": args.target,
        "output": proc.stdout.strip(),
        "entries": parsed,
    }
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "httpx_scan", **result})
        except Exception:
            pass
    return result


if __name__ == "__main__":
    main()
