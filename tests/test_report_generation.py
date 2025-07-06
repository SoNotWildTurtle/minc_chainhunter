import os
import threading
import time

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis_db.db_init import start_db_server
from analysis_db.db_api import log_scan_result
from analysis_db.db_api import generate_report


def test_report_generation(tmp_path):
    sock = tmp_path / "db.sock"
    db_dir = tmp_path / "data"
    report_dir = tmp_path / "out"

    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    log_scan_result(str(sock), {"target": "example.com", "reachable": True})
    t.join()

    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    resp = generate_report(str(sock), str(report_dir), "json")
    t.join()

    assert resp["status"] == "ok"
    assert os.path.isfile(resp["path"])

    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    resp = generate_report(str(sock), str(report_dir), "pdf")
    t.join()

    assert resp["status"] == "ok"
    assert os.path.isfile(resp["path"])

