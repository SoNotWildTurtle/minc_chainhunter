import os
import sys
import subprocess
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis_db.db_init import start_db_server
from analysis_db.db_api import log_scan_result


def test_cli_suggest_mods(tmp_path):
    sock = tmp_path / "db.sock"
    db_dir = tmp_path / "data"

    # log two results
    for result in [
        {"module": "ping_sweep", "ports": [80]},
        {"module": "sqli_scanner", "ports": [80], "severity": "high"},
    ]:
        t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
        t.start()
        time.sleep(0.1)
        log_scan_result(str(sock), result)
        t.join()

    # request suggestions
    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    env = os.environ.copy()
    env["MINC_DB_SOCKET"] = str(sock)
    proc = subprocess.run([sys.executable, "cli/main.py", "suggest-mods", "-n", "2"], capture_output=True, text=True, env=env)
    t.join()

    assert proc.returncode == 0
    assert "sqli_scanner" in proc.stdout

    # follow-up suggestions after ping_sweep
    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    env = os.environ.copy()
    env["MINC_DB_SOCKET"] = str(sock)
    proc2 = subprocess.run(
        [sys.executable, "cli/main.py", "suggest-mods", "--after", "ping_sweep"],
        capture_output=True,
        text=True,
        env=env,
    )
    t.join()
    assert proc2.returncode == 0
    assert "sqli_scanner" in proc2.stdout
