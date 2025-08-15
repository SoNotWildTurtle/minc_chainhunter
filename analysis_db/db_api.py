"""Client helpers for interacting with the analysis DB via IPC."""

from typing import Dict
import ast
from pathlib import Path
import os
import socket
import threading
import time

from ipc_bus.message_api import send_request
from ipc_bus.bus_integrity import is_alias_approved
from ipc_bus.bus_init import _parse_sock
from .db_init import start_db_server


def _module_code_stats(name: str) -> tuple[int, int]:
    """Return (function_count, line_count) for a module if available."""
    root = Path(__file__).resolve().parents[1]
    for folder in ["recon_modules", "vuln_modules", "offensive_modules", "pipelines"]:
        path = root / folder / f"{name}.py"
        if path.is_file():
            try:
                src = path.read_text(encoding="utf-8")
                tree = ast.parse(src)
                funcs = sum(isinstance(n, ast.FunctionDef) for n in ast.walk(tree))
                lines = src.count("\n") + 1
                return funcs, lines
            except Exception:
                return 0, 0
    return 0, 0


def log_scan_result(sock_path: str, result: Dict) -> Dict:
    alias = "scan"
    if not is_alias_approved(alias):
        raise ValueError("Alias not approved")
    if "module" in result:
        funcs, lines = _module_code_stats(result["module"])
        result.setdefault("code_funcs", funcs)
        result.setdefault("code_lines", lines)
    payload = {"alias": alias, "result": result}
    return _request(sock_path, payload)


def generate_report(sock_path: str, out_dir: str = "reports", fmt: str = "md", template: str | None = None) -> Dict:
    """Request the database server to generate a report."""
    alias = "report"
    if not is_alias_approved(alias):
        raise ValueError("Alias not approved")
    payload = {"alias": alias, "out_dir": out_dir, "format": fmt}
    if template:
        payload["template"] = template
    return _request(sock_path, payload)


def get_results(sock_path: str, limit: int = 0) -> Dict:
    """Retrieve stored scan results from the DB."""
    alias = "results"
    if not is_alias_approved(alias):
        raise ValueError("Alias not approved")
    payload = {"alias": alias, "limit": limit}
    return _request(sock_path, payload)


def search_results(sock_path: str, tag: str, limit: int = 0) -> Dict:
    """Retrieve stored results matching a tag."""
    alias = "search"
    if not is_alias_approved(alias):
        raise ValueError("Alias not approved")
    payload = {"alias": alias, "tag": tag, "limit": limit}
    return _request(sock_path, payload)


def purge_results(sock_path: str, limit: int) -> Dict:
    """Trim stored results to the latest ``limit`` entries."""
    alias = "purge"
    if not is_alias_approved(alias):
        raise ValueError("Alias not approved")
    payload = {"alias": alias, "limit": limit}
    return _request(sock_path, payload)


def ask_question(sock_path: str, question: str, limit: int = 5) -> Dict:
    """Ask ChatGPT a question about stored results."""
    alias = "chat"
    if not is_alias_approved(alias):
        raise ValueError("Alias not approved")
    payload = {"alias": alias, "question": question, "limit": limit}
    return _request(sock_path, payload)


def plan_pipeline(sock_path: str, limit: int = 5) -> Dict:
    """Ask ChatGPT for a pipeline recommendation."""
    alias = "plan"
    if not is_alias_approved(alias):
        raise ValueError("Alias not approved")
    payload = {"alias": alias, "limit": limit}
    return _request(sock_path, payload)


def train_model(sock_path: str) -> Dict:
    """Trigger neural model retraining on the server."""
    alias = "train"
    if not is_alias_approved(alias):
        raise ValueError("Alias not approved")
    payload = {"alias": alias}
    return _request(sock_path, payload)


def train_model_cve(sock_path: str, path: str) -> Dict:
    """Train neural model using CVE dataset."""
    alias = "train_cve"
    if not is_alias_approved(alias):
        raise ValueError("Alias not approved")
    payload = {"alias": alias, "path": path}
    return _request(sock_path, payload)


def train_model_success(sock_path: str, path: str) -> Dict:
    """Reinforce neural model using successful cases."""
    alias = "train_success"
    if not is_alias_approved(alias):
        raise ValueError("Alias not approved")
    payload = {"alias": alias, "path": path}
    return _request(sock_path, payload)


def suggest_modules_api(sock_path: str, limit: int = 5, prev: str | None = None) -> Dict:
    """Request module recommendations from the DB server."""
    alias = "modules"
    if not is_alias_approved(alias):
        raise ValueError("Alias not approved")
    payload = {"alias": alias, "limit": limit}
    if prev:
        payload["prev"] = prev
    return _request(sock_path, payload)


def suggest_params_api(sock_path: str, module: str, limit: int = 50) -> Dict:
    """Request parameter recommendations for a module."""
    alias = "params"
    if not is_alias_approved(alias):
        raise ValueError("Alias not approved")
    payload = {"alias": alias, "module": module, "limit": limit}
    return _request(sock_path, payload)


def get_stats(sock_path: str) -> Dict:
    """Retrieve simple statistics about stored results."""
    alias = "stats"
    if not is_alias_approved(alias):
        raise ValueError("Alias not approved")
    payload = {"alias": alias}
    return _request(sock_path, payload)


def operator_action(sock_path: str, action: str, value: str | float | None = None) -> Dict:
    """Send an operator command to the DB server."""
    alias = "operator"
    if not is_alias_approved(alias):
        raise ValueError("Alias not approved")
    payload = {"alias": alias, "action": action}
    if value is not None:
        payload["value"] = value
    return _request(sock_path, payload)


def explore_module_api(sock_path: str, module: str, doc: str, limit: int = 3) -> Dict:
    """Request example commands for a module from the DB server."""
    alias = "explore"
    if not is_alias_approved(alias):
        raise ValueError("Alias not approved")
    payload = {"alias": alias, "module": module, "doc": doc, "limit": limit}
    return _request(sock_path, payload)


def _ensure_db(sock_path: str) -> None:
    family, addr = _parse_sock(sock_path)
    try:
        with socket.socket(family, socket.SOCK_STREAM) as s:
            s.connect(addr)
            return
    except OSError:
        pass
    db_dir = os.environ.get("MINC_DB_DIR", "db_data")
    t = threading.Thread(target=start_db_server, args=(db_dir, sock_path), daemon=True)
    t.start()
    time.sleep(0.1)


def _request(sock_path: str, payload: Dict) -> Dict:
    try:
        return send_request(sock_path, payload)
    except OSError:
        _ensure_db(sock_path)
        return send_request(sock_path, payload)

