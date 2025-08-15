import json
import subprocess
import sys
import time
from pathlib import Path


def load_tasks(path: str) -> list[dict]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[!] Task file not found: {path}")
        return []
    except json.JSONDecodeError:
        print(f"[!] Invalid JSON in task file: {path}")
        return []


def run_schedule(path: str) -> None:
    tasks = load_tasks(path)
    for task in tasks:
        args = task.get('args', [])
        if not args:
            continue
        cmd = [sys.executable, 'cli/main.py', *args]
        interval = int(task.get('interval', 0))
        subprocess.run(cmd, check=False)
        if interval:
            time.sleep(interval)


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='Run scheduled ChainHunter tasks')
    p.add_argument('--file', default='tasks.json', help='JSON file of tasks')
    args = p.parse_args()
    run_schedule(args.file)
