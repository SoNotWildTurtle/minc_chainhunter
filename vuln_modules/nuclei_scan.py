"""Run nuclei vulnerability scanner."""

import os
import subprocess
import sys

from analysis_db.chat_analyzer import analyze_result


def main():
    if len(sys.argv) < 2:
        print("Usage: nuclei_scan.py <url>")
        return False
    url = sys.argv[1]
    script = os.path.join(os.path.dirname(__file__), "..", "github_scanners", "nuclei", "run.sh")
    proc = subprocess.run(["bash", script, "-u", url], capture_output=True, text=True)
    result = {"target": url, "output": proc.stdout.strip()}
    result.update(analyze_result(result))
    return result


if __name__ == "__main__":
    main()
