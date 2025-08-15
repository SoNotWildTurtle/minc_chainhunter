import os
import sys
import subprocess
import threading
import time
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis_db.db_init import start_db_server
from analysis_db.db_api import log_scan_result


def test_cli_stats(tmp_path):
    sock = tmp_path / "db.sock"
    db_dir = tmp_path / "data"

    # first result contains a vulnerability
    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    log_scan_result(str(sock), {"module": "ping_sweep", "vulnerabilities": [{}]})
    t.join()

    # second result has none
    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    log_scan_result(str(sock), {"module": "ping_sweep"})
    t.join()

    # fetch stats via CLI
    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    env = os.environ.copy()
    env["MINC_DB_SOCKET"] = str(sock)
    proc = subprocess.run([sys.executable, "cli/main.py", "stats"], capture_output=True, text=True, env=env)
    t.join()

    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data["module_success"]["ping_sweep"]["runs"] == 2
    assert data["module_success"]["ping_sweep"]["vuln"] == 1
