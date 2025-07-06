import os
import json
import threading
import time
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis_db.db_init import start_db_server
from analysis_db.db_api import log_scan_result


def test_chatgpt_analysis(tmp_path, monkeypatch):
    sock = tmp_path / "db.sock"
    db_dir = tmp_path / "data"

    class FakeCompletion:
        @staticmethod
        def create(model, messages, max_tokens):
            return {"choices": [{"message": {"content": "summary\nTAG1 TAG2"}}]}

    fake_openai = type("openai", (), {"ChatCompletion": FakeCompletion})
    monkeypatch.setitem(sys.modules, "openai", fake_openai)
    monkeypatch.setenv("OPENAI_API_KEY", "1")

    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)

    log_scan_result(str(sock), {"target": "1.2.3.4", "output": "ports"})
    t.join()

    with open(db_dir / "results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data[0]["summary"] == "summary"
    assert data[0]["tags"] == ["TAG1", "TAG2"]
