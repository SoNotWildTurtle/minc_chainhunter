#!/usr/bin/env python3
"""Manage third-party plugins for ChainHunter."""

import argparse
import os
import shutil
from typing import List

PLUGIN_DIR = os.environ.get(
    'CHAINHUNTER_PLUGIN_DIR',
    os.path.join(os.path.dirname(__file__), 'installed')
)


def list_plugins() -> List[str]:
    if not os.path.isdir(PLUGIN_DIR):
        return []
    return sorted(d for d in os.listdir(PLUGIN_DIR)
                  if os.path.isdir(os.path.join(PLUGIN_DIR, d)))


def install_plugin(path: str) -> str:
    """Install a plugin from a local path."""
    if not os.path.isdir(path):
        raise ValueError('Plugin path does not exist')
    name = os.path.basename(os.path.abspath(path))
    dest = os.path.join(PLUGIN_DIR, name)
    os.makedirs(PLUGIN_DIR, exist_ok=True)
    if os.path.exists(dest):
        raise ValueError('Plugin already installed')
    shutil.copytree(path, dest)
    return name


def main() -> None:
    parser = argparse.ArgumentParser(description='Plugin manager')
    sub = parser.add_subparsers(dest='cmd')
    sub.add_parser('list', help='List installed plugins')
    ins = sub.add_parser('install', help='Install plugin from path')
    ins.add_argument('path')

    args = parser.parse_args()
    if args.cmd == 'list' or args.cmd is None:
        for p in list_plugins():
            print(p)
        return
    if args.cmd == 'install':
        try:
            name = install_plugin(args.path)
            print(f'Installed {name}')
        except Exception as e:
            print(f'Error: {e}')


if __name__ == '__main__':
    main()
