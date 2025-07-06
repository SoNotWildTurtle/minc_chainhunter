"""Suggest pipelines using a tiny neural network on scan results."""

from __future__ import annotations

from typing import Dict, List

import numpy as np
from sklearn.neural_network import MLPClassifier


# Pre-trained on synthetic data representing port counts and high severity flags
# 0 -> bug_hunt, 1 -> extended_hunt
_MODEL = MLPClassifier(hidden_layer_sizes=(4,), random_state=42, max_iter=500)
_X = np.array([
    [0, 0],
    [1, 0],
    [2, 0],
    [3, 1],
    [5, 2],
    [6, 2],
])
_y = np.array([0, 0, 0, 1, 1, 1])
_MODEL.fit(_X, _y)


def _extract_features(result: Dict) -> List[int]:
    """Return [ports, high_severity] feature vector from a result entry."""
    ports = len(result.get("ports", []))
    high = 1 if result.get("severity") == "high" else 0
    for step in result.get("steps", []):
        ports += len(step.get("ports", []))
        if step.get("severity") == "high":
            high += 1
    return [ports, high]


def update_model_from_results(results: List[Dict]) -> None:
    """Retrain the model using stored pipeline results."""
    X = []
    y = []
    for r in results:
        module = r.get("module")
        if module not in {"bug_hunt", "extended_hunt"}:
            continue
        X.append(_extract_features(r))
        y.append(0 if module == "bug_hunt" else 1)
    if not X:
        return
    X_arr = np.array(X)
    y_arr = np.array(y)
    if not hasattr(_MODEL, "classes_"):
        _MODEL.partial_fit(X_arr, y_arr, classes=np.array([0, 1]))
    else:
        _MODEL.partial_fit(X_arr, y_arr)


def suggest_pipeline(results: List[Dict]) -> str:
    """Return the suggested pipeline name for given scan results."""
    ports = sum(len(r.get("ports", [])) for r in results)
    high = sum(1 for r in results if r.get("severity") == "high")
    pred = _MODEL.predict(np.array([[ports, high]]))[0]
    return "extended_hunt" if pred else "bug_hunt"
