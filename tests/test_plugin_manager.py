import os
import sys
import subprocess
from pathlib import Path


def test_plugin_install_and_list(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parent.parent
    plugin_home = tmp_path / "plugins"
    monkeypatch.setenv("CHAINHUNTER_PLUGIN_DIR", str(plugin_home))

    plugin_src = tmp_path / "sample_plugin"
    plugin_src.mkdir()
    (plugin_src / "sample_mod.py").write_text("def main():\n    print('hi')\n")

    # install plugin
    proc = subprocess.run([
        sys.executable,
        str(repo_root / "plugins" / "plugin_manager.py"),
        "install",
        str(plugin_src),
    ], capture_output=True, text=True, cwd=repo_root)
    assert proc.returncode == 0
    assert "Installed" in proc.stdout

    # list plugins
    proc = subprocess.run([
        sys.executable,
        str(repo_root / "plugins" / "plugin_manager.py"),
        "list",
    ], capture_output=True, text=True, cwd=repo_root, env={"CHAINHUNTER_PLUGIN_DIR": str(plugin_home)})
    assert proc.returncode == 0
    assert "sample_plugin" in proc.stdout

    # ensure CLI discovers plugin module
    proc = subprocess.run([
        sys.executable,
        str(repo_root / "cli" / "main.py"),
        "list",
    ], capture_output=True, text=True, cwd=repo_root, env={"CHAINHUNTER_PLUGIN_DIR": str(plugin_home)})
    assert "sample_mod" in proc.stdout
