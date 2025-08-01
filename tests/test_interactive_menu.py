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
