import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from cli.main import discover_modules


def test_module_discovery():
    mods = discover_modules()
    assert "ping_sweep" in mods
    assert "sqli_scanner" in mods
