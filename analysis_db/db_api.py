"""Client helpers for interacting with the analysis DB via IPC."""

from typing import Dict

from ipc_bus.message_api import send_request
from ipc_bus.bus_integrity import is_alias_approved


def log_scan_result(sock_path: str, result: Dict) -> Dict:
    alias = "scan"
    if not is_alias_approved(alias):
        raise ValueError("Alias not approved")
    payload = {"alias": alias, "result": result}
    return send_request(sock_path, payload)
