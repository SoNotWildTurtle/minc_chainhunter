"""Generate human-readable reports from stored scan results."""

import json
import os
from datetime import datetime
from typing import List, Dict
from cryptography.fernet import Fernet


def _get_cipher() -> Fernet | None:
    key = os.getenv("MINC_ENCRYPT_KEY")
    if not key:
        return None
    try:
        return Fernet(key.encode())
    except Exception:
        return None


def load_results(db_dir: str) -> List[Dict]:
    path = os.path.join(db_dir, "results.json")
    if not os.path.isfile(path):
        return []
    cipher = _get_cipher()
    if cipher:
        try:
            with open(path, "rb") as f:
                data = f.read()
            decrypted = cipher.decrypt(data)
            return json.loads(decrypted.decode())
        except Exception:
            return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_results(results: List[Dict], db_dir: str) -> None:
    path = os.path.join(db_dir, "results.json")
    cipher = _get_cipher()
    os.makedirs(db_dir, exist_ok=True)
    if cipher:
        data = json.dumps(results).encode()
        enc = cipher.encrypt(data)
        with open(path, "wb") as f:
            f.write(enc)
    else:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(results, f)
    os.chmod(path, 0o600)


def build_report(results: List[Dict], out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(out_dir, f"report_{ts}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# ChainHunter Report\n\n")
        for item in results:
            module = item.get("module", "unknown")
            target = item.get("target", "?")
            f.write(f"## {module} - {target}\n")
            summary = item.get("summary") or "No summary"
            f.write(summary + "\n\n")
            tags = item.get("tags") or []
            if tags:
                f.write("Tags: " + ", ".join(tags) + "\n\n")
    return report_path


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Generate ChainHunter report")
    parser.add_argument("--db_dir", default="db_data")
    parser.add_argument("--out_dir", default="reports")
    args = parser.parse_args()
    res = load_results(args.db_dir)
    path = build_report(res, args.out_dir)
    print(f"[+] Report written to {path}")


if __name__ == "__main__":
    main()
