import io
import contextlib
import sys

from cli import main as cm


def test_menu_shows_pipelines_and_shortcuts():
    cm.MODULES = cm.discover_modules()
    buf = io.StringIO()
    buf.isatty = lambda: False
    with contextlib.redirect_stdout(buf):
        cm.show_interactive_menu()
    out = buf.getvalue()
    assert "Pipelines:" in out
    assert "[a] Generate report" in out
    assert "[g] Gather artifacts" in out
    assert "[t] Retrain neural model" in out
    assert "[o] Operator actions" in out


def test_numeric_selection_runs_correct_module(monkeypatch):
    """Ensure selecting a numbered menu entry launches that module."""
    from cli import main as cm

    modules = {
        "ping_sweep": {"type": "recon", "path": "", "doc": "", "functions": []},
        "sqli_scanner": {"type": "vuln", "path": "", "doc": "", "functions": []},
    }

    monkeypatch.setattr(cm, "discover_modules", lambda: modules)

    called = {}

    def fake_run(name, args):
        called["name"] = name
        return True

    monkeypatch.setattr(cm, "run_module", fake_run)
    monkeypatch.setattr(cm, "show_module_usage", lambda name: None)
    monkeypatch.setattr(
        cm,
        "get_module_info",
        lambda name: {"type": modules[name]["type"], "path": "", "doc": "", "functions": []},
    )

    inputs = iter(["1", "q"])
    monkeypatch.setattr("builtins.input", lambda prompt='': next(inputs))

    cm.interactive_mode()

    assert called["name"] == "ping_sweep"
