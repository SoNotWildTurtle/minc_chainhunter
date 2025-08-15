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
_PARAM_STATS: Dict[str, Dict[Tuple[str, ...], Tuple[int, int]]] = {}
_MODULE_INTERACTIONS: Dict[str, Dict[str, int]] = {}
_THRESHOLD = 0.5
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
INTERACTIONS_PATH = Path(__file__).with_name("module_interactions.json")

def load_model(path: Path = MODEL_PATH) -> None:
    global _MODEL
    if path.is_file():
        try:
            with open(path, "rb") as f:
                _MODEL = pickle.load(f)
        except Exception:
            pass


def load_module_model(path: Path = MODULE_MODEL_PATH) -> None:
    global _MODULE_MODEL, _MODULE_MAP, _PARAM_STATS
    if path.is_file():
        try:
            with open(path, "rb") as f:
                _MODULE_MODEL, _MODULE_MAP, _PARAM_STATS = pickle.load(f)
        except Exception:
            pass


def load_interactions(path: Path = INTERACTIONS_PATH) -> None:
    global _MODULE_INTERACTIONS
    if path.is_file():
        try:
            import json

            with open(path, "r", encoding="utf-8") as f:
                _MODULE_INTERACTIONS = json.load(f)
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
            pickle.dump((_MODULE_MODEL, _MODULE_MAP, _PARAM_STATS), f)
    except Exception:
        pass


def save_interactions(path: Path = INTERACTIONS_PATH) -> None:
    try:
        import json

        with open(path, "w", encoding="utf-8") as f:
            json.dump(_MODULE_INTERACTIONS, f)
    except Exception:
        pass

load_model()
load_module_model()
load_interactions()


def set_threshold(value: float) -> None:
    """Set probability threshold for module suggestions."""
    global _THRESHOLD
    _THRESHOLD = max(0.0, min(1.0, float(value)))



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


def _extract_module_features(result: Dict) -> List[int]:
    """Return features including code metrics for module model."""
    feats = _extract_features(result)
    feats.append(int(result.get("code_funcs", 0)))
    feats.append(int(result.get("code_lines", 0)))
    return feats


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
    global _MODULE_MODEL
    X: List[List[int]] = []
    y: List[int] = []
    for r in results:
        for entry in _walk_results(r):
            mod = entry.get("module")
            if not mod:
                continue
            if mod not in _MODULE_MAP:
                _MODULE_MAP[mod] = len(_MODULE_MAP)
            X.append(_extract_module_features(entry))
            y.append(_MODULE_MAP[mod])
    if not X:
        return
    X_arr = np.array(X)
    y_arr = np.array(y)
    classes = np.arange(len(_MODULE_MAP))
    if not hasattr(_MODULE_MODEL, "classes_") or len(_MODULE_MODEL.classes_) != len(classes):
        _MODULE_MODEL = MLPClassifier(hidden_layer_sizes=(16,), random_state=42, max_iter=500)
        _MODULE_MODEL.partial_fit(X_arr, y_arr, classes=classes)
    else:
        _MODULE_MODEL.partial_fit(X_arr, y_arr, classes=classes)
    save_module_model()


def update_interactions_from_results(results: List[Dict]) -> None:
    """Update module interaction counts from sequential results."""
    prev = None
    for r in results:
        mod = r.get("module")
        if prev and mod:
            nxts = _MODULE_INTERACTIONS.setdefault(prev, {})
            nxts[mod] = nxts.get(mod, 0) + 1
        steps = r.get("steps", [])
        prev_step = mod
        for step in steps:
            s_mod = step.get("module")
            if prev_step and s_mod:
                nxts = _MODULE_INTERACTIONS.setdefault(prev_step, {})
                nxts[s_mod] = nxts.get(s_mod, 0) + 1
            prev_step = s_mod
        prev = mod if steps == [] else prev_step
    save_interactions()


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


def suggest_modules(results: List[Dict], top_n: int = 3, prev: str | None = None) -> List[str]:
    """Return top module recommendations for given results or followups."""
    if prev and _MODULE_INTERACTIONS.get(prev):
        items = sorted(
            _MODULE_INTERACTIONS[prev].items(), key=lambda kv: kv[1], reverse=True
        )
        return [name for name, _ in items[:top_n]]
    if not _MODULE_MAP:
        return []
    ports = sum(len(r.get("ports", [])) for r in results)
    high = sum(1 for r in results if r.get("severity") == "high")
    vulns = sum(len(r.get("vulnerabilities", [])) for r in results)
    tags = sum(len(r.get("tags", [])) for r in results)
    funcs = sum(int(r.get("code_funcs", 0)) for r in results)
    lines = sum(int(r.get("code_lines", 0)) for r in results)
    feats = np.array([[ports, high, vulns, tags, funcs, lines]])
    try:
        proba = _MODULE_MODEL.predict_proba(feats)[0]
    except Exception:
        return []
    items = sorted(_MODULE_MAP.items(), key=lambda kv: proba[kv[1]], reverse=True)
    filtered = [name for name, idx in items if proba[idx] >= _THRESHOLD]
    if not filtered:
        filtered = [name for name, _ in items[:1]]
    return filtered[:top_n]


def update_model_from_cve(path: str) -> None:
    """Extend training data using a small CVE dataset JSON file."""
    try:
        import json

        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)
    except Exception:
        return

    X: List[List[int]] = []
    y: List[int] = []
    for it in items:
        feats = [
            len(it.get("ports", [])),
            1 if it.get("severity") == "high" else 0,
            int(it.get("vuln_count", 0)),
            len(it.get("tags", [])),
        ]
        X.append(feats)
        label = {
            "bug_hunt": 0,
            "extended_hunt": 1,
            "repo_hunt": 2,
        }.get(it.get("pipeline", "bug_hunt"), 0)
        y.append(label)
    if not X:
        return
    X_arr = np.array(X)
    y_arr = np.array(y)
    if not hasattr(_MODEL, "classes_"):
        _MODEL.partial_fit(X_arr, y_arr, classes=np.array([0, 1, 2]))
    else:
        _MODEL.partial_fit(X_arr, y_arr)
    save_model()


def _flatten_params(model: MLPClassifier) -> np.ndarray:
    """Return all learnable parameters as a single vector."""
    params = []
    for coef in model.coefs_:
        params.append(coef.ravel())
    for inter in model.intercepts_:
        params.append(inter)
    return np.concatenate(params)


def reinforce_from_cases(path: str) -> float:
    """Reinforce the model using successful bug bounty cases.

    Returns the L2 distance between old and new parameters so callers can
    measure the effect of training.
    """
    try:
        import json

        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)
    except Exception:
        return

    X: List[List[int]] = []
    y: List[int] = []
    w: List[float] = []
    for it in items:
        feats = [
            len(it.get("ports", [])),
            1 if it.get("severity") == "high" else 0,
            int(it.get("vuln_count", 0)),
            len(it.get("tags", [])),
        ]
        X.append(feats)
        label = {
            "bug_hunt": 0,
            "extended_hunt": 1,
            "repo_hunt": 2,
        }.get(it.get("pipeline", "bug_hunt"), 0)
        y.append(label)
        w.append(float(it.get("reward", it.get("vuln_count", 1))))
    if not X:
        return 0.0
    old_params = _flatten_params(_MODEL)
    X_arr = np.array(X)
    y_arr = np.array(y)
    w_arr = np.array(w)
    if not hasattr(_MODEL, "classes_"):
        _MODEL.partial_fit(
            X_arr,
            y_arr,
            classes=np.array([0, 1, 2]),
            sample_weight=w_arr,
        )
    else:
        _MODEL.partial_fit(X_arr, y_arr, sample_weight=w_arr)
    save_model()
    new_params = _flatten_params(_MODEL)
    diff = float(np.linalg.norm(new_params - old_params))
    return diff


def update_param_stats_from_results(results: List[Dict]) -> None:
    """Update parameter statistics from stored results."""
    for r in results:
        for entry in _walk_results(r):
            mod = entry.get("module")
            if not mod:
                continue
            params = tuple(entry.get("params") or [])
            count = entry.get("vuln_count", len(entry.get("vulnerabilities", [])))
            stats = _PARAM_STATS.setdefault(mod, {})
            total, n = stats.get(params, (0, 0))
            stats[params] = (total + count, n + 1)


def suggest_params(module: str, top_n: int = 3) -> List[List[str]]:
    """Return parameter recommendations for a module."""
    stats = _PARAM_STATS.get(module)
    if not stats:
        return []
    items = sorted(
        stats.items(),
        key=lambda kv: (kv[1][0] / kv[1][1]) if kv[1][1] else 0,
        reverse=True,
    )
    return [list(p) for p, _ in items[:top_n]]

