import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import recon_modules.theharvester_scan as th
import recon_modules.amass_scan as am
import recon_modules.masscan_scan as ma
import recon_modules.aquatone_scan as aq


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


def test_masscan_cmd_build():
    cmd = ma.build_masscan_cmd("1.2.3.4", ports="80", rate=5000)
    script = os.path.join(os.path.dirname(ma.__file__), "..", "github_scanners", "masscan", "run.sh")
    assert cmd[:2] == ["bash", script]
    assert cmd[2] == "1.2.3.4"
    assert "-p" in cmd and cmd[cmd.index("-p") + 1] == "80"
    assert "--rate" in cmd and cmd[cmd.index("--rate") + 1] == "5000"


def test_aquatone_cmd_build():
    cmd = aq.build_aquatone_cmd("example.com", out_dir="out")
    script = os.path.join(os.path.dirname(aq.__file__), "..", "github_scanners", "aquatone", "run.sh")
    assert cmd[:2] == ["bash", script]
    assert cmd[2] == "example.com"
    assert cmd[3] == "out"
