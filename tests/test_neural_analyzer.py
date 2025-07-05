import sys
sys.path.insert(0, '.')

from analysis_db.neural_analyzer import suggest_pipeline


def test_suggest_pipeline():
    results = [
        {"ports": [80, 443]},
        {"severity": "high", "ports": [22, 8080, 3306]},
    ]
    pipeline = suggest_pipeline(results)
    assert pipeline in {"bug_hunt", "extended_hunt"}
