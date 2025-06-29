"""Resolve DNS records for a domain."""

import socket
import sys


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: dns_lookup.py <domain>")
        return False
    domain = argv[0]
    try:
        _, _, ips = socket.gethostbyname_ex(domain)
        print(f"[+] {domain} -> {', '.join(ips)}")
        return {"target": domain, "ips": ips}
    except Exception as e:
        print(f"[!] Lookup failed: {e}")
        return {"target": domain, "error": str(e)}


if __name__ == "__main__":
    main()
