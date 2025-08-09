import os
import threading
import time
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis_db.db_init import start_db_server
from analysis_db.db_api import log_scan_result
from analysis_db.report_gen import load_results


def test_db_hmac_integrity(tmp_path, monkeypatch):
    sock = tmp_path / "ipc.sock"
    db_dir = tmp_path / "data"
    monkeypatch.setenv("MINC_HMAC_KEY", "secret")

    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    log_scan_result(str(sock), {"target": "host"})
    t.join()

    sig_file = db_dir / "results.json.sig"
    assert sig_file.exists()

    with open(db_dir / "results.json", "ab") as f:
        f.write(b"tamper")

    records = load_results(str(db_dir))
    assert records == []
    monkeypatch.delenv("MINC_HMAC_KEY", raising=False)
