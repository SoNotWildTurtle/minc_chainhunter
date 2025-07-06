import importlib
import os
import sys
from typing import List, Dict

from analysis_db.db_api import log_scan_result

STEPS = [
    ("gitleaks_scan", "vuln_modules.gitleaks_scan"),
    ("trufflehog_scan", "vuln_modules.trufflehog_scan"),
]


def run_step(mod_name: str, module_path: str, target: str) -> Dict:
    mod = importlib.import_module(module_path)
    sys.argv = [mod_name, target]
    if hasattr(mod, "main"):
        res = mod.main()
        if isinstance(res, dict):
            res["module"] = mod_name
            return res
    return {}


def main(argv: List[str] | None = None):
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: repo_hunt.py <repo-path>")
        return False
    target = argv[0]
    results = []
    for name, path in STEPS:
        res = run_step(name, path, target)
        if res:
            results.append(res)
    return {"target": target, "steps": results}


if __name__ == "__main__":
    summary = main()
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {"module": "repo_hunt", **summary})
        except Exception:
            pass

