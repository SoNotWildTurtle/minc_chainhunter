"""Wrapper for running sqlmap from the bundled scanner repo."""
from __future__ import annotations

import os
from typing import List


def build_sqlmap_cmd(target: str, options: str | None = None) -> List[str]:
    script = os.path.join(os.path.dirname(__file__), "..", "github_scanners", "sqlmap", "run.sh")
    cmd = ["bash", script, "-u", target]
    if options:
        cmd.extend(options.split())
    return cmd


def run_sqlmap(target: str, options: str | None = None) -> dict:
    cmd = build_sqlmap_cmd(target, options)
    return {
        "module": "sqlmap_scan",
        "target": target,
        "command": cmd,
        "reachable": False,
        "output": "",
    }
