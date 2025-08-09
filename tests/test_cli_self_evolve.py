import subprocess
import sys
import os
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from analysis_db.db_init import start_db_server


def test_cli_self_evolve(tmp_path):
    sock = tmp_path / 'db.sock'
    db_dir = tmp_path / 'data'
    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), False), daemon=True)
    t.start()
    time.sleep(0.1)
    env = dict(os.environ)
    env['MINC_DB_SOCKET'] = str(sock)
    proc = subprocess.run([sys.executable, 'cli/main.py', 'self-evolve'], capture_output=True, text=True, env=env)
    assert proc.returncode == 0
    out = proc.stdout.lower()
    assert 'self-evolution' in out
    assert 'pipeline' in out
    assert 'recommended module' in out


def test_cli_self_evolve_heal():
    env = dict(os.environ)
    env['FAST_HEAL'] = '1'
    proc = subprocess.run([sys.executable, 'cli/main.py', 'self-evolve', '--heal'], capture_output=True, text=True, env=env)
    assert proc.returncode == 0
    assert 'self-healing' in proc.stdout.lower() or 'self-heal' in proc.stdout.lower()


def test_cli_self_evolve_patch(tmp_path):
    script = tmp_path / 'patch.py'
    script.write_text("print('patched')")
    proc = subprocess.run([sys.executable, 'cli/main.py', 'self-evolve', '--patch', str(script)], capture_output=True, text=True)
    assert proc.returncode == 0
    assert 'patch script' in proc.stdout.lower()


def test_cli_self_evolve_iterations(tmp_path):
    sock = tmp_path / 'db.sock'
    db_dir = tmp_path / 'data'
    t = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), False), daemon=True)
    t.start()
    time.sleep(0.1)
    env = dict(os.environ)
    env['MINC_DB_SOCKET'] = str(sock)
    proc = subprocess.run(
        [sys.executable, 'cli/main.py', 'self-evolve', '--iter', '2'],
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 0
    assert 'iteration 2/2' in proc.stdout

