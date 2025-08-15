import os
import sys
import threading
import time
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis_db.db_init import start_db_server
from analysis_db.db_api import log_scan_result


def test_code_metrics_logged(tmp_path):
    sock = tmp_path / "db.sock"
    data = tmp_path / "data"
    t = threading.Thread(target=start_db_server, args=(str(data), str(sock), True))
    t.start()
    time.sleep(0.1)
    log_scan_result(str(sock), {"module": "ping_sweep"})
    t.join()
    results_file = data / "results.json"
    assert results_file.is_file()
    with open(results_file, "r", encoding="utf-8") as f:
        items = json.load(f)
    entry = items[0]
    assert entry.get("code_lines", 0) > 0
    assert entry.get("code_funcs", 0) > 0
