"""Run gitleaks secret scanner."""

import os
import subprocess
import sys

from analysis_db.chat_analyzer import analyze_result


def main():
    if len(sys.argv) < 2:
        print("Usage: gitleaks_scan.py <repo_dir>")
        return False
    repo = sys.argv[1]
    script = os.path.join(os.path.dirname(__file__), "..", "github_scanners", "gitleaks", "run.sh")
    proc = subprocess.run(["bash", script, "detect", "--source", repo], capture_output=True, text=True)
    result = {"target": repo, "output": proc.stdout.strip()}
    result.update(analyze_result(result))
    return result


if __name__ == "__main__":
    main()
