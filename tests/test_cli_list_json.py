import subprocess, sys, json

def test_cli_list_json():
    proc = subprocess.run([sys.executable, 'cli/main.py', 'list', '--json'], capture_output=True, text=True)
    data = json.loads(proc.stdout)
    assert 'recon' in data
    assert 'ping_sweep' in data['recon']
