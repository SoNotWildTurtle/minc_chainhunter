#!/usr/bin/env python3
"""Direct file patching using mmap with backup and rollback support."""
import mmap
import shutil
from pathlib import Path


def backup_file(path: str | Path) -> Path:
    """Return path to created backup"""
    p = Path(path)
    backup = p.with_suffix(p.suffix + ".bak")
    shutil.copy2(p, backup)
    return backup


def rollback_file(path: str | Path) -> None:
    """Restore file from backup if it exists."""
    p = Path(path)
    backup = p.with_suffix(p.suffix + ".bak")
    if backup.exists():
        shutil.move(backup, p)
        print(f"[+] Rolled back {p} from backup")


def patch_file(path: str | Path, offset: int, data: bytes, *, backup: bool = True) -> None:
    """Patch file at offset with optional backup and bounds checking."""
    p = Path(path)
    if backup:
        backup_file(p)
    with p.open('r+b') as f:
        mm = mmap.mmap(f.fileno(), 0)
        end = offset + len(data)
        if end > mm.size():
            mm.close()
            raise ValueError("Patch exceeds file size")
        mm[offset:end] = data
        mm.flush()
        mm.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Patch or rollback a file")
    parser.add_argument("file")
    parser.add_argument("offset", type=int, nargs="?", default=0,
                        help="offset for patching")
    parser.add_argument("data", nargs="?", default="",
                        help="data to write for patching")
    parser.add_argument("--rollback", action="store_true",
                        help="restore file from backup instead of patching")
    parser.add_argument("--no-backup", action="store_true",
                        help="do not create backup before patching")
    args = parser.parse_args()
    if args.rollback:
        rollback_file(args.file)
    else:
        patch_file(args.file, args.offset, args.data.encode(), backup=not args.no_backup)
