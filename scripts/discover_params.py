#!/usr/bin/env python3
"""Analyze modules or directories to list argparse parameters."""
import argparse
import ast
import os
from typing import Dict, List


def parse_file(path: str) -> List[str]:
    with open(path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=path)
    params: List[str] = []

    class ArgVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'add_argument':
                if node.args:
                    arg = node.args[0]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        params.append(arg.value.lstrip('-'))
            self.generic_visit(node)

    ArgVisitor().visit(tree)
    return params


def analyze_path(path: str) -> Dict[str, List[str]]:
    results: Dict[str, List[str]] = {}
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for name in files:
                if name.endswith('.py'):
                    fp = os.path.join(root, name)
                    p = parse_file(fp)
                    if p:
                        results[fp] = p
    else:
        results[path] = parse_file(path)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description='Discover argparse parameters')
    parser.add_argument('path', nargs='+', help='Files or directories to analyze')
    args = parser.parse_args()

    for target in args.path:
        for file, params in analyze_path(target).items():
            if params:
                print(f'{file}: {" ".join(params)}')


if __name__ == '__main__':
    main()
