import os
import sys
import subprocess
import threading
import time
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis_db.db_init import start_db_server


def test_cli_train_cve(tmp_path):
    sock = tmp_path / "db.sock"
    db_dir = tmp_path / "data"

    dataset = tmp_path / "cve.json"
    json.dump([
        {"ports": [80], "severity": "high", "vuln_count": 2, "tags": ["web"], "pipeline": "extended_hunt"}
    ], open(dataset, "w"))

    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    env = os.environ.copy()
    env["MINC_DB_SOCKET"] = str(sock)
    proc = subprocess.run([sys.executable, "cli/main.py", "train-cve", str(dataset)], capture_output=True, text=True, env=env)
    t.join()

    assert proc.returncode == 0
    assert "CVE data" in proc.stdout
