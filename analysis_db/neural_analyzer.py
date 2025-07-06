"""Suggest pipelines using a tiny neural network on scan results."""

from __future__ import annotations

from typing import Dict, List
from pathlib import Path
import pickle

import numpy as np
from sklearn.neural_network import MLPClassifier


# Pre-trained on synthetic data representing port counts, high severity, and
# vulnerability totals. 0 -> bug_hunt, 1 -> extended_hunt
_MODEL = MLPClassifier(hidden_layer_sizes=(6,), random_state=42, max_iter=500)
_X = np.array([
    [0, 0, 0, 0],
    [1, 0, 1, 0],
    [2, 0, 1, 1],
    [3, 1, 2, 2],
    [5, 2, 3, 3],
    [7, 3, 4, 4],
])
_y = np.array([0, 0, 0, 1, 1, 1])
_MODEL.fit(_X, _y)

MODEL_PATH = Path(__file__).with_name("model.pkl")

def load_model(path: Path = MODEL_PATH) -> None:
    global _MODEL
    if path.is_file():
        try:
            with open(path, "rb") as f:
                _MODEL = pickle.load(f)
        except Exception:
            pass

def save_model(path: Path = MODEL_PATH) -> None:
    try:
        with open(path, "wb") as f:
            pickle.dump(_MODEL, f)
    except Exception:
        pass

load_model()


def _extract_features(result: Dict) -> List[int]:
    """Return [ports, high_severity, vuln_count, tag_count] from a result."""
    ports = len(result.get("ports", []))
    high = 1 if result.get("severity") == "high" else 0
    vulns = len(result.get("vulnerabilities", []))
    tags = len(result.get("tags", []))
    for step in result.get("steps", []):
        ports += len(step.get("ports", []))
        if step.get("severity") == "high":
            high += 1
        vulns += len(step.get("vulnerabilities", []))
        tags += len(step.get("tags", []))
    if "vuln_count" in result:
        vulns = result["vuln_count"]
    return [ports, high, vulns, tags]


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
    save_model()


def suggest_pipeline(results: List[Dict]) -> str:
    """Return the suggested pipeline name for given scan results."""
    ports = sum(len(r.get("ports", [])) for r in results)
    high = sum(1 for r in results if r.get("severity") == "high")
    vulns = sum(len(r.get("vulnerabilities", [])) for r in results)
    tags = sum(len(r.get("tags", [])) for r in results)
    pred = _MODEL.predict(np.array([[ports, high, vulns, tags]]))[0]
    return "extended_hunt" if pred else "bug_hunt"
