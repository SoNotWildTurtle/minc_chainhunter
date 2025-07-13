import os
import json
import subprocess
from pathlib import Path


def test_self_healing(tmp_path):
    db_dir = tmp_path / "data"
    db_dir.mkdir()
    results = [{"target": "example.com", "status": "ok"}]
    with open(db_dir / "results.json", "w", encoding="utf-8") as f:
        json.dump(results, f)

    env = os.environ.copy()
    env['SKIP_CLONE'] = '1'
    subprocess.check_call(['bash', 'scripts/install_scanner_repos.sh'], env=env)

    with open(db_dir / "results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == results

    # ensure directories created
    for name in ['gitleaks', 'ssrfmap', 'nuclei']:
        path = Path('github_scanners') / name / 'src'
        assert path.exists()
