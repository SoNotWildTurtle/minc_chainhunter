from pathlib import Path

def test_chainhunter_ps1_python_param():
    ps1 = Path('chainhunter.ps1')
    assert ps1.exists()
    text = ps1.read_text()
    assert '-Python' in text
    assert 'Stop-Process' in text
    assert 'install_requirements.py' in text
