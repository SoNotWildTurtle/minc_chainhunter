from pathlib import Path

def test_windows_batch_scripts():
    setup = Path('scripts/setup_ipc_bus.bat')
    service = Path('scripts/install_service.bat')
    for path in (setup, service):
        assert path.exists()
        text = path.read_text()
        assert 'powershell.exe' in text
        assert 'Start-Process -FilePath powershell.exe -Verb RunAs' in text
