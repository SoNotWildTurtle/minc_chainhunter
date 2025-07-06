import sys
sys.path.insert(0, '.')

from analysis_db.neural_analyzer import (
    suggest_pipeline,
    update_model_from_results,
    save_model,
    load_model,
    MODEL_PATH,
)


def test_suggest_pipeline():
    results = [
        {"ports": [80, 443]},
        {"severity": "high", "ports": [22, 8080, 3306]},
    ]
    pipeline = suggest_pipeline(results)
    assert pipeline in {"bug_hunt", "extended_hunt", "repo_hunt"}


def test_update_model_from_results():
    stored = [
        {"module": "bug_hunt", "ports": [80]},
        {
            "module": "extended_hunt",
            "steps": [{"ports": [22, 80], "severity": "high"}],
        },
        {"module": "repo_hunt", "tags": ["secrets"], "ports": []},
    ]
    update_model_from_results(stored)
    pred = suggest_pipeline([{"ports": [22, 80], "severity": "high"}])
    assert pred in {"bug_hunt", "extended_hunt", "repo_hunt"}


def test_model_persistence(tmp_path):
    stored = [
        {"module": "bug_hunt", "ports": [80]},
        {"module": "extended_hunt", "ports": [22], "severity": "high"},
        {"module": "repo_hunt", "tags": ["secrets"]},
    ]
    temp_model = tmp_path / "model.pkl"
    try:
        # train and save
        update_model_from_results(stored)
        save_model(temp_model)
        assert temp_model.is_file()
        # load back
        load_model(temp_model)
        pred = suggest_pipeline([{"ports": [22], "severity": "high"}])
        assert pred in {"bug_hunt", "extended_hunt", "repo_hunt"}
    finally:
        if temp_model.is_file():
            temp_model.unlink()
