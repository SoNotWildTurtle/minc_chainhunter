import argparse
import json
import os
import pwd
from typing import Dict, List, Optional

from .chat_analyzer import analyze_result
from .report_gen import build_report, load_results, save_results

from ipc_bus.bus_init import start_ipc_server
from ipc_bus.bus_integrity import is_alias_approved


def drop_privileges(user: Optional[str]) -> None:
    """Drop privileges to the specified user if running as root."""
    if os.getuid() != 0 or not user:
        return
    try:
        pw = pwd.getpwnam(user)
        os.setgid(pw.pw_gid)
        os.setuid(pw.pw_uid)
    except Exception:
        pass

DB_DIR = ""


def _count_vulns(entry: Dict) -> int:
    """Return total vulnerability entries in a result tree."""
    count = len(entry.get("vulnerabilities", []))
    for step in entry.get("steps", []):
        count += _count_vulns(step)
    return count


def handle_scan(result: Dict) -> Dict:
    data = load_results(DB_DIR)
    analysis = analyze_result(result)
    if analysis.get("tags"):
        tags = result.get("tags", []).copy()
        for t in analysis["tags"]:
            if t not in tags:
                tags.append(t)
        result["tags"] = tags
    result["summary"] = analysis.get("summary")
    result["vuln_count"] = _count_vulns(result)
    data.append(result)
    save_results(data, DB_DIR)
    return {"status": "ok"}


def handle_get_results(limit: int = 0) -> Dict:
    data = load_results(DB_DIR)
    if limit > 0:
        data = data[-limit:]
    return {"status": "ok", "results": data}


def handle_search_results(tag: str, limit: int = 0) -> Dict:
    """Return results containing the specified tag."""
    data = [r for r in load_results(DB_DIR) if tag in (r.get("tags") or [])]
    if limit > 0:
        data = data[-limit:]
    return {"status": "ok", "results": data}


def handle_purge(limit: int) -> Dict:
    """Keep only the latest `limit` results."""
    if limit <= 0:
        return {"status": "error", "error": "invalid limit"}
    data = load_results(DB_DIR)
    if len(data) <= limit:
        return {"status": "ok", "purged": 0}
    data = data[-limit:]
    save_results(data, DB_DIR)
    return {"status": "ok", "purged": True}


def start_db_server(
    db_dir: str,
    sock_path: str,
    once: bool = False,
    user: Optional[str] = None,
) -> None:
    global DB_DIR
    DB_DIR = db_dir
    os.makedirs(DB_DIR, mode=0o700, exist_ok=True)
    os.umask(0o077)
    drop_privileges(user)

    secret = os.getenv("MINC_IPC_SECRET")

    def handler(msg: Dict) -> Dict:
        alias = msg.get("alias")
        if not is_alias_approved(alias):
            return {"status": "error", "error": "alias not approved"}
        if alias == "scan":
            return handle_scan(msg.get("result", {}))
        if alias == "report":
            results = load_results(DB_DIR)
            out_dir = msg.get("out_dir", "reports")
            path = build_report(results, out_dir)
            return {"status": "ok", "path": path}
        if alias == "results":
            limit = int(msg.get("limit", 0))
            return handle_get_results(limit)
        if alias == "search":
            tag = msg.get("tag", "")
            limit = int(msg.get("limit", 0))
            return handle_search_results(tag, limit)
        if alias == "purge":
            limit = int(msg.get("limit", 0))
            return handle_purge(limit)
        return {"status": "error", "error": "unknown alias"}

    start_ipc_server(sock_path, handler, once, secret)


def main() -> None:
    parser = argparse.ArgumentParser(description="Start ChainHunter analysis DB server")
    parser.add_argument("--db_dir", default="db_data")
    parser.add_argument("--socket", required=True)
    parser.add_argument("--user", help="Drop privileges to this user")
    args = parser.parse_args()

    start_db_server(args.db_dir, args.socket, user=args.user)


if __name__ == "__main__":
    main()
