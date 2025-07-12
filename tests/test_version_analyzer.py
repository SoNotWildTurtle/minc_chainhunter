import subprocess


def test_version_analyzer_runs():
    out = subprocess.check_output(['python3', 'version_analyzer.py', '--count', '1'], text=True)
    assert 'Recommended version' in out
