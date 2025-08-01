import os
import sys
import subprocess
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis_db.db_init import start_db_server


def test_cli_explore(tmp_path, monkeypatch):
    sock = tmp_path / "db.sock"
    db_dir = tmp_path / "data"

    class FakeCompletion:
        @staticmethod
        def create(model, messages, max_tokens):
            return {"choices": [{"message": {"content": "cmd1\ncmd2"}}]}

    fake_openai = type("openai", (), {"ChatCompletion": FakeCompletion})
    monkeypatch.setitem(sys.modules, "openai", fake_openai)
    monkeypatch.setenv("OPENAI_API_KEY", "x")

    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    env = os.environ.copy()
    env["MINC_DB_SOCKET"] = str(sock)
    proc = subprocess.run([sys.executable, "cli/main.py", "explore", "ping_sweep", "-n", "2"], capture_output=True, text=True, env=env)
    t.join()

    assert proc.returncode == 0
    assert "cmd1" in proc.stdout
