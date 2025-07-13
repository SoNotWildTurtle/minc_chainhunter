import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from github_scanners import manager


def test_list_tools_cross_platform(tmp_path, monkeypatch):
    root = tmp_path / "gh_scanners"
    tool = root / "sample"
    tool.mkdir(parents=True)
    (tool / "run.sh").write_text("echo hi")
    monkeypatch.setattr(manager, 'SCANNER_DIR', str(root))
    tools = manager.list_tools()
    assert 'sample' in tools
