from pathlib import Path

def test_chainhunter_ps1_python_param():
    ps1 = Path('chainhunter.ps1')
    assert ps1.exists()
    text = ps1.read_text()
    assert '-Python' in text
