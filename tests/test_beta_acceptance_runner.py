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
    assert result["failing_tests"] == []
    assert result["failure_identifiers_present"] is False


def test_runner_keeps_versioned_failure_ids_but_never_raw_traceback(monkeypatch):
    log = (
        "FAILED tests/test_beta_restart_isolation.py::test_two_real_server_processes - "
        "AssertionError\n"
        "C:\\Users\\test\\private\\accounts.sqlite3 was locked\n"
    )
    monkeypatch.setattr(
        acceptance.subprocess, "run",
        lambda *_a, **_k: SimpleNamespace(returncode=1, stdout=log, stderr=""),
    )
    result = acceptance._run("python", ("fixture",), timeout=1)
    assert result["status"] == "FAILED"
    assert result["failure_identifiers_present"] is True
    assert result["failing_tests"] == [
        "tests/test_beta_restart_isolation.py::test_two_real_server_processes"]
    assert "private" not in str(result)


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


def test_tap_runner_failure_keeps_only_safe_title_not_path(monkeypatch):
    # Reproduces a concrete previous blind spot: Chrome stage exit nonzero
    # with no test identifier captured from the default Node reporter.
    # The actual earlier Chrome failure CAUSE remains unverified.
    tap = (
        "not ok 1 - Chrome CDP guest restore verification\n"
        "  error: C:\\Users\\test\\private\\cookie-secret.txt\n"
        "# tests 1\n# pass 0\n# fail 1\n"
    )
    monkeypatch.setattr(
        acceptance.subprocess, "run",
        lambda *_a, **_k: SimpleNamespace(
            returncode=1, stdout=tap, stderr=""),
    )
    result = acceptance._run("chrome_accessibility", ("fixture",), timeout=1)
    assert result["status"] == "FAILED"
    assert result["failing_tests"] == ["Chrome CDP guest restore verification"]
    assert result["failure_identifiers_present"] is True
    assert "cookie-secret" not in str(result)
    assert "C:\\Users" not in str(result)


def test_focal_browser_and_node_commands_explicitly_pin_tap(monkeypatch):
    collected = []
    def fake_run(label, command, *, timeout):
        del timeout
        collected.append((label, command))
        return {"label": label, "status": "PASS", "tests_passed": 1}
    monkeypatch.setattr(acceptance, "_run", fake_run)
    report = acceptance.run()
    assert report["status"] == "PASS"
    assert len(collected) == 4
    for label, command in collected:
        if label in {"node", "chrome_s9", "chrome_accessibility"}:
            assert "--test-reporter=tap" in command
        else:
            assert "--test-reporter=tap" not in command


def test_runner_rejects_skipped_native_chrome_in_python_stage(monkeypatch):
    # The S8 browser test used to be optional. When included in the beta gate,
    # a skip must not masquerade as a successful physical JSON download.
    monkeypatch.setattr(
        acceptance.subprocess, "run",
        lambda *_a, **_k: SimpleNamespace(
            returncode=0, stdout="245 passed, 1 skipped in 45.2s", stderr="",
        ),
    )
    result = acceptance._run("python", ("fixture",), timeout=1)
    assert result == {
        "label": "python",
        "status": "FAILED",
        "error": "REQUIRED_PYTHON_TEST_SKIPPED",
    }
