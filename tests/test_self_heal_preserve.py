import os
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.self_heal import run_self_heal


def test_self_heal_preserves_data(tmp_path):
    repo = Path.cwd()
    db_dir = repo / 'db_data'
    if db_dir.exists():
        shutil.rmtree(db_dir)
    db_dir.mkdir()
    results_file = db_dir / 'results.json'
    sample = [{"target": "host", "status": "ok"}]
    results_file.write_text(json.dumps(sample))

    scanner = repo / 'github_scanners' / 'gitleaks' / 'src'
    if scanner.exists():
        shutil.rmtree(scanner)
    assert not scanner.exists()

    os.environ['FAST_HEAL'] = '1'
    os.environ['SKIP_CLONE'] = '1'
    run_self_heal(str(repo))

    assert json.loads(results_file.read_text()) == sample
    assert scanner.exists()

    shutil.rmtree(db_dir)
