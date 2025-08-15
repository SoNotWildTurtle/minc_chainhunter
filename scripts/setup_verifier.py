import re
from pathlib import Path

CHECK_RE = re.compile(r"\[(SV\d+)\]\s+(.*?)\s+\((done|pending)\)", re.IGNORECASE)


def load_checks(path="SETUP_VERIFICATION.txt"):
    """Parse the setup verification checklist."""
    lines = Path(path).read_text().splitlines()
    checks = []
    for line in lines:
        match = CHECK_RE.match(line.strip())
        if match:
            checks.append({
                "id": match.group(1),
                "desc": match.group(2),
                "status": match.group(3).lower(),
            })
    return checks


def main():
    for check in load_checks():
        marker = "✓" if check["status"] == "done" else "✗"
        print(f"{marker} {check['id']}: {check['desc']} ({check['status']})")


if __name__ == "__main__":
    main()
