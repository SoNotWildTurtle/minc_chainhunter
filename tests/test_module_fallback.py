import os
import json
import types
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from analysis_db.db_api import log_scan_result
from cli import main as cm


def test_auto_start_db(tmp_path):
    sock = tmp_path / "db.sock"
    db_dir = tmp_path / "data"
    os.environ["MINC_DB_DIR"] = str(db_dir)
    resp = log_scan_result(str(sock), {"target": "auto"})
    assert resp["status"] == "ok"
    with open(db_dir / "results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data[0]["target"] == "auto"
    os.environ.pop("MINC_DB_DIR", None)


def test_run_module_self_heal(monkeypatch):
    attempts = {"n": 0}

    def fake_load(name):
        if attempts["n"] == 0:
            attempts["n"] += 1
            raise RuntimeError("boom")
        return types.SimpleNamespace(main=lambda: True)

    monkeypatch.setattr(cm, "load_module", fake_load)

    import scripts.self_heal as sh

    calls = {"n": 0}

    def fake_heal(repo_dir=None):
        calls["n"] += 1
        return True

    monkeypatch.setattr(sh, "run_self_heal", fake_heal)
    os.environ.pop("MINC_HEALED", None)
    assert cm.run_module("demo", []) is True
    assert calls["n"] == 1
