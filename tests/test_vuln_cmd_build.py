import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import vuln_modules.dirsearch_scan as ds
import vuln_modules.gitleaks_scan as gl
import vuln_modules.nuclei_scan as nu
import vuln_modules.ssrfmap_scan as sm
import vuln_modules.trufflehog_scan as th


def test_dirsearch_cmd_build():
    cmd = ds.build_dirsearch_cmd("http://example.com", wordlist="list.txt", threads=10, extensions="php")
    script = os.path.join(os.path.dirname(ds.__file__), "..", "github_scanners", "dirsearch", "run.sh")
    assert cmd[:2] == ["bash", script]
    assert "-u" in cmd and cmd[cmd.index("-u") + 1] == "http://example.com"
    assert "-w" in cmd and cmd[cmd.index("-w") + 1] == "list.txt"
    assert "-t" in cmd and cmd[cmd.index("-t") + 1] == "10"
    assert "-e" in cmd and cmd[cmd.index("-e") + 1] == "php"


def test_gitleaks_cmd_build():
    cmd = gl.build_gitleaks_cmd("repo", redact=True, config="conf.toml")
    script = os.path.join(os.path.dirname(gl.__file__), "..", "github_scanners", "gitleaks", "run.sh")
    assert cmd[:2] == ["bash", script]
    assert "--source" in cmd and cmd[cmd.index("--source") + 1] == "repo"
    assert "--redact" in cmd
    assert "--config" in cmd and cmd[cmd.index("--config") + 1] == "conf.toml"


def test_nuclei_cmd_build():
    cmd = nu.build_nuclei_cmd("http://x", templates="tpl", severity="high")
    script = os.path.join(os.path.dirname(nu.__file__), "..", "github_scanners", "nuclei", "run.sh")
    assert cmd[:2] == ["bash", script]
    assert "-u" in cmd and cmd[cmd.index("-u") + 1] == "http://x"
    assert "-t" in cmd and cmd[cmd.index("-t") + 1] == "tpl"
    assert "-severity" in cmd and cmd[cmd.index("-severity") + 1] == "high"


def test_ssrfmap_cmd_build():
    cmd = sm.build_ssrfmap_cmd("http://x", param="v", data="a=1")
    script = os.path.join(os.path.dirname(sm.__file__), "..", "github_scanners", "ssrfmap", "run.sh")
    assert cmd[:2] == ["bash", script]
    assert cmd[2] == "http://x"
    assert "-p" in cmd and cmd[cmd.index("-p") + 1] == "v"
    assert "-d" in cmd and cmd[cmd.index("-d") + 1] == "a=1"


def test_trufflehog_cmd_build():
    cmd = th.build_trufflehog_cmd("repo", regex=True)
    script = os.path.join(os.path.dirname(th.__file__), "..", "github_scanners", "trufflehog", "run.sh")
    assert cmd[:2] == ["bash", script]
    assert cmd[2] == "repo"
    assert "--regex" in cmd
