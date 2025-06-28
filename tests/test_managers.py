import os
import sys
import subprocess


def test_recon_manager_lists_modules(tmp_path):
    proc = subprocess.run([sys.executable, 'recon_modules/manager.py', '--list'], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
    assert 'ping_sweep' in proc.stdout


def test_pipeline_manager_lists_modules(tmp_path):
    proc = subprocess.run([
        sys.executable,
        'pipelines/manager.py',
        '--list'
    ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
    assert 'bug_hunt' in proc.stdout
