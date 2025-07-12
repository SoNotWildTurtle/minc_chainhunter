import os
import subprocess
import sys

def test_install_service(tmp_path):
    service_dir = tmp_path / "systemd"
    env = os.environ.copy()
    env["SYSTEMD_USER_DIR"] = str(service_dir)
    env["NO_SYSTEMCTL"] = "1"
    subprocess.run(["bash", "scripts/install_service.sh"], env=env, check=True)
    svc = service_dir / "chainhunter.service"
    timer = service_dir / "chainhunter.timer"
    assert svc.exists()
    assert timer.exists()
    text = svc.read_text()
    assert "ExecStart" in text

