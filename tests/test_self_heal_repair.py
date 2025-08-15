import json
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.self_heal import run_self_heal


def test_self_heal_repairs_corrupt_results():
    repo = Path.cwd()
    db_dir = repo / 'db_data'
    if db_dir.exists():
        shutil.rmtree(db_dir)
    db_dir.mkdir()
    (db_dir / 'results.json').write_text('corrupt')
    os.environ['FAST_HEAL'] = '1'
    os.environ['SKIP_CLONE'] = '1'
    os.environ['SKIP_INSTALL'] = '1'
    run_self_heal(str(repo))
    data_path = db_dir / 'results.json'
    backup_path = db_dir / 'results.json.bak'
    assert data_path.exists()
    assert json.loads(data_path.read_text()) == []
    assert backup_path.exists()
    shutil.rmtree(db_dir)
