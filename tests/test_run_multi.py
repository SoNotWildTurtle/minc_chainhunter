import os
import subprocess
import threading
import time
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis_db.db_init import start_db_server


def test_run_multi(tmp_path):
    sock = tmp_path / "db.sock"
    db_dir = tmp_path / "data"

    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), False), daemon=True)
    t.start()
    time.sleep(0.1)
    env = os.environ.copy()
    env["MINC_DB_SOCKET"] = str(sock)
    proc = subprocess.run(
        [sys.executable, "cli/main.py", "run", "ping_sweep", "--targets", "127.0.0.1", "localhost", "--workers", "2"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 0
    with open(db_dir / "results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    # expect at least two ping_sweep entries
    modules = [entry["module"] for entry in data if entry["module"] == "ping_sweep"]
    assert len(modules) >= 2
