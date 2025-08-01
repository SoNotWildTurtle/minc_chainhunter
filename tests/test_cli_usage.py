import subprocess
import sys


def test_cli_usage():
    proc = subprocess.run([sys.executable, 'cli/main.py', 'usage', 'ping_sweep'], capture_output=True, text=True)
    assert 'usage:' in proc.stdout.lower()
