import os
import sys
import subprocess


def test_recon_manager_lists_modules(tmp_path):
    proc = subprocess.run([sys.executable, 'recon_modules/manager.py', '--list'], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
    assert 'ping_sweep' in proc.stdout
    assert 'theharvester_scan' in proc.stdout
    assert 'amass_scan' in proc.stdout
    assert 'masscan_scan' in proc.stdout
    assert 'aquatone_scan' in proc.stdout
    vuln_proc = subprocess.run([
        sys.executable,
        'vuln_modules/manager.py',
        '--list'
    ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
    assert 'nmap_scan' in vuln_proc.stdout
    assert 'git_dumper_scan' in vuln_proc.stdout

    off_proc = subprocess.run([
        sys.executable,
        'offensive_modules/manager.py',
        '--list'
    ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
    assert 'mythic_control' in off_proc.stdout


def test_pipeline_manager_lists_modules(tmp_path):
    proc = subprocess.run([
        sys.executable,
        'pipelines/manager.py',
        '--list'
    ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
    assert 'bug_hunt' in proc.stdout
