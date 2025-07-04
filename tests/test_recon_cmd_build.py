import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import recon_modules.theharvester_scan as th
import recon_modules.amass_scan as am


def test_theharvester_cmd_build():
    cmd = th.build_theharvester_cmd("example.com", sources="google", limit=5)
    script = os.path.join(os.path.dirname(th.__file__), "..", "github_scanners", "theharvester", "run.sh")
    assert cmd[:2] == ["bash", script]
    assert "-d" in cmd and cmd[cmd.index("-d") + 1] == "example.com"
    assert "-s" in cmd and cmd[cmd.index("-s") + 1] == "google"
    assert "-l" in cmd and cmd[cmd.index("-l") + 1] == "5"


def test_amass_cmd_build():
    cmd = am.build_amass_cmd("example.com")
    script = os.path.join(os.path.dirname(am.__file__), "..", "github_scanners", "amass", "run.sh")
    assert cmd[:2] == ["bash", script]
    assert "enum" in cmd
    assert "-d" in cmd and cmd[cmd.index("-d") + 1] == "example.com"
