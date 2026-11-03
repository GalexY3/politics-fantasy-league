"""Deterministic private-input pathname race probes (synthetic Windows NTFS).

These tests create only disposable, anonymous form fixtures outside Git.  A
monkeypatch injects the swap at the precise security-check/open boundary;
the actual substituted NTFS inode and DACL are then checked independently.
No human participation, separate-user credentials, or ACL security guarantee
is inferred from a test running under the same Windows account.
"""
from __future__ import annotations

import builtins
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from test_beta_operator_instrument_versioning import _prepared_v2


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "beta_science_operator_protocol.py"
WINDOWS_ONLY = pytest.mark.skipif(os.name != "nt", reason="Real NTFS security descriptor test")


@pytest.fixture
def protocol():
    spec = importlib.util.spec_from_file_location("beta_operator_race_probe", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fixture(tmp_path: Path, stem: str):
    """One valid private form, an independent private copy and a public inode."""
    document, _, _, source, handout, rubric = _prepared_v2(tmp_path, stem)
    original = source.read_bytes()
    private_copy = source.parent / ("verified original " + stem + ".json")
    private_copy.write_bytes(original)
    assert private_copy.read_bytes() == original
    forged = json.loads(original)
    assert forged == document
    # The private source has OP01 blank; a distinct, valid synthetic OP02
    # observation makes the replacement detectable by SHA and by semantics.
    op02 = next(row for row in forged["observations"] if row["task_id"] == "OP02")
    op02.update(technical="TECH_COMPLETED", scientific="A", usability="UX_CLEAR")
    injected = (json.dumps(forged, ensure_ascii=True, sort_keys=True) + "\n").encode("utf-8")
    assert injected != original
    public_inode = handout.parent / ("Everyone readable synthetic " + stem + ".json")
    public_inode.write_bytes(injected)
    grant = subprocess.run(
        ["icacls", str(public_inode), "/grant", "*S-1-1-0:(R)"],
        capture_output=True, check=False,
    )
    assert grant.returncode == 0, grant.stderr.decode(errors="replace")
    assert public_inode.stat().st_nlink == 1
    return source, rubric, private_copy, public_inode, original, injected


def _install_acl_to_open_swap(monkeypatch, protocol, source: Path,
                              replacement: Path, original_copy: Path):
    """Inject at file-open; retain the actual pre-open DACL audit evidence.

    Intercept both pathlib and os.open so a secure descriptor-based repair
    can still undergo the test even if it no longer calls the pathname ACL
    helper. Only the designated synthetic source is intercepted.
    """
    source_identity = os.stat(source)
    assert source_identity.st_nlink == 1
    assert protocol._windows_dacl_safe(source, require_protected=False)
    assert not protocol._windows_dacl_safe(replacement, require_protected=False)
    original_audit = protocol._windows_dacl_safe
    original_path_open = Path.open
    original_os_open = os.open
    original_builtin_open = builtins.open
    audit_events = []
    events = []

    def audited(path, *, require_protected):
        verdict = original_audit(path, require_protected=require_protected)
        if Path(path) == source and not require_protected:
            audit_events.append(verdict)
        return verdict

    def swap_once():
        if events:
            return
        assert not audit_events or audit_events[-1] is True, (
            "The original source must pass any path ACL audit before opening")
        # A same-volume move preserves the substitute inode's public DACL.
        parked = source.parent / "checked inode parked for race.json"
        source.replace(parked)
        replacement.replace(source)
        current = os.stat(source)
        assert (current.st_dev, current.st_ino) != (
            source_identity.st_dev, source_identity.st_ino)
        assert source.stat().st_nlink == 1
        events.append((source_identity.st_ino, current.st_ino, tuple(audit_events)))
        assert source.read_bytes() != original_copy.read_bytes()
        assert not original_audit(source, require_protected=False), (
            "Replacement must demonstrably retain public NTFS read ACL")

    def path_open(path, *args, **kwargs):
        if path == source:
            swap_once()
        return original_path_open(path, *args, **kwargs)

    def os_fd_open(path, *args, **kwargs):
        if isinstance(path, (str, os.PathLike)) and Path(path) == source:
            swap_once()
        return original_os_open(path, *args, **kwargs)

    def builtin_open(path, *args, **kwargs):
        if isinstance(path, (str, os.PathLike)) and Path(path) == source:
            swap_once()
        return original_builtin_open(path, *args, **kwargs)

    monkeypatch.setattr(protocol, "_windows_dacl_safe", audited)
    monkeypatch.setattr(Path, "open", path_open)
    monkeypatch.setattr(os, "open", os_fd_open)
    monkeypatch.setattr(builtins, "open", builtin_open)
    return events


def _capture_main(protocol, *arguments):
    sink = io.StringIO()
    with redirect_stdout(sink):
        exit_code = protocol.main(list(map(str, arguments)))
    output = sink.getvalue()
    assert output.count("\n") == 1
    message = json.loads(output)
    assert message.get("participant_count") is None
    # Rejected CLI responses are deliberately minimal and have no R5 field.
    # Successful scientific/synthetic receipts carry the explicit R5 marker.
    if exit_code == 0:
        assert message.get("R5") == "STOP_R5"
    else:
        assert message.get("R5") in (None, "STOP_R5")
    return exit_code, message, output


@WINDOWS_ONLY
def test_prepatch_red_reader_rejects_public_inode_substituted_after_real_acl_audit(
    tmp_path, monkeypatch, protocol,
):
    source, _, saved, public, original, injected = _fixture(tmp_path, "reader Ω")
    events = _install_acl_to_open_swap(monkeypatch, protocol, source, public, saved)
    with pytest.raises(protocol.ProtocolError, match="OPERATOR_PRIVATE"):
        protocol._read_private_json_with_bytes(str(source))
    assert len(events) == 1
    assert saved.read_bytes() == original
    assert source.read_bytes() == injected


@WINDOWS_ONLY
def test_prepatch_red_record_form_does_not_publish_successor_after_source_inode_swap(
    tmp_path, monkeypatch, protocol,
):
    source, _, saved, original_public, original, injected = _fixture(
        tmp_path, "record Ω")
    destination = source.parent / "no successor from raced source.json"
    events = _install_acl_to_open_swap(
        monkeypatch, protocol, source, original_public, saved)
    code, response, stdout = _capture_main(
        protocol, "--record-form", source, destination,
        "OP01", "TECH_COMPLETED", "A", "UX_CLEAR",
    )
    assert events, "The real DACL check/open boundary was reached"
    if code == 0:
        # PREPATCH forensic evidence: the committed revision binds to the
        # substituted, publicly readable inode, not the original audited one.
        published = json.loads(destination.read_bytes())
        assert published["predecessor_sha256"] == hashlib.sha256(injected).hexdigest()
        assert response["source_sha256"] == hashlib.sha256(injected).hexdigest()
        assert response["source_sha256"] != hashlib.sha256(original).hexdigest()
    assert code != 0 and response["status"] == "OPERATOR_REJECTED"
    assert response["error_code"].startswith("OPERATOR_PRIVATE")
    assert not destination.exists()
    assert saved.read_bytes() == original and source.read_bytes() == injected
    assert str(source) not in stdout and str(destination) not in stdout
    assert "OP02" not in stdout


@WINDOWS_ONLY
def test_prepatch_red_evaluate_form_does_not_publish_scores_after_inode_swap(
    tmp_path, monkeypatch, protocol,
):
    source, rubric, saved, public, _, injected = _fixture(tmp_path, "evaluate Ω")
    destination = source.parent / "no score from raced source.json"
    events = _install_acl_to_open_swap(monkeypatch, protocol, source, public, saved)
    code, response, stdout = _capture_main(
        protocol, "--evaluate-form", source, rubric, destination)
    assert events
    if code == 0:
        # The exported digest independently confirms which bytes were scored.
        graded = json.loads(destination.read_bytes())
        assert graded["coded_input_sha256"] == hashlib.sha256(injected).hexdigest()
        assert response["sha256"] == hashlib.sha256(destination.read_bytes()).hexdigest()
    assert code != 0 and response["status"] == "OPERATOR_REJECTED"
    assert response["error_code"].startswith("OPERATOR_PRIVATE")
    assert not destination.exists()
    assert source.read_bytes() == injected
    assert str(source) not in stdout and str(destination) not in stdout
    assert "correct_answer_code" not in stdout


@WINDOWS_ONLY
def test_private_reader_control_preserves_exact_original_bytes_without_swap(
    tmp_path, protocol,
):
    source, _, saved, _, original, _ = _fixture(tmp_path, "control Ω")
    parsed, read_bytes = protocol._read_private_json_with_bytes(str(source))
    assert read_bytes == original == saved.read_bytes()
    assert hashlib.sha256(read_bytes).digest() == hashlib.sha256(original).digest()
    assert parsed["schema"] == protocol.FORM_INPUT_SCHEMA


@WINDOWS_ONLY
def test_windows_dacl_audit_distinguishes_private_and_public_open_handles(
    tmp_path, protocol,
):
    source, _, _, public, original, injected = _fixture(
        tmp_path, "handle security Ω")
    fd = os.open(source, os.O_RDONLY | getattr(os, "O_BINARY", 0))
    public_fd = os.open(public, os.O_RDONLY | getattr(os, "O_BINARY", 0))
    try:
        assert protocol._windows_dacl_safe_fd(fd, require_protected=False)
        assert not protocol._windows_dacl_safe_fd(
            public_fd, require_protected=False)
        assert os.fstat(fd).st_ino != os.fstat(public_fd).st_ino
        with os.fdopen(fd, "rb") as stream:
            fd = None
            assert stream.read() == original != injected
    finally:
        if fd is not None:
            os.close(fd)
        os.close(public_fd)


@WINDOWS_ONLY
def test_private_reader_rejects_existing_public_hardlink_without_reading_payload(
    tmp_path, protocol,
):
    source, _, _, public, _, injected = _fixture(tmp_path, "hardlink Ω")
    alias = source.parent / "hardlink already under private path.json"
    os.link(public, alias)
    assert os.path.samefile(public, alias)
    assert alias.stat().st_nlink == 2
    assert not protocol._windows_dacl_safe(alias, require_protected=False)
    with pytest.raises(protocol.ProtocolError, match="OPERATOR_PRIVATE_FILE_ALIAS_FORBIDDEN"):
        protocol._read_private_json_with_bytes(str(alias))
    assert public.read_bytes() == alias.read_bytes() == injected


@WINDOWS_ONLY
def test_private_reader_rejects_existing_file_symlink_or_records_windows_privilege_limit(
    tmp_path, protocol,
):
    source, _, _, public, _, injected = _fixture(tmp_path, "symlink Ω")
    alias = source.parent / "file symlink already under private path.json"
    try:
        alias.symlink_to(public)
    except OSError as exc:
        if getattr(exc, "winerror", None) == 1314:
            # This token cannot create the alias: verified prerequisite
            # limitation, not evidence that symlink rejection ran.
            assert not os.path.lexists(alias)
            return
        raise
    assert alias.is_symlink() and alias.read_bytes() == injected
    with pytest.raises(protocol.ProtocolError, match="OPERATOR_PRIVATE_FILE_ALIAS_FORBIDDEN"):
        protocol._read_private_json_with_bytes(str(alias))
    assert source.is_file() and public.is_file()
