"""Test the disposable local scientific beta HTTP smoke."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_beta_scientific_smoke_one_command_real_http_and_synthetic_intake():
    outcome = subprocess.run(
        [sys.executable, "-B", str(ROOT / "scripts" / "beta_scientific_smoke.py")],
        cwd=ROOT, encoding="utf-8", capture_output=True, check=False,
        env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"},
        timeout=55,
    )
    assert outcome.returncode == 0, outcome.stdout + outcome.stderr
    assert not outcome.stderr, outcome.stderr
    receipt = json.loads(outcome.stdout)
    assert receipt["schema"] == "pfl.beta_scientific_http_smoke.v1"
    assert receipt["status"] == "PASS"
    assert receipt["scope"] == "EPHEMERAL_AUTHOR_CLOSED_LOOPBACK_ONLY"
    assert receipt["synthetic"] is True
    assert receipt["checks_passed"] == 9
    assert set(receipt["checks"]) == {
        "loopback_health", "local_preflight_distinct_from_public_release",
        "real_http_python_node_lab_s7",
        "durable_v4_empty_overlay", "three_independent_cli_enrollments",
        "accepted_rejected_and_receipt_changed", "early_cut_no_future_intakes",
        "http_400_and_host_403", "tampered_schema_http_503",
    }
    for key in ("initial_receipt_sha256", "enrolled_receipt_sha256"):
        assert re.fullmatch(r"[0-9a-f]{64}", receipt[key])
    assert receipt["initial_receipt_sha256"] != receipt["enrolled_receipt_sha256"]
    assert receipt["R5"] == "STOP_R5"
    assert receipt["new_empirical_sources"] == 0
    assert receipt["scientific_ab_cycles"] == 0
    assert receipt["release_gates_passed"] == 0
    assert "AUTHOR_ALPHA" not in outcome.stdout
    assert "AUTHOR_BETA" not in outcome.stdout
    assert "accounts.sqlite3" not in outcome.stdout
