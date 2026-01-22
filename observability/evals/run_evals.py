"""Run automated regression evaluations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

DATASET_DIR = Path(__file__).resolve().parent / "datasets"


def _load_dataset(name: str) -> List[Dict[str, Any]]:
    path = DATASET_DIR / name
    if not path.exists():
        return []
    records: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        records.append(json.loads(line))
    return records


def run_regression_evals() -> Dict[str, Any]:
    """Return summary statistics for regression datasets."""
    golden = _load_dataset("golden.jsonl")
    synthetic = _load_dataset("synthetic.jsonl")
    return {
        "golden_cases": len(golden),
        "synthetic_cases": len(synthetic),
    }

