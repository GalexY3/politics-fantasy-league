"""NTFS destination-parent junction swap at private-output publishing boundaries.

All data and candidate Git worktrees are disposable pytest temp fixtures.
The harness runs under one Windows identity: no second token or participant
access is claimed. The desired behavior is fail-closed with no published
supervisor-only JSON in the alternate directory.
"""
from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess

import pytest

from test_beta_operator_instrument_versioning import _prepared_v2
from test_beta_operator_artifact_security import _get_acl


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "beta_science_operator_protocol.py"
WINDOWS = pytest.mark.skipif(os.name != "nt", reason="Real Windows junction semantics")


@pytest.fixture
def protocol():
    spec = importlib.util.spec_from_file_location("beta_output_alias_race_probe", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _main(protocol, *items):
    output = io.StringIO()
    with redirect_stdout(output):
        status = protocol.main([str(item) for item in items])
    raw = output.getvalue()
    assert raw.count("\n") == 1
    report = json.loads(raw)
    assert report.get("participant_count") is None
    return status, report, raw


def _public_parent(path: Path):
    path.mkdir(exist_ok=True)
    grant = subprocess.run(
        ["icacls", str(path), "/grant", "*S-1-1-0:(OI)(CI)(R)"],
        capture_output=True, check=False,
    )
    assert grant.returncode == 0, grant.stderr.decode(errors="replace")
    assert _get_acl(path)["everyone_read"] is True


def _replace_with_junction(private: Path, redirect: Path, parked: Path):
    assert private.is_dir() and not private.is_junction()
    assert redirect.is_dir()
    private.rename(parked)
    made = subprocess.run(
        ["cmd.exe", "/c", "mklink", "/J", str(private), str(redirect)],
        capture_output=True, check=False,
    )
    if made.returncode:
        parked.rename(private)
    assert made.returncode == 0, made.stderr.decode(errors="replace")
    assert private.is_junction()
    assert private.resolve(strict=True) == redirect.resolve(strict=True)


def _restore(private: Path, parked: Path):
    if private.is_junction():
        private.rmdir()
    if parked.exists():
        parked.rename(private)
    assert private.is_dir() and not private.is_junction()


def _coded(tmp_path, stem):
    _, rubric, _, source, handout, rubric_path = _prepared_v2(tmp_path, stem)
    assert rubric_path.exists() and rubric["schema"].endswith(".v2")
    # The participant handout lives in a different directory already.
    assert source.parent != handout.parent
    return source, rubric, rubric_path, handout.parent


@WINDOWS
@pytest.mark.parametrize("destination_kind", ("public", "disposable_git"))
def test_private_record_rejects_junction_parent_swap_before_stage_open(
    tmp_path, monkeypatch, protocol, destination_kind,
):
    source, _, _, public = _coded(tmp_path, "stage junction " + destination_kind)
    private = source.parent
    protected = source.read_bytes()
    alternative = public if destination_kind == "public" else tmp_path / "fake Git only"
    _public_parent(alternative)
    if destination_kind == "disposable_git":
        (alternative / ".git").mkdir()
    destination = private / ("private successor " + destination_kind + ".json")
    parked = tmp_path / ("parked original " + destination_kind)
    real_open = Path.open
    seen = []

    def intercept(path, mode="r", *args, **kwargs):
        if (not seen and mode == "xb"
                and path.parent == private and path.name.startswith(".pfl-stage-")):
            assert protocol._windows_dacl_safe(private, require_protected=True)
            seen.append(path.name)
            _replace_with_junction(private, alternative, parked)
        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", intercept)
    try:
        rc, report, raw = _main(
            protocol, "--record-form", source, destination,
            "OP01", "TECH_COMPLETED", "A", "UX_CLEAR")
        assert len(seen) == 1, "Race must reach the actual stage.open boundary"
        assert rc != 0 and report["status"] == "OPERATOR_REJECTED"
        assert report["error_code"] == "OPERATOR_PRIVATE_OUTPUT_UNVERIFIED"
        assert not (alternative / destination.name).exists()
        assert not (alternative / seen[0]).exists()
        assert str(destination) not in raw and str(source) not in raw
        assert (parked / source.name).read_bytes() == protected
        if destination_kind == "disposable_git":
            assert {x.name for x in alternative.iterdir()} == {".git"}
    finally:
        _restore(private, parked)
    assert not destination.exists()


@WINDOWS
@pytest.mark.parametrize("destination_kind", ("public", "disposable_git"))
def test_private_score_rejects_junction_parent_swap_at_hardlink(
    tmp_path, monkeypatch, protocol, destination_kind,
):
    source, rubric, rubric_path, public = _coded(
        tmp_path, "link junction " + destination_kind)
    private = source.parent
    recorded = private / "recorded before junction.json"
    code, receipt, _ = _main(
        protocol, "--record-form", source, recorded,
        "OP01", "TECH_COMPLETED",
        rubric["tasks"][0]["correct_answer_code"], "UX_CLEAR")
    assert code == 0 and receipt["status"] == "OPERATOR_FORM_OBSERVATION_RECORDED"
    recorded_before = recorded.read_bytes()
    alternative = public if destination_kind == "public" else tmp_path / "fake Git link"
    _public_parent(alternative)
    if destination_kind == "disposable_git":
        (alternative / ".git").mkdir()
    destination = private / ("private score " + destination_kind + ".json")
    parked = tmp_path / ("parked link original " + destination_kind)
    real_link = os.link
    seen = []

    def intercept(src, dst, *args, **kwargs):
        if (not seen and Path(dst) == destination
                and Path(src).name.startswith(".pfl-stage-")):
            assert Path(src).is_file() and Path(src).stat().st_nlink == 1
            assert protocol._windows_dacl_safe(Path(src), require_protected=False)
            seen.append(Path(src).name)
            _replace_with_junction(private, alternative, parked)
        return real_link(src, dst, *args, **kwargs)

    monkeypatch.setattr(os, "link", intercept)
    try:
        rc, report, raw = _main(
            protocol, "--evaluate-form", recorded, rubric_path, destination)
        assert len(seen) == 1, "Race must reach actual os.link after private write"
        assert rc != 0 and report["status"] == "OPERATOR_REJECTED"
        assert report["error_code"] == "OPERATOR_OUTPUT_WRITE_FAILED"
        assert not (alternative / destination.name).exists()
        assert not (alternative / seen[0]).exists()
        assert str(destination) not in raw and str(recorded) not in raw
        assert (parked / recorded.name).read_bytes() == recorded_before
        if destination_kind == "disposable_git":
            assert {x.name for x in alternative.iterdir()} == {".git"}
    finally:
        _restore(private, parked)
    assert not destination.exists()
    # On failure after the descriptor has been closed, the random stage can
    # remain inside the original restricted directory under its renamed path.
    for stage in private.glob(".pfl-stage-*.tmp"):
        assert protocol._windows_dacl_safe(stage, require_protected=False)
        stage.unlink()


@WINDOWS
def test_private_record_control_without_destination_alias_swap(tmp_path, protocol):
    source, _, _, _ = _coded(tmp_path, "clean control")
    destination = source.parent / "successful private control.json"
    before = source.read_bytes()
    rc, report, raw = _main(
        protocol, "--record-form", source, destination,
        "OP01", "TECH_COMPLETED", "A", "UX_CLEAR")
    assert rc == 0 and report["status"] == "OPERATOR_FORM_OBSERVATION_RECORDED"
    assert destination.exists() and destination.stat().st_nlink == 1
    assert protocol._windows_dacl_safe(destination, require_protected=False)
    assert source.read_bytes() == before
    assert str(destination) not in raw
