import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import ipc_bus.bus_integrity as bi


def test_alias_is_approved():
    assert bi.is_alias_approved("scan")
    assert not bi.is_alias_approved("rm -rf")
