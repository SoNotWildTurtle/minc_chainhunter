import os
import subprocess
import threading
import time
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis_db.db_init import start_db_server


def test_port_scan_pipeline(tmp_path):
    sock = tmp_path / "db.sock"
    db_dir = tmp_path / "data"

    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), False), daemon=True)
    t.start()
    time.sleep(0.1)
    env = os.environ.copy()
    env["MINC_DB_SOCKET"] = str(sock)
    env["SKIP_CLONE"] = "1"
    proc = subprocess.run(
        [sys.executable, "cli/main.py", "run", "port_scan", "127.0.0.1"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 0
    with open(db_dir / "results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    entry = data[-1]
    assert entry["module"] == "port_scan"
    steps = entry.get("steps", [])
    step_names = {s["module"] for s in steps}
    assert {"masscan_scan", "nmap_scan"} <= step_names
