import os
import sys
import subprocess
from pathlib import Path

def test_discover_params(tmp_path):
    mod = tmp_path / 'sample.py'
    mod.write_text('import argparse\nparser=argparse.ArgumentParser();\nparser.add_argument("--foo");\nparser.add_argument("-b")\n')
    proc = subprocess.run([sys.executable, 'scripts/discover_params.py', str(mod)], cwd=Path(__file__).resolve().parent.parent, capture_output=True, text=True)
    assert proc.returncode == 0
    out = proc.stdout.strip()
    assert 'foo' in out
    assert 'b' in out
