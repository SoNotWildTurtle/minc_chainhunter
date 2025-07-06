import os
import threading
import time
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ipc_bus.bus_init import start_ipc_server
from ipc_bus.message_api import send_request


def test_ipc_secret(monkeypatch, tmp_path):
    sock = tmp_path / "secret.sock"
    secret = "s3cr3t"

    def handler(msg):
        return {"ok": True}

    t = threading.Thread(target=start_ipc_server, args=(str(sock), handler, True, secret))
    t.start()
    time.sleep(0.1)
    monkeypatch.setenv("MINC_IPC_SECRET", secret)
    resp = send_request(str(sock), {})
    t.join()
    assert resp["ok"] is True

    t = threading.Thread(target=start_ipc_server, args=(str(sock), handler, True, secret))
    t.start()
    time.sleep(0.1)
    monkeypatch.setenv("MINC_IPC_SECRET", "bad")
    resp = send_request(str(sock), {})
    t.join()
    assert resp.get("error") == "unauthorized"
