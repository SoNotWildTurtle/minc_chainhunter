import os
import subprocess
import sys

SCRIPT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sandbox', 'main_app', 'run_main.sh')


def test_run_main_script_lists_modules():
    result = subprocess.run(['bash', SCRIPT, 'list'], capture_output=True, text=True)
    assert 'ping_sweep' in result.stdout
