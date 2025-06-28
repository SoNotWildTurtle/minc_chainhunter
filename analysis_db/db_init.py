import argparse
import json
import os
from typing import Dict

from ipc_bus.bus_init import start_ipc_server
from ipc_bus.bus_integrity import is_alias_approved

DB_DIR = ""


def handle_scan(result: Dict) -> Dict:
    path = os.path.join(DB_DIR, "results.json")
    data = []
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    data.append(result)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return {"status": "ok"}


def start_db_server(db_dir: str, sock_path: str, once: bool = False) -> None:
    global DB_DIR
    DB_DIR = db_dir
    os.makedirs(DB_DIR, exist_ok=True)

    def handler(msg: Dict) -> Dict:
        alias = msg.get("alias")
        if not is_alias_approved(alias):
            return {"status": "error", "error": "alias not approved"}
        if alias == "scan":
            return handle_scan(msg.get("result", {}))
        return {"status": "error", "error": "unknown alias"}

    start_ipc_server(sock_path, handler, once)


def main() -> None:
    parser = argparse.ArgumentParser(description="Start ChainHunter analysis DB server")
    parser.add_argument("--db_dir", default="db_data")
    parser.add_argument("--socket", required=True)
    args = parser.parse_args()

    start_db_server(args.db_dir, args.socket)


if __name__ == "__main__":
    main()
