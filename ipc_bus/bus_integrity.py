"""Simple IPC bus integrity checks."""

import os
import json
from stat import S_ISSOCK

ALIAS_FILE = os.path.join(os.path.dirname(__file__), "approved_aliases.json")


def load_approved_aliases(path: str = ALIAS_FILE):
    """Return list of approved command aliases from JSON file."""
    if not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []
    return data.get("aliases", [])


def is_alias_approved(alias: str, path: str = ALIAS_FILE) -> bool:
    """Check whether an alias is approved."""
    aliases = load_approved_aliases(path)
    return alias in aliases


def check_socket_permissions(sock_path: str) -> bool:
    """Ensure socket exists and is not world writable."""
    try:
        st = os.stat(sock_path)
    except FileNotFoundError:
        return False
    if not S_ISSOCK(st.st_mode):
        return False
    # world writable bit
    if st.st_mode & 0o002:
        return False
    return True
