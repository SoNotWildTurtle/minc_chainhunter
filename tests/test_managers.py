import os
import sys
import subprocess


def test_recon_manager_lists_modules(tmp_path):
    proc = subprocess.run([sys.executable, 'recon_modules/manager.py', 'list'], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
    assert 'ping_sweep' in proc.stdout
    assert 'theharvester_scan' in proc.stdout
    assert 'amass_scan' in proc.stdout
    assert 'masscan_scan' in proc.stdout
    assert 'aquatone_scan' in proc.stdout
    vuln_proc = subprocess.run([
        sys.executable,
        'vuln_modules/manager.py',
        'list'
    ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
    assert 'nmap_scan' in vuln_proc.stdout
    assert 'git_dumper_scan' in vuln_proc.stdout

    off_proc = subprocess.run([
        sys.executable,
        'offensive_modules/manager.py',
        'list'
    ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
    assert 'mythic_control' in off_proc.stdout


def test_pipeline_manager_lists_modules(tmp_path):
    proc = subprocess.run([
        sys.executable,
        'pipelines/manager.py',
        'list'
    ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
    assert 'bug_hunt' in proc.stdout


def test_scanner_manager_info(tmp_path):
    repo_root = os.path.dirname(__file__) + '/..'
    proc = subprocess.run([
        sys.executable,
        'github_scanners/manager.py',
        'info',
        'ssrfmap'
    ], capture_output=True, text=True, cwd=repo_root)
    assert 'ssrfmap' in proc.stdout


def test_manager_funcs_and_call(tmp_path):
    repo_root = os.path.dirname(__file__) + '/..'
    proc = subprocess.run([
        sys.executable,
        'vuln_modules/manager.py',
        'funcs',
        'gitleaks_scan'
    ], capture_output=True, text=True, cwd=repo_root)
    assert 'build_gitleaks_cmd' in proc.stdout

    call_proc = subprocess.run([
        sys.executable,
        'vuln_modules/manager.py',
        'call',
        'gitleaks_scan',
        'build_gitleaks_cmd',
        '/tmp/repo'
    ], capture_output=True, text=True, cwd=repo_root)
    assert '/tmp/repo' in call_proc.stdout

    rec_proc = subprocess.run([
        sys.executable,
        'vuln_modules/manager.py',
        'recommend',
        'gitleaks_scan',
        '-n', '1'
    ], capture_output=True, text=True, cwd=repo_root)
    assert rec_proc.returncode == 0

    help_proc = subprocess.run([
        sys.executable,
        'recon_modules/manager.py',
        'help',
        'ping_sweep'
    ], capture_output=True, text=True, cwd=repo_root)
    assert 'usage' in help_proc.stdout.lower()
