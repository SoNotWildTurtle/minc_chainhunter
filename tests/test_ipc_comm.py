import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ipc_bus.bus_init import start_ipc_server
from ipc_bus.message_api import send_request
from ipc_bus.bus_integrity import check_socket_permissions


def test_ipc_echo(tmp_path):
    sock = tmp_path / "bus.sock"

    def handler(msg):
        return {"reply": msg.get("msg")}

    t = threading.Thread(target=start_ipc_server, args=(str(sock), handler, True))
    t.start()
    time.sleep(0.1)

    resp = send_request(str(sock), {"msg": "hello"})
    t.join()

    assert resp["reply"] == "hello"
    assert check_socket_permissions(str(sock))
