import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import recon_modules.theharvester_scan as th
import recon_modules.amass_scan as am
import recon_modules.masscan_scan as ma
import recon_modules.aquatone_scan as aq
import recon_modules.httpx_scan as hx
import recon_modules.whois_scan as ws


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


def test_masscan_parse():
    sample = "Discovered open port 80/tcp on 1.2.3.4\nDiscovered open port 443/tcp on 1.2.3.4"
    ports = ma._parse_ports(sample)
    assert ports == [80, 443]


def test_aquatone_cmd_build():
    cmd = aq.build_aquatone_cmd("example.com", out_dir="out")
    script = os.path.join(os.path.dirname(aq.__file__), "..", "github_scanners", "aquatone", "run.sh")
    assert cmd[:2] == ["bash", script]
    assert cmd[2] == "example.com"
    assert cmd[3] == "out"


def test_httpx_cmd_build():
    cmd = hx.build_httpx_cmd("https://example.com")
    script = os.path.join(os.path.dirname(hx.__file__), "..", "github_scanners", "httpx", "run.sh")
    assert cmd[:2] == ["bash", script]
    for flag in ["-json", "-status-code", "-title", "-tech-detect", "-silent"]:
        assert flag in cmd
    assert "-u" in cmd and cmd[cmd.index("-u") + 1] == "https://example.com"


def test_httpx_parse():
    sample = '{"host":"example.com","status-code":200,"title":"Example","tech":["nginx"]}\n'
    parsed = hx._parse_httpx_output(sample)
    assert parsed == [{"host": "example.com", "status_code": 200, "title": "Example", "tech": ["nginx"]}]


def test_whois_cmd_build():
    cmd = ws.build_whois_cmd("example.com")
    assert cmd == ["whois", "example.com"]
