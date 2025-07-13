import os
import subprocess


def test_install_requirements(tmp_path):
    env = os.environ.copy()
    env['SKIP_INSTALL'] = '1'
    subprocess.run(['python3', 'scripts/install_requirements.py'], env=env, check=True)
