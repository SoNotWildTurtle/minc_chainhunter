"""Minimal IPC bus server implementation."""

import json
import os
import socket
from typing import Callable, Dict, Optional, Tuple


def _parse_sock(sock_path: str) -> Tuple[socket.AddressFamily, Tuple[str, int] | str]:
    if sock_path.startswith("tcp://"):
        host_port = sock_path[6:]
        host, port_str = host_port.split(":", 1)
        return socket.AF_INET, (host, int(port_str))
    return socket.AF_UNIX, sock_path


def start_ipc_server(
    sock_path: str,
    handler: Callable[[Dict], Dict],
    once: bool = False,
    secret: Optional[str] = None,
    max_size: int = 65536,
) -> None:
    """Start a simple IPC server using UNIX or TCP sockets.

    Parameters
    ----------
    sock_path: str
        Path to the UNIX domain socket.
    handler: Callable[[Dict], Dict]
        Called with the parsed JSON request. Should return a JSON-serialisable dict.
    once: bool
        If True, handle a single request and exit.
    """
    family, addr = _parse_sock(sock_path)
    if family == socket.AF_UNIX:
        if os.path.exists(addr):
            os.remove(addr)
    with socket.socket(family, socket.SOCK_STREAM) as server:
        server.bind(addr)
        if family == socket.AF_UNIX:
            os.chmod(addr, 0o600)
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
                    if len(data) > max_size:
                        break
                if not data:
                    continue
                if len(data) > max_size:
                    response = {"status": "error", "error": "request too large"}
                else:
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
