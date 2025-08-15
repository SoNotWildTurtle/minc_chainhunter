import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import vuln_modules.dirsearch_scan as ds
import vuln_modules.gitleaks_scan as gl
import vuln_modules.nuclei_scan as nu
import vuln_modules.ssrfmap_scan as sm
import vuln_modules.trufflehog_scan as th
import vuln_modules.nmap_scan as nm
import vuln_modules.git_dumper_scan as gd
import vuln_modules.xsstrike_scan as xs
import vuln_modules.sqlmap_scan as sql
import vuln_modules.ffuf_scan as ff
import vuln_modules.hydra_scan as hy
import vuln_modules.nikto_scan as nk


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


def test_nmap_cmd_build():
    cmd = nm.build_nmap_cmd("example.com", options="-sS")
    script = os.path.join(os.path.dirname(nm.__file__), "..", "github_scanners", "nmap", "run.sh")
    assert cmd[:2] == ["bash", script]
    assert cmd[2] == "example.com"
    assert "-sS" in cmd


def test_nmap_parse():
    sample = "22/tcp open ssh\n80/tcp open http"
    ports = nm._parse_ports(sample)
    assert ports == [22, 80]


def test_git_dumper_cmd_build():
    cmd = gd.build_git_dumper_cmd("http://ex.com", out_dir="repo")
    script = os.path.join(os.path.dirname(gd.__file__), "..", "github_scanners", "git_dumper", "run.sh")
    assert cmd[:2] == ["bash", script]
    assert cmd[2] == "http://ex.com"
    assert cmd[3] == "repo"


def test_xsstrike_cmd_build():
    cmd = xs.build_xsstrike_cmd("http://victim", crawl=True)
    script = os.path.join(os.path.dirname(xs.__file__), "..", "github_scanners", "xsstrike", "run.sh")
    assert cmd[:2] == ["bash", script]
    assert "-u" in cmd and cmd[cmd.index("-u") + 1] == "http://victim"
    assert "--crawl" in cmd


def test_sqlmap_cmd_build():
    cmd = sql.build_sqlmap_cmd("http://victim", options="--batch")
    script = os.path.join(os.path.dirname(sql.__file__), "..", "github_scanners", "sqlmap", "run.sh")
    assert cmd[:2] == ["bash", script]
    assert "-u" in cmd and cmd[cmd.index("-u") + 1] == "http://victim"
    assert "--batch" in cmd


def test_ffuf_cmd_build():
    cmd = ff.build_ffuf_cmd("http://example.com", wordlist="list.txt")
    script = os.path.join(os.path.dirname(ff.__file__), "..", "github_scanners", "ffuf", "run.sh")
    assert cmd[:2] == ["bash", script]
    assert "-u" in cmd and cmd[cmd.index("-u") + 1] == "http://example.com"
    assert "-w" in cmd and cmd[cmd.index("-w") + 1] == "list.txt"


def test_hydra_cmd_build():
    cmd = hy.build_hydra_cmd("target", "ssh", user="root", password="pass")
    script = os.path.join(os.path.dirname(hy.__file__), "..", "github_scanners", "hydra", "run.sh")
    assert cmd[:2] == ["bash", script]
    assert "target" in cmd and "ssh" in cmd
    assert "-l" in cmd and cmd[cmd.index("-l") + 1] == "root"
    assert "-p" in cmd and cmd[cmd.index("-p") + 1] == "pass"


def test_nikto_cmd_build():
    cmd = nk.build_nikto_cmd("example.com", options="-ssl")
    script = os.path.join(os.path.dirname(nk.__file__), "..", "github_scanners", "nikto", "run.sh")
    assert cmd[:2] == ["bash", script]
    assert "-host" in cmd and cmd[cmd.index("-host") + 1] == "example.com"
    assert "-ssl" in cmd



def test_wpscan_cmd_build():
    import vuln_modules.wpscan_scan as wp
    cmd = wp.build_wpscan_cmd("http://blog", options="--stealth")
    script = os.path.join(os.path.dirname(wp.__file__), "..", "github_scanners", "wpscan", "run.sh")
    assert cmd[:2] == ["bash", script]
    assert "--url" in cmd and cmd[cmd.index("--url") + 1] == "http://blog"
    assert "--stealth" in cmd

