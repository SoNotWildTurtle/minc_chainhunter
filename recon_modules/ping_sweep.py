"""Simple ping sweep module for Chainhunter."""

import subprocess
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: ping_sweep.py <cidr>")
        return False
    target = sys.argv[1]
    print(f"[+] Pinging {target} ...")
    try:
        subprocess.run(["ping", "-c", "1", target], check=True)
        print("[+] Host reachable")
        return True
    except subprocess.CalledProcessError:
        print("[-] Host unreachable")
        return False

if __name__ == "__main__":
    main()
