import os
import threading
import time
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis_db.db_init import start_db_server
from analysis_db.db_api import log_scan_result
from analysis_db.report_gen import load_results


def test_db_encryption(tmp_path, monkeypatch):
    sock = tmp_path / "ipc.sock"
    db_dir = tmp_path / "data"
    key = b""  # generate key via cryptography
    from cryptography.fernet import Fernet
    key = Fernet.generate_key()
    monkeypatch.setenv("MINC_ENCRYPT_KEY", key.decode())

    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.5)

    log_scan_result(str(sock), {"target": "a", "ok": True})
    t.join()

    # file should not be plain JSON
    with open(db_dir / "results.json", "rb") as f:
        data = f.read()
    assert b"{" not in data[:1]

    # ensure we can decrypt
    records = load_results(str(db_dir))
    assert records[0]["target"] == "a"
    monkeypatch.delenv("MINC_ENCRYPT_KEY", raising=False)
