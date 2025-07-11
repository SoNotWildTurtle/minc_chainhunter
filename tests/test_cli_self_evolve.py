import subprocess
import sys
import os


def test_cli_self_evolve():
    proc = subprocess.run([sys.executable, 'cli/main.py', 'self-evolve'], capture_output=True, text=True)
    assert proc.returncode == 0
    assert 'self-evolution' in proc.stdout.lower()
    assert 'pipeline' in proc.stdout.lower()


def test_cli_self_evolve_heal():
    env = dict(os.environ)
    env['FAST_HEAL'] = '1'
    proc = subprocess.run([sys.executable, 'cli/main.py', 'self-evolve', '--heal'], capture_output=True, text=True, env=env)
    assert proc.returncode == 0
    assert 'self-healing' in proc.stdout.lower() or 'self-heal' in proc.stdout.lower()
