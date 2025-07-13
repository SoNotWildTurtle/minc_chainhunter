import os
import stat
import threading
import time

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis_db.db_init import start_db_server
from analysis_db.db_api import log_scan_result


def test_db_file_permissions(tmp_path):
    sock = tmp_path / "db.sock"
    db_dir = tmp_path / "data"

    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    log_scan_result(str(sock), {"target": "x", "ok": True})
    t.join()

    path = db_dir / "results.json"
    mode = stat.S_IMODE(os.stat(path).st_mode)
    assert mode & 0o077 == 0  # no group/other perms


