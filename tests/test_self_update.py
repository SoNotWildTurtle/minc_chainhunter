import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from cli.main import update_minc


def test_self_update(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True)
    (repo / "file.txt").write_text("v1")
    subprocess.run(["git", "add", "file.txt"], cwd=repo, check=True)
    env = os.environ.copy()
    env.update({
        'GIT_AUTHOR_NAME': 'test', 'GIT_AUTHOR_EMAIL': 't@example.com',
        'GIT_COMMITTER_NAME': 'test', 'GIT_COMMITTER_EMAIL': 't@example.com'
    })
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, env=env)

    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", remote.as_posix()], check=True)
    subprocess.run(["git", "remote", "add", "origin", remote.as_posix()], cwd=repo, check=True)
    subprocess.run(["git", "push", "-u", "origin", "master"], cwd=repo, check=True)

    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", remote.as_posix(), clone.as_posix()], check=True)
    (clone / "file.txt").write_text("v2")
    subprocess.run(["git", "commit", "-am", "update"], cwd=clone, check=True, env=env)
    subprocess.run(["git", "push"], cwd=clone, check=True)

    assert update_minc(False, repo_dir=str(repo))
    local = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo).strip()
    remote_head = subprocess.check_output(["git", "rev-parse", "origin/master"], cwd=repo).strip()
    assert local == remote_head
