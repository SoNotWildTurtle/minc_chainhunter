import subprocess
import sys
from pathlib import Path


def test_create_module(tmp_path):
    script = Path(__file__).resolve().parent.parent / 'scripts' / 'create_module.py'
    proc = subprocess.run([sys.executable, str(script), 'recon', 'foo', '--root', str(tmp_path)], capture_output=True, text=True)
    assert proc.returncode == 0
    mod_file = tmp_path / 'recon_modules' / 'foo_scan.py'
    assert mod_file.exists()
    content = mod_file.read_text()
    assert 'def main' in content
