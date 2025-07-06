"""Resolve DNS records for a domain."""

import os
import socket
import sys
from analysis_db.db_api import log_scan_result
from analysis_db.chat_analyzer import analyze_result


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: dns_lookup.py <domain>")
        return False
    domain = argv[0]
    raw = {"query": domain}
    try:
        _, _, ips = socket.gethostbyname_ex(domain)
        print(f"[+] {domain} -> {', '.join(ips)}")
        raw["response"] = ",".join(ips)
        result = {"target": domain, "ips": ips, "raw": raw}
    except Exception as e:
        print(f"[!] Lookup failed: {e}")
        raw["error"] = str(e)
        result = {"target": domain, "error": str(e), "raw": raw}
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "dns_lookup", **result})
        except Exception:
            pass
    return result


if __name__ == "__main__":
    main()
