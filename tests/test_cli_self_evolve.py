import subprocess
import sys


def test_cli_self_evolve():
    proc = subprocess.run([sys.executable, 'cli/main.py', 'self-evolve'], capture_output=True, text=True)
    assert proc.returncode == 0
    assert 'self-evolution' in proc.stdout.lower()
