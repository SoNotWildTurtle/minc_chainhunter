#!/usr/bin/env python3
"""Manage GitHub-based scanner tools."""

import argparse
import os
import subprocess
import sys

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
    'masscan': 'High speed port scanner',
    'nmap': 'Network exploration and service detection',
    'git_dumper': 'Download exposed .git directories',
    'aquatone': 'Screenshot discovered hosts',
    'xsstrike': 'Detect XSS vulnerabilities',
    'sqlmap': 'Automated SQL injection exploitation',
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
    subprocess.run(cmd)


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


if __name__ == '__main__':
    main()
