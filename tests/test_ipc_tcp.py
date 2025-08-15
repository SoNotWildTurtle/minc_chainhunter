import os
import sys
import threading
import time
import socket

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ipc_bus.bus_init import start_ipc_server
from ipc_bus.message_api import send_request


def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def test_ipc_tcp(tmp_path):
    port = get_free_port()
    sock = f"tcp://127.0.0.1:{port}"

    def handler(msg):
        return {"reply": msg.get("msg")}

    t = threading.Thread(target=start_ipc_server, args=(sock, handler, True))
    t.start()
    time.sleep(0.1)

    resp = send_request(sock, {"msg": "hello"})
    t.join()

    assert resp["reply"] == "hello"
