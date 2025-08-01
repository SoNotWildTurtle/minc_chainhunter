import os
import subprocess
import sys


def test_cli_self_test():
    env = dict(os.environ)
    env['SKIP_CLONE'] = '1'
    proc = subprocess.run([sys.executable, 'cli/main.py', 'self-test'], capture_output=True, text=True, env=env)
    assert proc.returncode == 0
    out = proc.stdout.lower() + proc.stderr.lower()
    assert 'tests passed' in out or 'self-test' in out
