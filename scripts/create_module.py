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
    host = argv[0] if argv else '127.0.0.1'
    status = os.system(f"ping -c 1 {host} > /dev/null 2>&1")
    result = {{'args': argv, 'reachable': status == 0}}
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
    url = argv[0] if argv else 'http://localhost/'
    import urllib.request
    try:
        data = urllib.request.urlopen(url, timeout=5).read().decode('utf-8', 'ignore')
    except Exception:
        data = ''
    vulns = ['sql error'] if 'SQL' in data.upper() else []
    result = {{'args': argv, 'vulnerabilities': vulns}}
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
    try:
        from recon_modules.manager import load_module
        ping = load_module('ping_sweep')
        results.append(ping.main([target]))
    except Exception:
        pass
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
