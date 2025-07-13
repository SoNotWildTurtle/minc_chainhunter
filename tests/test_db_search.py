import os
import threading
import time
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis_db.db_init import start_db_server
from analysis_db.db_api import log_scan_result, search_results


def test_search_results(tmp_path):
    sock = tmp_path / "db.sock"
    db_dir = tmp_path / "data"

    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    log_scan_result(str(sock), {"target": "tagged.com", "tags": ["findme"]})
    t.join()

    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    resp = search_results(str(sock), "findme")
    t.join()

    assert resp["status"] == "ok"
    assert resp["results"] and resp["results"][0]["target"] == "tagged.com"
