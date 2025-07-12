#!/usr/bin/env python3
"""Generate skeleton modules for ChainHunter."""
import argparse
import os
import stat

RECON_TEMPLATE = '''"""Recon module {name}."""

import os
import sys
from analysis_db.db_api import log_scan_result


def main(argv=None):
    argv = argv or sys.argv[1:]
    # TODO: implement scanning logic
    result = {{'args': argv}}
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {{'module': '{name}', **result}})
        except Exception:
            pass
    return result


if __name__ == '__main__':
    main()
'''

VULN_TEMPLATE = '''"""Vulnerability module {name}."""

import os
import sys
from analysis_db.db_api import log_scan_result


def main(argv=None):
    argv = argv or sys.argv[1:]
    # TODO: implement vulnerability check
    result = {{'args': argv, 'vulnerabilities': []}}
    sock = os.environ.get("MINC_DB_SOCKET")
    if sock:
        try:
            log_scan_result(sock, {{'module': '{name}', **result}})
        except Exception:
            pass
    return result


if __name__ == '__main__':
    main()
'''

PIPELINE_TEMPLATE = '''"""Pipeline {name}."""

from typing import List


def run(target: str) -> List[dict]:
    results = []
    # TODO: call modules here
    return results
'''

TEMPLATES = {
    'recon': ('recon_modules', RECON_TEMPLATE),
    'vuln': ('vuln_modules', VULN_TEMPLATE),
    'pipeline': ('pipelines', PIPELINE_TEMPLATE),
}


def main() -> None:
    parser = argparse.ArgumentParser(description='Create a new module skeleton')
    parser.add_argument('type', choices=TEMPLATES.keys(), help='Module type')
    parser.add_argument('name', help='Module name without _scan suffix')
    parser.add_argument('--root', default=os.path.dirname(os.path.dirname(__file__)), help='Repository root')
    args = parser.parse_args()

    subdir, template = TEMPLATES[args.type]
    root = os.path.abspath(args.root)
    os.makedirs(os.path.join(root, subdir), exist_ok=True)
    mod_name = args.name
    if args.type != 'pipeline' and not mod_name.endswith('_scan'):
        mod_name = mod_name + '_scan'
    path = os.path.join(root, subdir, mod_name + '.py')
    if os.path.exists(path):
        print(f'{path} already exists')
        return
    with open(path, 'w', encoding='utf-8') as f:
        f.write(template.format(name=mod_name))
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
    print(f'Created {path}')


if __name__ == '__main__':
    main()
