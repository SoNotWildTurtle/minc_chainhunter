import os
import threading
import time
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis_db.db_init import start_db_server
from analysis_db.db_api import log_scan_result, get_results, generate_report
from ipc_bus.message_api import send_request


def test_db_alias_commands(tmp_path):
    sock = tmp_path / "db.sock"
    db_dir = tmp_path / "data"
    out_dir = tmp_path / "reports"

    # start server and log result via approved alias
    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    res = {"target": "alias.com", "ok": True}
    resp = log_scan_result(str(sock), res)
    t.join()
    assert resp["status"] == "ok"

    # get results via alias
    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    resp = get_results(str(sock))
    t.join()
    assert resp["status"] == "ok"
    assert resp["results"][0]["target"] == "alias.com"

    # search results via alias
    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    resp = send_request(str(sock), {"alias": "search", "tag": "test"})
    t.join()
    assert resp["status"] == "ok"

    # generate report via alias
    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    resp = generate_report(str(sock), str(out_dir))
    t.join()
    assert resp["status"] == "ok"
    assert os.path.isfile(resp["path"])

    # unapproved alias should fail
    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    resp = send_request(str(sock), {"alias": "rm -rf"})
    t.join()
    assert resp["status"] == "error"
