import sys
sys.path.insert(0, '.')

from analysis_db.neural_analyzer import suggest_pipeline, update_model_from_results


def test_suggest_pipeline():
    results = [
        {"ports": [80, 443]},
        {"severity": "high", "ports": [22, 8080, 3306]},
    ]
    pipeline = suggest_pipeline(results)
    assert pipeline in {"bug_hunt", "extended_hunt"}


def test_update_model_from_results():
    stored = [
        {"module": "bug_hunt", "ports": [80]},
        {
            "module": "extended_hunt",
            "steps": [{"ports": [22, 80], "severity": "high"}],
        },
    ]
    update_model_from_results(stored)
    pred = suggest_pipeline([{"ports": [22, 80], "severity": "high"}])
    assert pred in {"bug_hunt", "extended_hunt"}
