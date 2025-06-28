"""Simple ping sweep module for Chainhunter."""

import subprocess
import sys


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
    return {"target": target, "reachable": reachable}


if __name__ == "__main__":
    main()
