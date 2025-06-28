"""Run hakrawler for link discovery."""

import os
import subprocess
import sys

from analysis_db.chat_analyzer import analyze_result


def main():
    if len(sys.argv) < 2:
        print("Usage: hakrawler_scan.py <url>")
        return False
    url = sys.argv[1]
    script = os.path.join(os.path.dirname(__file__), "..", "github_scanners", "hakrawler", "run.sh")
    proc = subprocess.run(["bash", script, "-url", url], capture_output=True, text=True)
    result = {"target": url, "output": proc.stdout.strip()}
    result.update(analyze_result(result))
    return result


if __name__ == "__main__":
    main()
