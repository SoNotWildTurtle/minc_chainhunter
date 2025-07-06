import os
import sys
import subprocess
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis_db.db_init import start_db_server
from analysis_db.db_api import log_scan_result


def test_cli_chat(tmp_path):
    sock = tmp_path / "db.sock"
    db_dir = tmp_path / "data"

    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    log_scan_result(str(sock), {"target": "chat.com", "ports": [80]})
    t.join()

    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    env = os.environ.copy()
    env["MINC_DB_SOCKET"] = str(sock)
    proc = subprocess.run([sys.executable, "cli/main.py", "chat", "What's up?", "-n", "1"], capture_output=True, text=True, env=env)
    t.join()

    assert proc.returncode == 0
    assert "ChatGPT" in proc.stdout or "OPENAI_API_KEY" in proc.stdout
