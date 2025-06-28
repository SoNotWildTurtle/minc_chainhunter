#!/usr/bin/env python3
"""Manage vulnerability modules."""

import argparse
import importlib
import os
import sys
from typing import List

MODULE_DIR = os.path.dirname(__file__)


def list_modules() -> List[str]:
    mods = []
    for f in os.listdir(MODULE_DIR):
        if f.endswith('.py') and f not in ('__init__.py', 'manager.py'):
            mods.append(os.path.splitext(f)[0])
    return sorted(mods)


def run_module(name: str, args: List[str]) -> None:
    sys.path.insert(0, MODULE_DIR)
    mod = importlib.import_module(name)
    sys.argv = [name] + args
    if hasattr(mod, 'main'):
        mod.main()
    else:
        print(f'Module {name} has no main()')


def main() -> None:
    parser = argparse.ArgumentParser(description='Vulnerability module manager')
    parser.add_argument('--list', action='store_true', help='List modules')
    parser.add_argument('module', nargs='?', help='Module to run')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.list or not args.module:
        for m in list_modules():
            print(m)
        if not args.module:
            return

    if args.module:
        if args.module not in list_modules():
            print('Unknown module')
            return
        run_module(args.module, args.args)


if __name__ == '__main__':
    main()
