import os
import json
import threading
import time

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis_db.db_init import start_db_server
from analysis_db.db_api import log_scan_result, get_results


def test_db_logging(tmp_path):
    sock = tmp_path / "db.sock"
    db_dir = tmp_path / "data"

    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)

    res = {"target": "example.com", "reachable": True}
    log_scan_result(str(sock), res)
    t.join()

    with open(db_dir / "results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data[0]["target"] == "example.com"
    assert data[0]["vuln_count"] == 0

    # fetch results via API
    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    resp = get_results(str(sock))
    t.join()
    assert resp["status"] == "ok"
    assert resp["results"][0]["target"] == "example.com"
