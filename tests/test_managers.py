import os
import sys
import subprocess
import threading
import time
from analysis_db.db_init import start_db_server


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


def test_manager_best_run(tmp_path):
    repo_root = os.path.dirname(__file__) + '/..'
    sock = tmp_path / 'db.sock'
    data_dir = tmp_path / 'data'

    t = threading.Thread(target=start_db_server, args=(str(data_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    from analysis_db.db_api import log_scan_result
    log_scan_result(str(sock), {'module': 'ping_sweep', 'params': ['127.0.0.1']})
    t.join()

    t = threading.Thread(target=start_db_server, args=(str(data_dir), str(sock), True))
    t.start()
    time.sleep(0.1)
    env = os.environ.copy()
    env['MINC_DB_SOCKET'] = str(sock)
    proc = subprocess.run([
        sys.executable,
        'recon_modules/manager.py',
        'best',
        'ping_sweep',
        '-n', '1'
    ], capture_output=True, text=True, cwd=repo_root, env=env)
    t.join()
    assert proc.returncode == 0
