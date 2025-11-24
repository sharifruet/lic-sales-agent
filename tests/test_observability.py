"""Tests for observability helpers."""

import os

from observability import langsmith_init
from observability.evals import run_evals


def test_langsmith_init_disabled(monkeypatch):
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    enabled = langsmith_init.init_langsmith("test-project")
    assert enabled is False


def test_langsmith_init_enabled(monkeypatch):
    monkeypatch.setenv("LANGSMITH_API_KEY", "dummy")
    enabled = langsmith_init.init_langsmith("test-project")
    assert enabled is True
    assert os.environ.get("LANGCHAIN_PROJECT") == "test-project"


def test_run_regression_evals_returns_counts():
    summary = run_evals.run_regression_evals()
    assert "golden_cases" in summary
    assert "synthetic_cases" in summary
    assert summary["golden_cases"] >= 0

