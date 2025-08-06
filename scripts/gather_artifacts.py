#!/usr/bin/env python3
"""Gather proof-of-concept artifacts from stored results."""

import argparse
import json
import os
from typing import Dict, Any

from analysis_db.report_gen import load_results


def _collect(entry: Dict[str, Any], base: str, prefix: str) -> None:
    raw = entry.get("raw")
    if raw:
        path = os.path.join(base, f"{prefix}_raw.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(raw, f, indent=2)
    for idx, step in enumerate(entry.get("steps") or []):
        _collect(step, base, f"{prefix}_s{idx}")


def gather_artifacts(db_dir: str, out_dir: str = "artifacts") -> str:
    """Gather raw data from stored results into files."""
    results = load_results(db_dir)
    os.makedirs(out_dir, exist_ok=True)
    for i, entry in enumerate(results):
        prefix = f"{i}_{entry.get('module', 'unknown')}"
        _collect(entry, out_dir, prefix)
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Gather proof-of-concept artifacts")
    parser.add_argument("--db_dir", default="db_data")
    parser.add_argument("--out_dir", default="artifacts")
    args = parser.parse_args()
    path = gather_artifacts(args.db_dir, args.out_dir)
    print(f"[+] Artifacts written to {path}")


if __name__ == "__main__":
    main()
