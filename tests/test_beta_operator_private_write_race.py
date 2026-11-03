"""Real NTFS ACL publication race: synthetic supervisor-only v2 fixtures.

This test requires a Windows local filesystem supporting inherited DACLs.
It uses only pytest tmp_path outside Git and the same local account.  The
mutation is deterministic: icacls expands the *parent* DACL immediately
before the real stage.open('xb') in the existing publisher.  Tests establish
actual resulting ACLs, not access from a different Windows security token.
"""
from __future__ import annotations

from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess

import pytest

from test_beta_operator_artifact_security import _get_acl
from test_beta_operator_instrument_versioning import _prepared_v2


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "beta_science_operator_protocol.py"
NTFS_ONLY = pytest.mark.skipif(os.name != "nt", reason="Real Windows NTFS DACL test")


@pytest.fixture
def protocol():
    spec = importlib.util.spec_from_file_location("beta_private_write_race_probe", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _main(protocol, *args: object) -> tuple[int, dict, str]:
    sink = io.StringIO()
    with redirect_stdout(sink):
        status = protocol.main([str(item) for item in args])
    stdout = sink.getvalue()
    assert stdout.count("\n") == 1
    result = json.loads(stdout)
    assert result.get("participant_count") is None
    return status, result, stdout


def _inject_public_inheritance_before_stage(monkeypatch, protocol, parent: Path):
    """Hook only the real stage creation, after all caller-side ACL checks."""
    assert parent.is_dir()
    assert protocol._windows_dacl_safe(parent, require_protected=True)
    assert not _get_acl(parent)["everyone_read"]
    real_open = Path.open
    events = []

    def stage_open(path, mode="r", *args, **kwargs):
        if (Path(path).parent == parent and Path(path).name.startswith(".pfl-stage-")
                and mode == "xb" and not events):
            assert protocol._windows_dacl_safe(parent, require_protected=True), (
                "Private parent was not secure just before intended mutation")
            grant = subprocess.run(
                ["icacls", str(parent), "/grant", "*S-1-1-0:(OI)(CI)(R)"],
                capture_output=True, check=False,
            )
            assert grant.returncode == 0, grant.stderr.decode(errors="replace")
            parent_acl = _get_acl(parent)
            assert parent_acl["everyone_read"] is True, parent_acl
            assert not protocol._windows_dacl_safe(parent, require_protected=True), (
                "Real private-parent Windows DACL audit should now reject Everyone")
            events.append({"stage_name": Path(path).name, "parent_acl": parent_acl})
        stream = real_open(path, mode, *args, **kwargs)
        if (events and Path(path).parent == parent
                and Path(path).name == events[0]["stage_name"] and mode == "xb"):
            # The stage was CREATED only after the broad inheritable ACE.
            acl = _get_acl(Path(path))
            events[0]["stage_acl"] = acl
            events[0]["stage_identity"] = (
                os.fstat(stream.fileno()).st_dev, os.fstat(stream.fileno()).st_ino)
        return stream

    monkeypatch.setattr(Path, "open", stage_open)
    return events


def _assert_real_broad_publication(destination: Path, events: list[dict]):
    assert len(events) == 1, "Injection must occur at the actual output stage.open"
    assert events[0]["parent_acl"]["everyone_read"] is True
    assert events[0]["stage_acl"]["everyone_read"] is True, events[0]["stage_acl"]
    assert destination.is_file()
    assert destination.stat().st_nlink == 1
    assert (destination.stat().st_dev, destination.stat().st_ino) == (
        events[0]["stage_identity"])
    published_acl = _get_acl(destination)
    assert published_acl["everyone_read"] is True, published_acl
    assert len(destination.read_bytes()) > 0


@NTFS_ONLY
def test_prepatch_red_record_form_rejects_public_acl_inherited_at_stage_open(
    tmp_path, monkeypatch, protocol,
):
    blank, rubric, _, source, _, rubric_path = _prepared_v2(
        tmp_path, "write-race record Ω")
    assert blank["schema"] == protocol.FORM_INPUT_SCHEMA
    assert rubric_path.is_file() and rubric["schema"] == protocol.FORM_TEMPLATE_SCHEMA
    original = source.read_bytes()
    destination = source.parent / "private synthetic successor race.json"
    events = _inject_public_inheritance_before_stage(
        monkeypatch, protocol, source.parent)

    code, receipt, stdout = _main(
        protocol, "--record-form", source, destination,
        "OP01", "TECH_COMPLETED", "A", "UX_CLEAR",
    )
    assert events
    if code == 0:
        _assert_real_broad_publication(destination, events)
        successor = json.loads(destination.read_bytes())
        assert successor["predecessor_sha256"] == hashlib.sha256(original).hexdigest()
        row = next(x for x in successor["observations"] if x["task_id"] == "OP01")
        assert row["technical"] == "TECH_COMPLETED" and row["scientific"] == "A"
        assert receipt["destination_sha256"] == hashlib.sha256(
            destination.read_bytes()).hexdigest()
    assert code != 0, "Must not publish private coded revision with Everyone-read ACL"
    assert receipt["status"] == "OPERATOR_REJECTED"
    assert not destination.exists()
    assert source.read_bytes() == original
    assert str(source) not in stdout and str(destination) not in stdout


@NTFS_ONLY
def test_prepatch_red_evaluate_form_rejects_public_acl_inherited_at_stage_open(
    tmp_path, monkeypatch, protocol,
):
    _, rubric, _, source, _, rubric_path = _prepared_v2(
        tmp_path, "write-race score Ω")
    # Populate one task before the race with an ordinary, OS-private revision.
    recorded = source.parent / "coded score source prior to race.json"
    code, preliminary, _ = _main(
        protocol, "--record-form", source, recorded,
        "OP01", "TECH_COMPLETED",
        rubric["tasks"][0]["correct_answer_code"], "UX_CLEAR",
    )
    assert code == 0 and preliminary["status"] == "OPERATOR_FORM_OBSERVATION_RECORDED"
    raw_recorded = recorded.read_bytes()
    assert protocol._windows_dacl_safe(recorded, require_protected=False)
    destination = source.parent / "private synthetic scored race.json"
    events = _inject_public_inheritance_before_stage(
        monkeypatch, protocol, source.parent)

    code, receipt, stdout = _main(
        protocol, "--evaluate-form", recorded, rubric_path, destination,
    )
    assert events
    if code == 0:
        _assert_real_broad_publication(destination, events)
        result = json.loads(destination.read_bytes())
        assert result["coded_input_sha256"] == hashlib.sha256(raw_recorded).hexdigest()
        assert result["rollup"]["scientific"]["SCI_CORRECT"] == 1
        assert receipt["sha256"] == hashlib.sha256(destination.read_bytes()).hexdigest()
    assert code != 0, "Must not export supervisor-only scores under Everyone-read ACL"
    assert receipt["status"] == "OPERATOR_REJECTED"
    assert not destination.exists()
    assert recorded.read_bytes() == raw_recorded
    assert str(recorded) not in stdout and str(destination) not in stdout


@NTFS_ONLY
def test_private_stage_control_without_acl_race_preserves_private_publish(
    tmp_path, protocol,
):
    blank, _, _, source, _, _ = _prepared_v2(tmp_path, "write-race control Ω")
    assert blank["schema"] == protocol.FORM_INPUT_SCHEMA
    destination = source.parent / "safe coded successor control.json"
    before = source.read_bytes()
    assert protocol._windows_dacl_safe(source.parent, require_protected=True)
    code, receipt, stdout = _main(
        protocol, "--record-form", source, destination,
        "OP01", "TECH_COMPLETED", "A", "UX_CLEAR",
    )
    assert code == 0, receipt
    assert receipt["status"] == "OPERATOR_FORM_OBSERVATION_RECORDED"
    assert destination.stat().st_nlink == 1
    assert _get_acl(destination)["everyone_read"] is False
    assert protocol._windows_dacl_safe(destination, require_protected=False)
    assert source.read_bytes() == before
    assert str(destination) not in stdout


@NTFS_ONLY
def test_private_form_preparation_rejects_acl_change_before_key_stage(
    tmp_path, monkeypatch, protocol,
):
    private = tmp_path / "private supervisor preparación Ω"
    public = tmp_path / "public handout"
    public.mkdir()
    assert protocol.new_private_dir(str(private))["status"] == "OPERATOR_PRIVATE_DIR_CREATED"
    coded = private / "coded session.json"
    rubric = private / "private rubric.json"
    html = public / "participant.html"
    events = _inject_public_inheritance_before_stage(monkeypatch, protocol, private)
    rc, receipt, stdout = _main(protocol, "--prepare-form", coded, html, rubric)
    assert events and events[0]["stage_acl"]["everyone_read"]
    assert rc != 0 and receipt["status"] == "OPERATOR_REJECTED"
    assert not any(path.exists() for path in (coded, html, rubric))
    assert not list(private.glob(".pfl-stage-*.tmp"))
    assert str(private) not in stdout and str(public) not in stdout


@NTFS_ONLY
def test_private_output_rejects_parent_acl_change_at_final_hardlink(
    tmp_path, monkeypatch, protocol,
):
    _, _, _, source, _, _ = _prepared_v2(tmp_path, "write-race link Ω")
    destination = source.parent / "must not publish after parent changes.json"
    original_link = os.link
    events = []

    def publish_after_acl_change(stage, target, *args, **kwargs):
        if (Path(target) == destination
                and Path(stage).name.startswith(".pfl-stage-") and not events):
            grant = subprocess.run(
                ["icacls", str(source.parent), "/grant", "*S-1-1-0:(OI)(CI)(R)"],
                capture_output=True, check=False,
            )
            assert grant.returncode == 0, grant.stderr.decode(errors="replace")
            assert _get_acl(source.parent)["everyone_read"]
            events.append(Path(stage).stat().st_ino)
        return original_link(stage, target, *args, **kwargs)

    monkeypatch.setattr(protocol.os, "link", publish_after_acl_change)
    rc, receipt, stdout = _main(
        protocol, "--record-form", source, destination,
        "OP01", "TECH_COMPLETED", "A", "UX_CLEAR",
    )
    assert len(events) == 1
    assert rc != 0 and receipt["status"] == "OPERATOR_REJECTED"
    assert not destination.exists()
    assert not list(source.parent.glob(".pfl-stage-*.tmp"))
    assert str(destination) not in stdout
