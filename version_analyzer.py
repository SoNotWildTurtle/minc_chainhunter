import argparse
import subprocess
import sys
from typing import Dict, Tuple


def get_commits(count: int):
    try:
        out = subprocess.check_output(['git', 'rev-list', '--max-count', str(count), 'HEAD'], text=True)
        return out.strip().splitlines()
    except subprocess.CalledProcessError:
        return []


def count_py_lines(treeish: str, path: str) -> Tuple[int, int]:
    try:
        out = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', treeish, path], text=True)
    except subprocess.CalledProcessError:
        return 0, 0
    total_lines = 0
    files = [f for f in out.splitlines() if f.endswith('.py')]
    for f in files:
        try:
            content = subprocess.check_output(['git', 'show', f'{treeish}:{f}'], text=True, errors='ignore')
            total_lines += len(content.splitlines())
        except subprocess.CalledProcessError:
            continue
    return total_lines, len(files)


def analyze_commit(commit: str) -> Dict[str, int]:
    metrics = {}
    metrics['recon_modules'], metrics['recon_files'] = count_py_lines(commit, 'recon_modules')
    metrics['vuln_modules'], metrics['vuln_files'] = count_py_lines(commit, 'vuln_modules')
    metrics['pipelines'], metrics['pipeline_files'] = count_py_lines(commit, 'pipelines')
    metrics['tests'], metrics['test_files'] = count_py_lines(commit, 'tests')
    metrics['commit'] = commit
    metrics['loc'] = (
        metrics['recon_modules'] + metrics['vuln_modules'] +
        metrics['pipelines'] + metrics['tests']
    )
    return metrics


def choose_best(metrics_list):
    # Choose commit with highest loc and tests count
    return max(metrics_list, key=lambda m: (m['test_files'], m['loc']))


def main():
    parser = argparse.ArgumentParser(description='Analyze multiple versions of ChainHunter')
    parser.add_argument('--count', type=int, default=4, help='Number of commits to analyze')
    args = parser.parse_args()
    commits = get_commits(args.count)
    if not commits:
        print('No commits found')
        return 1
    results = [analyze_commit(c) for c in commits]
    for r in results:
        print(f"Commit {r['commit'][:7]}: {r['loc']} LOC across {r['test_files']} tests")
    best = choose_best(results)
    print(f"Recommended version: {best['commit'][:7]} (tests: {best['test_files']}, LOC: {best['loc']})")
    return 0


if __name__ == '__main__':
    sys.exit(main())
