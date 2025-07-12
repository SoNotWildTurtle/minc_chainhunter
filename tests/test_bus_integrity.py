import os
import tempfile
import socket

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ipc_bus.bus_integrity import check_socket_permissions


def test_socket_permissions():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "sock")
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.bind(path)
        try:
            os.chmod(path, 0o600)
            assert check_socket_permissions(path)
            os.chmod(path, 0o666)
            assert not check_socket_permissions(path)
        finally:
            s.close()
