#!/usr/bin/env python3
"""Manage GitHub-based scanner tools."""

import argparse
import os
import subprocess
import sys

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


def main():
    parser = argparse.ArgumentParser(description='Scanner tool manager')
    sub = parser.add_subparsers(dest='cmd')

    sub.add_parser('list', help='List available tools')

    r = sub.add_parser('run', help='Run a specific tool')
    r.add_argument('tool')
    r.add_argument('args', nargs=argparse.REMAINDER)

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


if __name__ == '__main__':
    main()
