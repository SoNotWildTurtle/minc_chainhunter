#!/usr/bin/env python3
"""Manage developer notes with progressive compression."""

import argparse
import base64
import zlib
import os
from datetime import datetime
from typing import List, Tuple

NOTES_PATH = os.environ.get(
    "DEV_NOTES_PATH",
    os.path.join(os.path.dirname(__file__), "..", "DEV_NOTES.dat"),
)


def _decode_line(line: str) -> Tuple[int, str]:
    level, b64 = line.split(':', 1)
    text = zlib.decompress(base64.b64decode(b64)).decode('utf-8')
    return int(level), text


def _encode_line(level: int, text: str) -> str:
    data = zlib.compress(text.encode('utf-8'), level)
    return f"{level}:{base64.b64encode(data).decode('utf-8')}"


def load_notes() -> List[Tuple[int, str]]:
    if not os.path.isfile(NOTES_PATH):
        return []
    notes: List[Tuple[int, str]] = []
    with open(NOTES_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            notes.append(_decode_line(line))
    return notes


def save_notes(notes: List[Tuple[int, str]]) -> None:
    with open(NOTES_PATH, 'w', encoding='utf-8') as f:
        f.write('# notes:pc-v1\n')
        f.write('# decode with: python3 dev_notes/notes_manager.py --show\n')
        for level, text in notes:
            f.write(_encode_line(level, text) + '\n')


def add_note(text: str) -> None:
    notes = load_notes()
    updated: List[Tuple[int, str]] = []
    for level, t in notes:
        updated.append((min(9, level + 1), t))
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    updated.append((1, f'{timestamp} - {text}'))
    save_notes(updated)


def show_notes(n: int = 0) -> None:
    notes = load_notes()
    if n > 0:
        notes = notes[-n:]
    for _, text in notes:
        print(text)


def view_notes(center: int, radius: int = 0) -> None:
    """View notes around a specific index and adjust compression levels."""
    notes = load_notes()
    if not notes:
        return
    total = len(notes)
    center = max(0, min(total - 1, center))
    updated: List[Tuple[int, str]] = []
    for idx, (_, text) in enumerate(notes):
        dist = abs(idx - center)
        level = min(9, 1 + dist)
        updated.append((level, text))
    save_notes(updated)
    start = max(0, center - radius)
    end = min(total, center + radius + 1)
    for _, text in updated[start:end]:
        print(text)


def main() -> None:
    parser = argparse.ArgumentParser(description='Developer notes manager')
    parser.add_argument('--add', metavar='TEXT', help='Add a note')
    parser.add_argument('--show', type=int, nargs='?', const=5, metavar='N', help='Show last N notes')
    parser.add_argument('--view', type=int, metavar='INDEX', help='View notes around INDEX and recompress others')
    parser.add_argument('--radius', type=int, default=0, metavar='N', help='Number of neighbouring notes to display with --view')
    args = parser.parse_args()

    if args.add:
        add_note(args.add)
    elif args.show is not None:
        show_notes(args.show)
    elif args.view is not None:
        view_notes(args.view, radius=args.radius)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
