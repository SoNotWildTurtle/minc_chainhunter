from pathlib import Path

def test_chainhunter_sh_contents():
    sh = Path('chainhunter.sh')
    assert sh.exists()
    text = sh.read_text()
    assert 'setup_ipc_bus.sh' in text
    assert '-Python' in text
