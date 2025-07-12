import subprocess
import sys
import os


def test_cli_self_heal():
    env = dict(os.environ)
    env['FAST_HEAL'] = '1'
    proc = subprocess.run([sys.executable, 'cli/main.py', 'self-heal'], capture_output=True, text=True, env=env)
    assert proc.returncode == 0
    out = proc.stdout.lower() + proc.stderr.lower()
    assert 'fast_heal' in out or 'self-heal' in out
