"""Client helpers for IPC bus communication."""

import json
import socket
from typing import Dict


def send_request(sock_path: str, payload: Dict) -> Dict:
    """Send a JSON payload to the IPC bus and return the JSON response."""
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.connect(sock_path)
        client.sendall(json.dumps(payload).encode())
        client.shutdown(socket.SHUT_WR)
        data = b""
        while True:
            chunk = client.recv(4096)
            if not chunk:
                break
            data += chunk
        return json.loads(data.decode()) if data else {}
