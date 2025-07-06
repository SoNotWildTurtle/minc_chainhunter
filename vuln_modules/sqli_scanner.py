"""Basic SQL injection scanner using HTTP error detection."""

import argparse
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

from analysis_db.chat_analyzer import analyze_result
from analysis_db.db_api import log_scan_result

SQL_ERRORS = [
    "sql syntax",
    "mysql_fetch",
    "syntax error",
    "unclosed quotation",
]


def scan_url(url: str, payload: str) -> tuple[bool, dict]:
    """Return detection result and raw data."""
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    if "?" in url:
        test_url = url + urllib.parse.quote(payload)
    else:
        test_url = url + "?q=" + urllib.parse.quote(payload)
    raw = {"url": test_url}
    try:
        with urllib.request.urlopen(test_url, timeout=5) as resp:
            body = resp.read().decode(errors="ignore")
            raw.update({"status": resp.getcode(), "response": body[:200]})
    except Exception as e:
        raw.update({"error": str(e)})
        return False, raw
    detected = any(err in body.lower() for err in SQL_ERRORS)
    return detected, raw


def main(argv: list[str] | None = None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Scan for SQL injection")
    parser.add_argument("url")
    parser.add_argument("--payload", default="'")
    args = parser.parse_args(argv)

    print(f"[+] Scanning {args.url} for SQL injection")
    vulnerable, raw = scan_url(args.url, args.payload)
    vulnerabilities = []
    if vulnerable:
        print("[!] SQL injection detected")
        vulnerabilities.append({"payload": args.payload})
    else:
        print("[-] No vulnerabilities found")
    result = {"target": args.url, "vulnerabilities": vulnerabilities, "raw": raw}
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "sqli_scanner", **result})
        except Exception:
            pass
    return result


if __name__ == "__main__":
    main()
