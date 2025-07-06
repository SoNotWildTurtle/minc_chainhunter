"""Suggest pipelines using a tiny neural network on scan results."""

from __future__ import annotations

from typing import Dict, List, Tuple
from pathlib import Path
import pickle

import numpy as np
from sklearn.neural_network import MLPClassifier


# Pre-trained on synthetic data representing port counts, high severity, and
# vulnerability totals.
_MODEL = MLPClassifier(hidden_layer_sizes=(8,), random_state=42, max_iter=500)
_MODULE_MODEL = MLPClassifier(hidden_layer_sizes=(16,), random_state=42, max_iter=500)
_MODULE_MAP: Dict[str, int] = {}
_X = np.array([
    [0, 0, 0, 0],
    [1, 0, 1, 0],
    [2, 0, 1, 1],
    [3, 1, 2, 2],
    [5, 2, 3, 3],
    [7, 3, 4, 4],
    [1, 0, 0, 1],
    [4, 1, 1, 3],
])
_y = np.array([0, 0, 0, 1, 1, 1, 2, 2])
_MODEL.fit(_X, _y)

MODEL_PATH = Path(__file__).with_name("model.pkl")
MODULE_MODEL_PATH = Path(__file__).with_name("module_model.pkl")

def load_model(path: Path = MODEL_PATH) -> None:
    global _MODEL
    if path.is_file():
        try:
            with open(path, "rb") as f:
                _MODEL = pickle.load(f)
        except Exception:
            pass


def load_module_model(path: Path = MODULE_MODEL_PATH) -> None:
    global _MODULE_MODEL, _MODULE_MAP
    if path.is_file():
        try:
            with open(path, "rb") as f:
                _MODULE_MODEL, _MODULE_MAP = pickle.load(f)
        except Exception:
            pass

def save_model(path: Path = MODEL_PATH) -> None:
    try:
        with open(path, "wb") as f:
            pickle.dump(_MODEL, f)
    except Exception:
        pass


def save_module_model(path: Path = MODULE_MODEL_PATH) -> None:
    try:
        with open(path, "wb") as f:
            pickle.dump((_MODULE_MODEL, _MODULE_MAP), f)
    except Exception:
        pass

load_model()
load_module_model()


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


def _walk_results(result: Dict) -> List[Dict]:
    items = [result]
    for step in result.get("steps", []):
        items.extend(_walk_results(step))
    return items


def update_model_from_results(results: List[Dict]) -> None:
    """Retrain the model using stored pipeline results."""
    X = []
    y = []
    for r in results:
        module = r.get("module")
        if module not in {"bug_hunt", "extended_hunt", "repo_hunt"}:
            continue
        X.append(_extract_features(r))
        if module == "bug_hunt":
            y.append(0)
        elif module == "extended_hunt":
            y.append(1)
        else:
            y.append(2)
    if not X:
        return
    X_arr = np.array(X)
    y_arr = np.array(y)
    if not hasattr(_MODEL, "classes_"):
        _MODEL.partial_fit(X_arr, y_arr, classes=np.array([0, 1, 2]))
    else:
        _MODEL.partial_fit(X_arr, y_arr)
    save_model()


def update_module_model_from_results(results: List[Dict]) -> None:
    X: List[List[int]] = []
    y: List[int] = []
    for r in results:
        for entry in _walk_results(r):
            mod = entry.get("module")
            if not mod:
                continue
            if mod not in _MODULE_MAP:
                _MODULE_MAP[mod] = len(_MODULE_MAP)
            X.append(_extract_features(entry))
            y.append(_MODULE_MAP[mod])
    if not X:
        return
    X_arr = np.array(X)
    y_arr = np.array(y)
    if not hasattr(_MODULE_MODEL, "classes_"):
        _MODULE_MODEL.partial_fit(X_arr, y_arr, classes=np.arange(len(_MODULE_MAP)))
    else:
        _MODULE_MODEL.partial_fit(X_arr, y_arr)
    save_module_model()


def suggest_pipeline(results: List[Dict]) -> str:
    """Return the suggested pipeline name for given scan results."""
    ports = sum(len(r.get("ports", [])) for r in results)
    high = sum(1 for r in results if r.get("severity") == "high")
    vulns = sum(len(r.get("vulnerabilities", [])) for r in results)
    tags = sum(len(r.get("tags", [])) for r in results)
    pred = _MODEL.predict(np.array([[ports, high, vulns, tags]]))[0]
    if pred == 0:
        return "bug_hunt"
    if pred == 1:
        return "extended_hunt"
    return "repo_hunt"


def suggest_modules(results: List[Dict], top_n: int = 3) -> List[str]:
    """Return top module recommendations for given results."""
    if not _MODULE_MAP:
        return []
    ports = sum(len(r.get("ports", [])) for r in results)
    high = sum(1 for r in results if r.get("severity") == "high")
    vulns = sum(len(r.get("vulnerabilities", [])) for r in results)
    tags = sum(len(r.get("tags", [])) for r in results)
    feats = np.array([[ports, high, vulns, tags]])
    try:
        proba = _MODULE_MODEL.predict_proba(feats)[0]
    except Exception:
        return []
    items = sorted(_MODULE_MAP.items(), key=lambda kv: proba[kv[1]], reverse=True)
    return [name for name, _ in items[:top_n]]
