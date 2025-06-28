#!/usr/bin/env python3
"""Manage developer notes with progressive compression."""

import argparse
import base64
import json
import os
import zlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple

NOTES_PATH = os.environ.get(
    "DEV_NOTES_PATH",
    os.path.join(os.path.dirname(__file__), "..", "DEV_NOTES.dat"),
)


def _decode_line(line: str) -> Tuple[int, Dict]:
    level, b64 = line.split(':', 1)
    data = zlib.decompress(base64.b64decode(b64))
    try:
        meta = json.loads(data.decode("utf-8"))
    except json.JSONDecodeError:
        # legacy format: just plain text
        meta = {
            "id": 0,
            "ts": "unknown",
            "tags": [],
            "personal": False,
            "text": data.decode("utf-8"),
        }
    return int(level), meta


def _encode_line(level: int, meta: Dict) -> str:
    raw = json.dumps(meta).encode("utf-8")
    data = zlib.compress(raw, level)
    return f"{level}:{base64.b64encode(data).decode('utf-8')}"


def load_notes() -> List[Tuple[int, Dict]]:
    if not os.path.isfile(NOTES_PATH):
        return []
    notes: List[Tuple[int, Dict]] = []
    with open(NOTES_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            notes.append(_decode_line(line))
    return notes


def save_notes(notes: List[Tuple[int, Dict]]) -> None:
    with open(NOTES_PATH, 'w', encoding='utf-8') as f:
        f.write('# notes:pcmeta-v1\n')
        f.write('# decode with: python3 dev_notes/notes_manager.py --show\n')
        for level, meta in notes:
            f.write(_encode_line(level, meta) + '\n')


def add_note(text: str, tags: Optional[List[str]] = None, personal: bool = False) -> None:
    """Add a note and recompress older ones."""
    notes = load_notes()
    updated: List[Tuple[int, Dict]] = []
    for level, meta in notes:
        updated.append((min(9, level + 1), meta))
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    next_id = notes[-1][1]["id"] + 1 if notes else 1
    meta = {
        "id": next_id,
        "ts": timestamp,
        "tags": tags or [],
        "personal": personal,
        "text": text,
    }
    updated.append((1, meta))
    save_notes(updated)


def show_notes(n: int = 0, tag: Optional[str] = None) -> None:
    notes = load_notes()
    if tag:
        notes = [nt for nt in notes if tag in nt[1].get("tags", [])]
    if n > 0:
        notes = notes[-n:]
    for _, meta in notes:
        print(f"{meta['ts']} - {meta['text']}")


def view_notes(center: int, radius: int = 0) -> None:
    """View notes around a specific index and adjust compression levels."""
    notes = load_notes()
    if not notes:
        return
    total = len(notes)
    center = max(0, min(total - 1, center))
    updated: List[Tuple[int, Dict]] = []
    for idx, (_, meta) in enumerate(notes):
        dist = abs(idx - center)
        level = min(9, 1 + dist)
        updated.append((level, meta))
    save_notes(updated)
    start = max(0, center - radius)
    end = min(total, center + radius + 1)
    for _, meta in updated[start:end]:
        print(f"{meta['ts']} - {meta['text']}")


def search_notes(tag: str) -> None:
    """Print notes matching a tag."""
    show_notes(tag=tag)


def main() -> None:
    parser = argparse.ArgumentParser(description='Developer notes manager')
    parser.add_argument('--add', metavar='TEXT', help='Add a note')
    parser.add_argument('--tags', nargs='*', default=[], help='Tags for --add')
    parser.add_argument('--personal', action='store_true', help='Mark new note as personal')
    parser.add_argument('--show', type=int, nargs='?', const=5, metavar='N', help='Show last N notes')
    parser.add_argument('--tag', metavar='TAG', help='Filter notes by TAG when using --show')
    parser.add_argument('--view', type=int, metavar='INDEX', help='View notes around INDEX and recompress others')
    parser.add_argument('--radius', type=int, default=0, metavar='N', help='Number of neighbouring notes to display with --view')
    args = parser.parse_args()

    if args.add:
        add_note(args.add, tags=args.tags, personal=args.personal)
    elif args.show is not None:
        show_notes(args.show, tag=args.tag)
    elif args.view is not None:
        view_notes(args.view, radius=args.radius)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
