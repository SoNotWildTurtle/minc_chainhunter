#!/usr/bin/env python3
"""Manage offensive pentesting modules."""

import argparse
import importlib
import inspect
import os
import sys
from typing import List

MODULE_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, REPO_ROOT)


def list_modules() -> List[str]:
    mods = []
    for f in os.listdir(MODULE_DIR):
        if f.endswith('.py') and f not in ('__init__.py', 'manager.py'):
            mods.append(os.path.splitext(f)[0])
    return sorted(mods)


def list_functions(module: str) -> List[str]:
    sys.path.insert(0, MODULE_DIR)
    mod = importlib.import_module(module)
    return sorted(
        name for name, obj in vars(mod).items() if callable(obj) and not name.startswith('_')
    )


def call_function(module: str, func: str, args: List[str]) -> None:
    sys.path.insert(0, MODULE_DIR)
    mod = importlib.import_module(module)
    if not hasattr(mod, func):
        print('Function not found')
        return
    fn = getattr(mod, func)
    sig = inspect.signature(fn)
    try:
        if len(sig.parameters) == 0:
            res = fn()
        else:
            res = fn(*args)
        if res is not None:
            print(res)
    except Exception as exc:
        print(f'Error: {exc}')


def run_module(name: str, args: List[str]) -> None:
    sys.path.insert(0, MODULE_DIR)
    mod = importlib.import_module(name)
    sys.argv = [name] + args
    if hasattr(mod, 'main'):
        mod.main()
    else:
        print(f'Module {name} has no main()')


def main() -> None:
    parser = argparse.ArgumentParser(description='Offensive module manager')
    sub = parser.add_subparsers(dest='cmd')

    sub.add_parser('list', help='List modules')

    r = sub.add_parser('run', help='Run module main')
    r.add_argument('module')
    r.add_argument('args', nargs=argparse.REMAINDER)

    f = sub.add_parser('funcs', help='List functions in a module')
    f.add_argument('module')

    c = sub.add_parser('call', help='Call a function in a module')
    c.add_argument('module')
    c.add_argument('func')
    c.add_argument('args', nargs=argparse.REMAINDER)

    p = sub.add_parser('recommend', help='Recommend parameters for a module')
    p.add_argument('module')
    p.add_argument('-n', type=int, default=50, metavar='N', help='Analyze last N results')

    args = parser.parse_args()

    if args.cmd in (None, 'list'):
        for m in list_modules():
            print(m)
        return
    if args.cmd == 'run':
        if args.module not in list_modules():
            print('Unknown module')
            return
        run_module(args.module, args.args)
    elif args.cmd == 'funcs':
        if args.module not in list_modules():
            print('Unknown module')
            return
        for fn in list_functions(args.module):
            print(fn)
    elif args.cmd == 'call':
        if args.module not in list_modules():
            print('Unknown module')
            return
        call_function(args.module, args.func, args.args)
    elif args.cmd == 'recommend':
        if args.module not in list_modules():
            print('Unknown module')
            return
        try:
            from analysis_db.db_api import suggest_params_api
            sock = os.environ.get('MINC_DB_SOCKET', '/tmp/minc_db.sock')
            resp = suggest_params_api(sock, args.module, args.n)
            if resp.get('status') == 'ok':
                for p in resp.get('params', []):
                    print(' '.join(p) if p else '(no params)')
            else:
                print('Failed to get recommendations')
        except Exception as exc:
            print(f'Error: {exc}')


if __name__ == '__main__':
    main()
