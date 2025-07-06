import json
import subprocess
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_scheduler_runs(tmp_path):
    tasks = [{"args": ["list"], "interval": 0}]
    task_file = tmp_path / "tasks.json"
    task_file.write_text(json.dumps(tasks))
    proc = subprocess.run(
        [sys.executable, "scripts/scheduler.py", "--file", str(task_file)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
