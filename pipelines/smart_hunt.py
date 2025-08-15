import importlib
import os
import sys
from typing import List, Dict

from analysis_db.db_api import get_results
from analysis_db.neural_analyzer import suggest_pipeline


def main(argv: List[str] | None = None) -> Dict | bool:
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: smart_hunt.py <target>")
        return False
    target = argv[0]
    sock = os.environ.get("MINC_DB_SOCKET")
    recent = []
    if sock:
        try:
            resp = get_results(sock, limit=5)
            recent = resp.get("results", [])
        except Exception:
            pass
    pipeline = os.environ.get("MINC_OVERRIDE_PIPELINE")
    if not pipeline:
        pipeline = suggest_pipeline(recent)
    mod = importlib.import_module(f"pipelines.{pipeline}")
    summary = mod.main([target])
    return {"pipeline": pipeline, **(summary or {})}


if __name__ == "__main__":
    res = main()
    if isinstance(res, dict):
        print(res)
