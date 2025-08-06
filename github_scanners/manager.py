#!/usr/bin/env python3
"""Manage GitHub-based scanner tools."""

import argparse
import os
import subprocess
import sys

from analysis_db.db_api import log_scan_result

# ensure imports work when run from repo root
REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, REPO_ROOT)

# Basic information about available scanners. This avoids executing the tools
# when network access or dependencies are missing. The info command simply
# prints these descriptions so other components can understand new tools.
TOOL_INFO = {
    'gitleaks': 'Scan git repositories for secrets',
    'ssrfmap': 'Detect Server-Side Request Forgery issues',
    'nuclei': 'Fast vulnerability scanning using templates',
    'dirsearch': 'Brute-force web directories',
    'subfinder': 'Enumerate subdomains',
    'hakrawler': 'Crawl websites for URLs',
    'trufflehog': 'Find secrets in git history',
    'theharvester': 'Gather emails and subdomains',
    'amass': 'Perform in-depth DNS enumeration',
    'httpx': 'Probe HTTP hosts and detect technologies',
    'masscan': 'High speed port scanner',
    'nmap': 'Network exploration and service detection',
    'git_dumper': 'Download exposed .git directories',
    'aquatone': 'Screenshot discovered hosts',
    'xsstrike': 'Detect XSS vulnerabilities',
    'sqlmap': 'Automated SQL injection exploitation',
    'ffuf': 'Fast web fuzzer for content discovery',
    'hydra': 'Network login cracker',
    'mythic': 'Offensive C2 framework controller',
}

SCANNER_DIR = os.path.dirname(__file__)


def list_tools():
    return [d for d in os.listdir(SCANNER_DIR) if os.path.isdir(os.path.join(SCANNER_DIR, d)) and d not in ("__pycache__") and not d.endswith('.py')]


def run_tool(tool: str, args):
    script = os.path.join(SCANNER_DIR, tool, 'run.sh')
    if not os.path.isfile(script):
        print(f'Tool {tool} not found')
        return
    cmd = ['bash', script] + args
    proc = subprocess.run(cmd, capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    sock = os.environ.get('MINC_DB_SOCKET')
    if sock:
        try:
            log_scan_result(
                sock,
                {
                    'module': tool,
                    'params': args,
                    'output': proc.stdout.strip(),
                    'returncode': proc.returncode,
                },
            )
        except Exception:
            pass


def show_info(tool: str) -> None:
    """Display stored information about the scanner."""
    desc = TOOL_INFO.get(tool)
    if not desc:
        print(f'No info for tool {tool}')
        return
    print(f"{tool}: {desc}")
    print(f"Run script: {os.path.join(SCANNER_DIR, tool, 'run.sh')}")


def main():
    parser = argparse.ArgumentParser(description='Scanner tool manager')
    sub = parser.add_subparsers(dest='cmd')

    sub.add_parser('list', help='List available tools')

    r = sub.add_parser('run', help='Run a specific tool')
    r.add_argument('tool')
    r.add_argument('args', nargs=argparse.REMAINDER)

    info_p = sub.add_parser('info', help='Show tool details')
    info_p.add_argument('tool')

    rec_p = sub.add_parser('recommend', help='Recommend parameters for a tool')
    rec_p.add_argument('tool')
    rec_p.add_argument('-n', type=int, default=50, metavar='N', help='Analyze last N results')

    best_p = sub.add_parser('best', help='Run tool with recommended parameters')
    best_p.add_argument('tool')
    best_p.add_argument('-n', type=int, default=50, metavar='N', help='Analyze last N results')

    help_p = sub.add_parser('help', help='Show tool usage')
    help_p.add_argument('tool')

    args = parser.parse_args()

    if args.cmd == 'list' or args.cmd is None:
        for t in list_tools():
            print(t)
        return

    if args.cmd == 'run':
        if args.tool not in list_tools():
            print('Unknown tool')
            return
        run_tool(args.tool, args.args)
    elif args.cmd == 'info':
        if args.tool not in list_tools():
            print('Unknown tool')
            return
        show_info(args.tool)
    elif args.cmd == 'recommend':
        if args.tool not in list_tools():
            print('Unknown tool')
            return
        try:
            from analysis_db.db_api import suggest_params_api
            sock = os.environ.get('MINC_DB_SOCKET', '/tmp/minc_db.sock')
            resp = suggest_params_api(sock, args.tool, args.n)
            if resp.get('status') == 'ok':
                for p in resp.get('params', []):
                    print(' '.join(p) if p else '(no params)')
            else:
                print('Failed to get recommendations')
        except Exception as exc:
            print(f'Error: {exc}')
    elif args.cmd == 'best':
        if args.tool not in list_tools():
            print('Unknown tool')
            return
        try:
            from analysis_db.db_api import suggest_params_api
            sock = os.environ.get('MINC_DB_SOCKET', '/tmp/minc_db.sock')
            resp = suggest_params_api(sock, args.tool, args.n)
            params = resp.get('params', [[]])
            best = params[0] if params else []
        except Exception as exc:
            print(f'Error: {exc}')
            best = []
        run_tool(args.tool, best)
    elif args.cmd == 'help':
        if args.tool not in list_tools():
            print('Unknown tool')
            return
        show_info(args.tool)


if __name__ == '__main__':
    main()
