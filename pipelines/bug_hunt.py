"""Simple bug hunting pipeline example."""

import importlib
import sys
from typing import List, Dict

STEPS = [
    ("ping_sweep", "recon_modules.ping_sweep"),
    ("sqli_scanner", "vuln_modules.sqli_scanner"),
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
        print("Usage: bug_hunt.py <target>")
        return False
    target = argv[0]
    results = []
    for name, path in STEPS:
        res = run_step(name, path, target)
        if res:
            results.append(res)
    return {"target": target, "steps": results}


if __name__ == "__main__":
    main()
