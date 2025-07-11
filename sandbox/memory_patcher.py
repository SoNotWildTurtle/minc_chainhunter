#!/usr/bin/env python3
"""Direct file patching using mmap."""
import mmap
from pathlib import Path


def patch_file(path: str | Path, offset: int, data: bytes) -> None:
    p = Path(path)
    with p.open('r+b') as f:
        mm = mmap.mmap(f.fileno(), 0)
        mm[offset:offset+len(data)] = data
        mm.flush()
        mm.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Patch a file at a given offset")
    parser.add_argument("file")
    parser.add_argument("offset", type=int)
    parser.add_argument("data")
    args = parser.parse_args()
    patch_file(args.file, args.offset, args.data.encode())
