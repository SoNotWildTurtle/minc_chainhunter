#!/usr/bin/env python3
"""Utility script to manage the analysis database."""

import argparse

from .db_init import start_db_server
from .report_gen import load_results, build_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage ChainHunter analysis database")
    sub = parser.add_subparsers(dest="cmd")

    s = sub.add_parser("start", help="Start the database IPC service")
    s.add_argument("--db_dir", default="db_data")
    s.add_argument("--socket", required=True)

    r = sub.add_parser("report", help="Generate a markdown report")
    r.add_argument("--db_dir", default="db_data")
    r.add_argument("--out_dir", default="reports")

    args = parser.parse_args()

    if args.cmd == "start":
        start_db_server(args.db_dir, args.socket)
    elif args.cmd == "report":
        results = load_results(args.db_dir)
        path = build_report(results, args.out_dir)
        print(path)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
