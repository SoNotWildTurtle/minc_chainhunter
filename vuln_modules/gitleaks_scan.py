"""Run gitleaks secret scanner."""

import argparse
import os
import subprocess
import sys
from typing import List

from analysis_db.chat_analyzer import analyze_result


def build_gitleaks_cmd(
    repo_dir: str,
    redact: bool = False,
    config: str | None = None,
) -> List[str]:
    """Construct the command list for gitleaks."""
    script = os.path.join(
        os.path.dirname(__file__), "..", "github_scanners", "gitleaks", "run.sh"
    )
    cmd = ["bash", script, "detect", "--source", repo_dir]
    if redact:
        cmd.append("--redact")
    if config:
        cmd += ["--config", config]
    return cmd


def main(argv: List[str] | None = None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Run gitleaks")
    parser.add_argument("repo_dir")
    parser.add_argument("--redact", action="store_true", help="Redact secrets")
    parser.add_argument("--config", help="Custom config file")
    args = parser.parse_args(argv)

    cmd = build_gitleaks_cmd(args.repo_dir, redact=args.redact, config=args.config)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    result = {"target": args.repo_dir, "output": proc.stdout.strip()}
    result.update(analyze_result(result))
    return result


if __name__ == "__main__":
    main()
