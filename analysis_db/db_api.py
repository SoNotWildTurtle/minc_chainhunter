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


def generate_report(sock_path: str, out_dir: str = "reports") -> Dict:
    """Request the database server to generate a report."""
    alias = "report"
    if not is_alias_approved(alias):
        raise ValueError("Alias not approved")
    payload = {"alias": alias, "out_dir": out_dir}
    return send_request(sock_path, payload)


def get_results(sock_path: str, limit: int = 0) -> Dict:
    """Retrieve stored scan results from the DB."""
    alias = "results"
    if not is_alias_approved(alias):
        raise ValueError("Alias not approved")
    payload = {"alias": alias, "limit": limit}
    return send_request(sock_path, payload)


def search_results(sock_path: str, tag: str, limit: int = 0) -> Dict:
    """Retrieve stored results matching a tag."""
    alias = "search"
    if not is_alias_approved(alias):
        raise ValueError("Alias not approved")
    payload = {"alias": alias, "tag": tag, "limit": limit}
    return send_request(sock_path, payload)


def purge_results(sock_path: str, limit: int) -> Dict:
    """Trim stored results to the latest ``limit`` entries."""
    alias = "purge"
    if not is_alias_approved(alias):
        raise ValueError("Alias not approved")
    payload = {"alias": alias, "limit": limit}
    return send_request(sock_path, payload)

