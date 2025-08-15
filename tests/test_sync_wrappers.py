import os
import subprocess
import sys
from pathlib import Path


def test_sync_scanner_wrappers(tmp_path):
    repo_root = Path(__file__).resolve().parent.parent
    env = os.environ.copy()
    proc = subprocess.run([
        sys.executable,
        str(repo_root / 'scripts' / 'sync_scanner_wrappers.py'),
        '--root', str(tmp_path)
    ], capture_output=True, text=True)
    assert proc.returncode == 0
    # Should create at least one wrapper file
    files = list(tmp_path.rglob('*_scan.py'))
    assert files
