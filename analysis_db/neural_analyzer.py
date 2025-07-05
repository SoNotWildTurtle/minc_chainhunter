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


def suggest_pipeline(results: List[Dict]) -> str:
    """Return the suggested pipeline name for given scan results."""
    ports = sum(len(r.get("ports", [])) for r in results)
    high = sum(1 for r in results if r.get("severity") == "high")
    pred = _MODEL.predict(np.array([[ports, high]]))[0]
    return "extended_hunt" if pred else "bug_hunt"
