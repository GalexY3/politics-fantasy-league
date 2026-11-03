"""The focal beta gate fails closed even on ambiguous test-runner output."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from scripts import beta_acceptance as acceptance


@pytest.mark.parametrize(
    "label,summary,expected",
    [
        ("python", "........ 23 passed in 1.00s", 23),
        ("node", "ℹ tests 35\nℹ pass 35\nℹ fail 0", 35),
        ("chrome_s9", "# pass 1\n# fail 0", 1),
    ],
)
def test_runner_accepts_verified_pass_totals(monkeypatch, label, summary, expected):
    def fake_run(*_args, **_kwargs):
        return SimpleNamespace(returncode=0, stdout=summary, stderr="")

    monkeypatch.setattr(acceptance.subprocess, "run", fake_run)
    result = acceptance._run(label, ("fixture",), timeout=1)
    assert result == {"label": label, "status": "PASS", "tests_passed": expected}


def test_runner_rejects_nonzero_exit_even_when_summary_claims_pass(monkeypatch):
    monkeypatch.setattr(
        acceptance.subprocess, "run",
        lambda *_a, **_k: SimpleNamespace(
            returncode=7, stdout="12 passed", stderr="internal failure"),
    )
    result = acceptance._run("python", ("fixture",), timeout=1)
    assert result["status"] == "FAILED"
    assert result["error"] == "NONZERO_EXIT"


def test_runner_rejects_success_without_a_parser_verifiable_pass_total(monkeypatch):
    monkeypatch.setattr(
        acceptance.subprocess, "run",
        lambda *_a, **_k: SimpleNamespace(returncode=0, stdout="OK", stderr=""),
    )
    result = acceptance._run("node", ("fixture",), timeout=1)
    assert result == {
        "label": "node", "status": "FAILED",
        "error": "NO_VERIFIABLE_PASS_TOTAL",
    }
