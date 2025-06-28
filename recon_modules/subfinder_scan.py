"""Run subfinder for subdomain enumeration."""

import os
import subprocess
import sys

from analysis_db.chat_analyzer import analyze_result


def main():
    if len(sys.argv) < 2:
        print("Usage: subfinder_scan.py <domain>")
        return False
    domain = sys.argv[1]
    script = os.path.join(os.path.dirname(__file__), "..", "github_scanners", "subfinder", "run.sh")
    proc = subprocess.run(["bash", script, "-d", domain], capture_output=True, text=True)
    result = {"target": domain, "output": proc.stdout.strip()}
    result.update(analyze_result(result))
    return result


if __name__ == "__main__":
    main()
