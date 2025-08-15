from scripts.setup_verifier import load_checks


def test_load_checks_parses_entries():
    checks = load_checks()
    assert any(c["id"] == "SV01" for c in checks)
    assert all("status" in c for c in checks)
