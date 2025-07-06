import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import vuln_modules.sqli_scanner as sqli
import vuln_modules.xxe_scan as xxe


def test_sqli_scanner_run():
    res = sqli.main(["127.0.0.1"])
    assert isinstance(res, dict)
    assert res["target"] == "127.0.0.1"
    assert "vulnerabilities" in res
    assert "raw" in res


def test_xxe_scan_run():
    res = xxe.main(["127.0.0.1"])
    assert isinstance(res, dict)
    assert res["target"] == "127.0.0.1"
    assert "vulnerabilities" in res
    assert "raw" in res
