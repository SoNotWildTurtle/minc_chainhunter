"""Minimal IPC bus server implementation."""

import json
import os
import socket
from typing import Callable, Dict, Optional


def start_ipc_server(
    sock_path: str,
    handler: Callable[[Dict], Dict],
    once: bool = False,
    secret: Optional[str] = None,
) -> None:
    """Start a simple UNIX socket server.

    Parameters
    ----------
    sock_path: str
        Path to the UNIX domain socket.
    handler: Callable[[Dict], Dict]
        Called with the parsed JSON request. Should return a JSON-serialisable dict.
    once: bool
        If True, handle a single request and exit.
    """
    if os.path.exists(sock_path):
        os.remove(sock_path)
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
        server.bind(sock_path)
        os.chmod(sock_path, 0o600)
        server.listen(1)
        while True:
            conn, _ = server.accept()
            with conn:
                data = b""
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                if not data:
                    continue
                request = json.loads(data.decode())
                if secret and request.get("secret") != secret:
                    response = {"status": "error", "error": "unauthorized"}
                else:
                    response = handler(request)
                try:
                    conn.sendall(json.dumps(response).encode())
                except BrokenPipeError:
                    pass
            if once:
                break
