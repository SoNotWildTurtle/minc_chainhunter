import os
from pathlib import Path
from sandbox.debugger import apply_evolution
from sandbox.memory_patcher import patch_file, rollback_file

def test_apply_evolution(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text("hello")

    def patch(repo: Path):
        target = repo / "sample.txt"
        target.write_text("patched")

    # copy repo from tmp_path only
    assert apply_evolution(patch, repo_dir=str(tmp_path), run_tests=False)
    assert sample.read_text() == "hello"  # original untouched


def test_patch_file(tmp_path):
    f = tmp_path / "data.bin"
    f.write_bytes(b"ABCDEFG")
    patch_file(f, 2, b"ZZ")
    assert f.read_bytes() == b"ABZZEFG"
    backup = f.with_suffix(f.suffix + ".bak")
    assert backup.exists()
    rollback_file(f)
    assert not backup.exists()
    assert f.read_bytes() == b"ABCDEFG"
