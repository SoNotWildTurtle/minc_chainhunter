"""Client helpers for IPC bus communication."""

import json
import os
import socket
from typing import Dict, Tuple


def _parse_sock(sock_path: str) -> Tuple[socket.AddressFamily, Tuple[str, int] | str]:
    """Return address family and address tuple/path for the socket."""
    if sock_path.startswith("tcp://"):
        host_port = sock_path[6:]
        host, port_str = host_port.split(":", 1)
        return socket.AF_INET, (host, int(port_str))
    return socket.AF_UNIX, sock_path


def send_request(sock_path: str, payload: Dict) -> Dict:
    """Send a JSON payload to the IPC bus and return the JSON response."""
    secret = os.getenv("MINC_IPC_SECRET")
    if secret:
        payload = {"secret": secret, **payload}

    family, addr = _parse_sock(sock_path)
    with socket.socket(family, socket.SOCK_STREAM) as client:
        client.connect(addr)
        client.sendall(json.dumps(payload).encode())
        client.shutdown(socket.SHUT_WR)
        data = b""
        while True:
            chunk = client.recv(4096)
            if not chunk:
                break
            data += chunk
        return json.loads(data.decode()) if data else {}
