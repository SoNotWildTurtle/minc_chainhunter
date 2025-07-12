#!/usr/bin/env python3
"""Simple IPC bus manager."""

import argparse
import json

from .bus_init import start_ipc_server
from .message_api import send_request


def main():
    parser = argparse.ArgumentParser(description='IPC bus manager')
    sub = parser.add_subparsers(dest='cmd')

    s = sub.add_parser('start', help='Start echo server')
    s.add_argument('--socket', required=True)

    snd = sub.add_parser('send', help='Send JSON payload')
    snd.add_argument('--socket', required=True)
    snd.add_argument('payload')

    args = parser.parse_args()

    if args.cmd == 'start':
        def handler(msg):
            return msg
        start_ipc_server(args.socket, handler)
    elif args.cmd == 'send':
        resp = send_request(args.socket, json.loads(args.payload))
        print(json.dumps(resp))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
