import json
import os
import json
import threading
import time
from pathlib import Path

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis_db.db_init import start_db_server
from analysis_db.db_api import log_scan_result
from analysis_db import neural_analyzer as na


def test_db_interactions(tmp_path):
    sock = tmp_path / "db.sock"
    db_dir = tmp_path / "data"
    inter_file = Path("analysis_db/module_interactions.json")
    model_file = na.MODULE_MODEL_PATH
    inter_backup = inter_file.read_text() if inter_file.exists() else None
    model_backup = model_file.read_bytes() if model_file.exists() else None
    if inter_file.exists():
        inter_file.unlink()
    na._MODULE_MAP.clear()
    na._MODULE_INTERACTIONS.clear()

    # log first result
    t1 = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t1.start()
    time.sleep(0.1)
    log_scan_result(str(sock), {"module": "ping_sweep"})
    t1.join()

    # log second result
    t2 = threading.Thread(target=start_db_server, args=(str(db_dir), str(sock), True))
    t2.start()
    time.sleep(0.1)
    log_scan_result(str(sock), {"module": "sqli_scanner"})
    t2.join()

    with open(inter_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("ping_sweep", {}).get("sqli_scanner") == 1

    na._MODULE_INTERACTIONS.clear()
    na._MODULE_MAP.clear()
    if inter_backup is not None:
        inter_file.write_text(inter_backup)
    else:
        inter_file.unlink(missing_ok=True)
    if model_backup is not None:
        model_file.write_bytes(model_backup)
    else:
        model_file.unlink(missing_ok=True)
    na.load_module_model()
    na.load_interactions()
