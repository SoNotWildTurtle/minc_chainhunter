import os
import subprocess
import threading
import time
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis_db.db_init import start_db_server


def test_smart_hunt_pipeline(tmp_path):
    sock = tmp_path / "db.sock"
    db_dir = tmp_path / "data"

    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), False), daemon=True)
    t.start()
    time.sleep(0.1)
    env = os.environ.copy()
    env["MINC_DB_SOCKET"] = str(sock)
    env["MINC_OVERRIDE_PIPELINE"] = "bug_hunt"
    proc = subprocess.run(
        [sys.executable, "cli/main.py", "run", "smart_hunt", "example.com"],
        capture_output=True,
        text=True,
        env=env,
    )
    # server thread continues

    assert proc.returncode == 0
    with open(db_dir / "results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    entry = data[-1]
    assert entry["module"] == "smart_hunt"
    assert entry["pipeline"] == "bug_hunt"
    steps = entry.get("steps", [])
    step_names = {s["module"] for s in steps}
    assert {"ping_sweep", "sqli_scanner"} <= step_names
