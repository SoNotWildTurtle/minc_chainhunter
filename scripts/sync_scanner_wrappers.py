#!/usr/bin/env python3
"""Generate missing Python wrapper modules for GitHub scanners."""

import argparse
import os
from pathlib import Path

TOOL_TYPES = {
    'gitleaks': 'vuln',
    'ssrfmap': 'vuln',
    'nuclei': 'vuln',
    'dirsearch': 'vuln',
    'subfinder': 'recon',
    'hakrawler': 'recon',
    'trufflehog': 'vuln',
    'theharvester': 'recon',
    'amass': 'recon',
    'masscan': 'recon',
    'nmap': 'vuln',
    'git_dumper': 'vuln',
    'aquatone': 'recon',
    'xsstrike': 'vuln',
    'sqlmap': 'vuln',
    'mythic': 'offensive',
}

WRAPPER_TEMPLATE = '''"""Run {tool} scanner."""

import os
import subprocess
import sys
from analysis_db.db_api import log_scan_result


def main(argv=None):
    argv = argv or sys.argv[1:]
    script = os.path.join(os.path.dirname(__file__), '..', 'github_scanners', '{tool}', 'run.sh')
    cmd = ['bash', script] + argv
    proc = subprocess.run(cmd, capture_output=True, text=True)
    result = {{'output': proc.stdout.strip()}}
    sock = os.environ.get('MINC_DB_SOCKET')
    if sock:
        try:
            log_scan_result(sock, {{'module': '{tool}_scan', **result}})
        except Exception:
            pass
    return result


if __name__ == '__main__':
    main()
'''


def create_wrapper(root: Path, tool: str, ttype: str) -> bool:
    if ttype == 'recon':
        dest = root / 'recon_modules'
    elif ttype == 'offensive':
        dest = root / 'offensive_modules'
    else:
        dest = root / 'vuln_modules'
    dest.mkdir(exist_ok=True)
    mod_file = dest / f'{tool}_scan.py'
    if mod_file.exists():
        return False
    mod_file.write_text(WRAPPER_TEMPLATE.format(tool=tool))
    return True


def sync_wrappers(root: Path) -> list[str]:
    created = []
    for tool, ttype in TOOL_TYPES.items():
        if create_wrapper(root, tool, ttype):
            created.append(tool)
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description='Ensure scanner wrappers exist')
    parser.add_argument('--root', default=os.path.dirname(os.path.dirname(__file__)), help='Repository root')
    args = parser.parse_args()
    root = Path(args.root)
    created = sync_wrappers(root)
    if created:
        print('[+] Created wrappers:', ', '.join(created))
    else:
        print('[*] All wrappers present')


if __name__ == '__main__':
    main()
