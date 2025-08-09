import os
import subprocess
import sys
from pathlib import Path

def test_create_manager(tmp_path):
    d = tmp_path / "mods"
    d.mkdir()
    script = Path(__file__).resolve().parent.parent / 'scripts' / 'create_manager.py'
    proc = subprocess.run([sys.executable, str(script), str(d), '--kind', 'recon'], capture_output=True, text=True)
    assert proc.returncode == 0
    manager = d / 'manager.py'
    assert manager.exists()
    # ensure generated script lists modules
    (d / 'foo.py').write_text('def main():\n    print("foo")\n')
    list_proc = subprocess.run([sys.executable, str(manager), 'list'], capture_output=True, text=True)
    assert 'foo' in list_proc.stdout

    funcs_proc = subprocess.run([sys.executable, str(manager), 'funcs', 'foo'], capture_output=True, text=True)
    assert 'main' in funcs_proc.stdout
