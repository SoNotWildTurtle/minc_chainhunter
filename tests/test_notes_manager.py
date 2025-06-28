import os
import importlib

import dev_notes.notes_manager as nm


def test_add_and_view(tmp_path, monkeypatch, capsys):
    path = tmp_path / 'notes.dat'
    monkeypatch.setitem(os.environ, 'DEV_NOTES_PATH', str(path))
    importlib.reload(nm)
    nm.add_note('one', tags=['code'])
    nm.add_note('two', tags=['code'])
    nm.add_note('three', tags=['personal'], personal=True)
    levels = [lvl for lvl, _ in nm.load_notes()]
    assert levels == [3, 2, 1]
    nm.view_notes(0)
    levels = [lvl for lvl, _ in nm.load_notes()]
    assert levels == [1, 2, 3]
    nm.view_notes(1, radius=1)
    captured = capsys.readouterr().out.strip().splitlines()
    assert any('two' in line for line in captured)
    # tag filtering
    nm.show_notes(tag='personal')
    captured = capsys.readouterr().out.strip()
    assert 'three' in captured


def test_context_and_alg(tmp_path, monkeypatch):
    path = tmp_path / 'notes.dat'
    monkeypatch.setitem(os.environ, 'DEV_NOTES_PATH', str(path))
    importlib.reload(nm)
    nm.add_note('first')
    nm.add_note('second', context=[1])
    nm.view_notes(1)
    levels = [lvl for lvl, _ in nm.load_notes()]
    assert levels[0] == 1
    meta = nm.load_notes()[1][1]
    assert meta['alg'] in ('zlib', 'lzma')


def test_lzma_usage(tmp_path, monkeypatch):
    path = tmp_path / 'notes.dat'
    monkeypatch.setitem(os.environ, 'DEV_NOTES_PATH', str(path))
    importlib.reload(nm)
    for i in range(9):
        nm.add_note(f'n{i}')
    level, meta = nm.load_notes()[0]
    assert level == 9
    assert meta['alg'] == 'lzma'
