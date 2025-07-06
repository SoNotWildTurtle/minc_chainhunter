import os
import threading
import time
import json
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis_db.db_init import start_db_server
from analysis_db.db_api import log_scan_result, get_results, purge_results


def test_purge_results(tmp_path):
    sock = tmp_path / "db.sock"
    db_dir = tmp_path / "data"

    for name in ["a", "b", "c"]:
        t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
        t.start()
        time.sleep(0.1)
        log_scan_result(str(sock), {"target": name})
        t.join()

    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    resp = purge_results(str(sock), 1)
    t.join()
    assert resp["status"] == "ok"

    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    resp = get_results(str(sock))
    t.join()
    assert len(resp.get("results", [])) == 1
    assert resp["results"][0]["target"] == "c"
