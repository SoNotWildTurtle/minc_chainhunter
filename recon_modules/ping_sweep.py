"""Simple ping sweep module for Chainhunter."""

import os
import subprocess
import sys
from analysis_db.db_api import log_scan_result
from analysis_db.chat_analyzer import analyze_result


def main():
    if len(sys.argv) < 2:
        print("Usage: ping_sweep.py <host>")
        return False
    target = sys.argv[1]
    print(f"[+] Pinging {target} ...")
    reachable = True
    try:
        subprocess.run(["ping", "-c", "1", target], check=True)
        print("[+] Host reachable")
    except subprocess.CalledProcessError:
        print("[-] Host unreachable")
        reachable = False
    result = {"target": target, "reachable": reachable}
    result.update(analyze_result(result))
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "ping_sweep", **result})
        except Exception:
            pass
    return result


if __name__ == "__main__":
    main()
