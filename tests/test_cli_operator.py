import os
import sys
import subprocess
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis_db.db_init import start_db_server


def test_cli_operator_tune(tmp_path):
    sock = tmp_path / "db.sock"
    db_dir = tmp_path / "data"
    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    env = os.environ.copy()
    env["MINC_DB_SOCKET"] = str(sock)
    proc = subprocess.run([sys.executable, "cli/main.py", "operator", "tune", "0.8"], capture_output=True, text=True, env=env)
    t.join()
    assert proc.returncode == 0
    assert "Operator action" in proc.stdout


def _run_op(sock, args):
    env = os.environ.copy()
    env["MINC_DB_SOCKET"] = str(sock)
    return subprocess.run([sys.executable, "cli/main.py", *args], capture_output=True, text=True, env=env)


def test_cli_operator_pause_resume(tmp_path):
    sock = tmp_path / "db.sock"
    db_dir = tmp_path / "data"
    t1 = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t1.start()
    time.sleep(0.1)
    proc = _run_op(sock, ["operator", "pause", "job1"])
    t1.join()
    assert proc.returncode == 0
    assert "Operator action" in proc.stdout
    assert (db_dir / "paused").is_file()
    t2 = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t2.start()
    time.sleep(0.1)
    proc2 = _run_op(sock, ["operator", "resume", "job1"])
    t2.join()
    assert proc2.returncode == 0
    assert not (db_dir / "paused").exists()

