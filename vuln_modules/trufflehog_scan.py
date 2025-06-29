import argparse
import os
import subprocess
import sys
from typing import List

from analysis_db.chat_analyzer import analyze_result


def build_trufflehog_cmd(repo_dir: str, regex: bool = False) -> List[str]:
    """Construct the command list for truffleHog."""
    script = os.path.join(
        os.path.dirname(__file__), "..", "github_scanners", "trufflehog", "run.sh"
    )
    cmd = ["bash", script, repo_dir]
    if regex:
        cmd.append("--regex")
    return cmd


def main(argv: List[str] | None = None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Run truffleHog")
    parser.add_argument("repo_dir")
    parser.add_argument("--regex", action="store_true", help="Enable regex mode")
    args = parser.parse_args(argv)

    cmd = build_trufflehog_cmd(args.repo_dir, regex=args.regex)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    result = {"target": args.repo_dir, "output": proc.stdout.strip()}
    result.update(analyze_result(result))
    return result


if __name__ == "__main__":
    main()
