import os
import sys
import subprocess


def test_cli_notes(tmp_path):
    notes = tmp_path / 'notes.dat'
    env = os.environ.copy()
    env['DEV_NOTES_PATH'] = str(notes)

    proc = subprocess.run([
        sys.executable,
        'cli/main.py',
        'notes', 'add', 'test entry', '--tags', 't1'
    ], capture_output=True, text=True, env=env)
    assert proc.returncode == 0

    proc = subprocess.run([
        sys.executable,
        'cli/main.py',
        'notes', 'show', '-n', '1'
    ], capture_output=True, text=True, env=env)
    assert proc.returncode == 0
    assert 'test entry' in proc.stdout
