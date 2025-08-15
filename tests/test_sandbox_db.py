import os
import time
from pathlib import Path
import subprocess

SCRIPT = Path(__file__).resolve().parents[1] / 'sandbox' / 'manager.sh'


def test_run_db_creates_socket(tmp_path):
    db_dir = tmp_path / 'data'
    sock = tmp_path / 'ipc.sock'
    env = os.environ.copy()
    env.update({
        'MINC_DB_DIR': str(db_dir),
        'MINC_DB_SOCKET': str(sock),
        'MINC_SKIP_NS': '1'
    })
    subprocess.run(['bash', str(SCRIPT), 'run_db'], env=env, check=True)
    # allow server to start
    time.sleep(0.2)
    assert sock.exists()
    pid_file = db_dir / 'db.pid'
    assert pid_file.exists()
    pid = int(pid_file.read_text().strip())
    os.kill(pid, 15)


def test_run_db_chroot(tmp_path):
    chroot = tmp_path / 'root'
    db_dir = '/data'
    sock_path = '/ipc.sock'
    env = os.environ.copy()
    env.update({
        'MINC_DB_CHROOT': str(chroot),
        'MINC_DB_DIR': db_dir,
        'MINC_DB_SOCKET': sock_path,
        'MINC_DB_USER': '',
        'MINC_SKIP_NS': '1'
    })
    subprocess.run(['bash', str(SCRIPT), 'run_db'], env=env, check=True)
    time.sleep(0.2)
    pid_file = chroot / 'data' / 'db.pid'
    assert pid_file.exists()
    pid = int(pid_file.read_text().strip())
    root_link = os.readlink(f'/proc/{pid}/root')
    assert os.path.realpath(root_link) == str(chroot)
    os.kill(pid, 15)
