"""Bounded, repeatable local PFL scientific beta acceptance gate.

Run from any directory:
    python scripts/beta_acceptance.py

This is not the full historical suite, remote CI, or a public-release gate.
It exercises only the beta's affected local paths: Python HTTP/restart/roles,
Node S8/S9 read-only and SHA consumers, and the native Chrome guest journeys.
No originals, accounts from the user's demo, external services or real
politicians are consulted; tests use disposable loopback fixtures.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PYTHON_TESTS = (
    "tests/test_beta_acceptance_runner.py",
    "tests/test_beta_scientific_smoke.py",
    "tests/test_beta_readiness_endpoint.py",
    "tests/test_beta_local_launcher.py",
    "tests/test_beta_guest_link_launcher.py",
    "tests/test_beta_live_science_doctor.py",
    "tests/test_beta_live_science_doctor_runtime.py",
    "tests/test_beta_science_only.py",
    "tests/test_beta_restart_isolation.py",
    "tests/test_beta_concurrent_science_http.py",
    "tests/test_beta_snapshot_verifier.py",
    "tests/test_beta_offline_cut_comparison.py",
)
NODE_TESTS = (
    "tests/test_beta_guest_lab_explorer.mjs",
    "tests/test_beta_registry_comparison.mjs",
    "tests/test_beta_scientific_guest.mjs",
    "tests/test_s8_scientific_ui.mjs",
    "tests/test_s9_scientific_ui.mjs",
)
BROWSER_TESTS = (
    "tests/test_s9_chrome_registry.mjs",
    "tests/test_beta_accessibility.mjs",
)


def _run(label: str, command: tuple[str, ...], *, timeout: int) -> dict:
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src"),
           "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
    try:
        completed = subprocess.run(
            command, cwd=ROOT, env=env, text=True, encoding="utf-8",
            errors="replace", capture_output=True, check=False,
            timeout=timeout,
        )
    except FileNotFoundError:
        return {"label": label, "status": "UNAVAILABLE", "error": "EXECUTABLE_NOT_FOUND"}
    except subprocess.TimeoutExpired:
        return {"label": label, "status": "FAILED", "error": "TIMEOUT"}
    output = completed.stdout + "\n" + completed.stderr
    if label == "python":
        match = re.search(r"\b(\d+) passed\b", output)
    else:
        match = re.search(r"(?m)^(?:#|ℹ)\s+pass\s+(\d+)\s*$", output)
    if completed.returncode != 0:
        # Return only identifiers of VERSIONED tests; never copy arbitrary
        # traceback lines, user paths, cookies or raw fixture bytes into a
        # public machine-readable acceptance receipt.
        failed = re.findall(
            r"(?m)^(?:FAILED|ERROR) (tests/[A-Za-z0-9_./:\[\]-]+)",
            output)
        if label.startswith("chrome") or label == "node":
            failed.extend(re.findall(
                r"(?m)^\s*not ok \d+ - ([A-Za-z0-9_,.:/() \-]{1,120})\s*$",
                output))
        return {"label": label, "status": "FAILED", "error": "NONZERO_EXIT",
                "exit_code": completed.returncode,
                "failing_tests": failed[:5],
                "failure_identifiers_present": bool(failed)}
    if not match or int(match.group(1)) < 1:
        return {"label": label, "status": "FAILED", "error": "NO_VERIFIABLE_PASS_TOTAL"}
    return {"label": label, "status": "PASS", "tests_passed": int(match.group(1))}


def run() -> dict:
    steps = (
        ("python", (sys.executable, "-B", "-m", "pytest", "-q", *PYTHON_TESTS), 90),
        # Pin TAP rather than Node's environment-sensitive default reporter.
        # On failure its "not ok" identifiers can be safely redacted by _run,
        # without copying a traceback, local paths, cookies or fixture bytes.
        ("node", ("node", "--test", "--test-reporter=tap", *NODE_TESTS), 90),
        # Separate invocations avoid concurrent native-Chrome launches.
        ("chrome_s9", ("node", "--test", "--test-reporter=tap",
                        BROWSER_TESTS[0]), 60),
        ("chrome_accessibility", ("node", "--test", "--test-reporter=tap",
                                   BROWSER_TESTS[1]), 60),
    )
    results = []
    for label, command, timeout in steps:
        if any(not (ROOT / path).is_file() for path in (
                PYTHON_TESTS if label == "python"
                else NODE_TESTS if label == "node"
                else (BROWSER_TESTS[0],) if label == "chrome_s9"
                else (BROWSER_TESTS[1],))):
            results.append({"label": label, "status": "UNAVAILABLE",
                            "error": "EXPECTED_TEST_FILE_MISSING"})
            break
        result = _run(label, command, timeout=timeout)
        results.append(result)
        if result["status"] != "PASS":
            break
    try:
        head = subprocess.run(
            ("git", "rev-parse", "HEAD"), cwd=ROOT, capture_output=True,
            text=True, check=True, timeout=8,
        ).stdout.strip()
        tree = subprocess.run(
            ("git", "status", "--porcelain=v1"), cwd=ROOT, capture_output=True,
            text=True, check=True, timeout=8,
        ).stdout
        dirty = bool(tree.strip())
    except (OSError, subprocess.SubprocessError):
        head, dirty = None, None
    status = "PASS" if len(results) == len(steps) and all(
        step["status"] == "PASS" for step in results) else "FAIL"
    return {
        "schema": "pfl.beta_local_focal_acceptance.v1",
        "status": status,
        "scope": "LOCAL_SYNTHETIC_NONCYCLE_FOCAL_ONLY",
        # A dirty checkout means HEAD is a *baseline*, not the code tested.
        "git_head_at_execution": head,
        "working_tree_modified_at_execution": dirty,
        "execution_source_kind": ("UNCOMMITTED_WORKTREE" if dirty else
                                  "COMMITTED_HEAD" if dirty is False else
                                  "GIT_STATE_UNVERIFIED"),
        "checks": results,
        "tests_passed": sum(step.get("tests_passed", 0) for step in results),
        "test_sources_sha256": {
            path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for path in (*PYTHON_TESTS, *NODE_TESTS, *BROWSER_TESTS)
            if (ROOT / path).is_file()
        },
        "R5": "STOP_R5",
        "scientific_ab_cycles_added": 0,
        "new_empirical_sources_admitted": 0,
        "release_gates_passed": 0,
        "public_hosting_authorized": False,
    }


def main() -> int:
    report = run()
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
