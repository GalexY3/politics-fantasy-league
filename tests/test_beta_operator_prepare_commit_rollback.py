"""Synthetic NTFS regression for post-publication prepare-form rollback.

The real writer succeeds with three immutable new files.  A deterministic
one-shot OSError is injected *only* into the final participant HTML's
Path.stat() after the writer returns, before prepare_form records ownership.
No real participant observations, extra Windows identities or Git writes.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from test_beta_operator_private_write_race import _main, protocol


ROOT = Path(__file__).resolve().parents[1]
WINDOWS_ONLY = pytest.mark.skipif(
    os.name != "nt", reason="Windows NTFS private-output rollback experiment")


def _destinations(tmp_path: Path, protocol, stem: str):
    private = tmp_path / ("privado datos Ω " + stem)
    public = tmp_path / ("público hoja Ω " + stem)
    os.mkdir(private, mode=0o700)
    public.mkdir()
    assert protocol._private_directory_status(private) == "WINDOWS_RESTRICTED_DACL_CHECKED"
    rubric = private / ("clave supervisor Ω " + stem + ".json")
    coded = private / ("observaciones sintéticas Ω " + stem + ".json")
    handout = public / ("hoja participante Ω " + stem + ".html")
    assert not any(path.exists() or path.is_relative_to(ROOT)
                   for path in (coded, handout, rubric))
    # Independent preexisting files must survive both success and rollback.
    private_existing = private / "PREEXISTING_PRIVATE_NO_OVERWRITE.txt"
    public_existing = public / "PREEXISTING_PUBLIC_NO_OVERWRITE.txt"
    private_existing.write_bytes(b"PRIVATE SENTINEL OMEGA\n")
    public_existing.write_bytes(b"PUBLIC SENTINEL OMEGA\n")
    return coded, handout, rubric, private_existing, public_existing


@WINDOWS_ONLY
def test_prepatch_red_prepare_form_rolls_back_html_when_final_postwrite_stat_fails(
    tmp_path, monkeypatch, protocol,
):
    coded, handout, rubric, existing_private, existing_public = _destinations(
        tmp_path, protocol, "postwrite stat")
    original_private = existing_private.read_bytes()
    original_public = existing_public.read_bytes()
    real_write = protocol._write_external_utf8
    real_stat = Path.stat
    events = {"armed": False, "injected": 0, "commit": None}

    def write_then_arm(path, content, **kwargs):
        # Invoke the actual NTFS writer, including fsync/link, without mocking
        # disk operations, identity or DACL verification.
        result = real_write(path, content, **kwargs)
        if Path(path) == handout:
            assert not events["armed"]
            assert all(os.path.isfile(path) for path in (rubric, coded, handout))
            original_bytes = handout.read_bytes()
            assert result == (
                len(original_bytes), hashlib.sha256(original_bytes).hexdigest())
            assert "correct_answer_code" not in original_bytes.decode("utf-8")
            events["commit"] = (
                result, (os.stat(handout).st_dev, os.stat(handout).st_ino),
                original_bytes)
            events["armed"] = True
        return result

    def fail_exactly_one_html_postcommit_stat(path, *args, **kwargs):
        if events["armed"] and Path(path) == handout and not events["injected"]:
            events["injected"] += 1
            raise PermissionError(13, "INJECTED_POSTWRITE_STAT_ONCE", str(path))
        return real_stat(path, *args, **kwargs)

    monkeypatch.setattr(protocol, "_write_external_utf8", write_then_arm)
    monkeypatch.setattr(Path, "stat", fail_exactly_one_html_postcommit_stat)
    code, receipt, stdout = _main(
        protocol, "--prepare-form", coded, handout, rubric)
    assert events["armed"] and events["injected"] == 1
    assert events["commit"] is not None, "The real HTML writer must finish first"
    assert code != 0 and receipt["status"] == "OPERATOR_REJECTED"
    assert receipt["error_code"] == "OPERATOR_FORM_WRITE_FAILED"
    assert stdout.count("\n") == 1
    assert all(str(path) not in stdout and path.name not in stdout for path in
               (coded, handout, rubric, existing_private, existing_public))
    assert "correct_answer_code" not in stdout
    assert existing_private.read_bytes() == original_private
    assert existing_public.read_bytes() == original_public
    # PREPATCH forensics: the earlier rubric and coded JSON were removed, but
    # the final HTML still exists because created.append was never reached.
    if handout.exists():
        assert handout.read_bytes() == events["commit"][2]
        assert (handout.stat().st_dev, handout.stat().st_ino) == events["commit"][1]
        assert not rubric.exists() and not coded.exists()
    # Required all-or-nothing rollback of the three synthetic form artifacts.
    assert not any(path.exists() for path in (coded, handout, rubric)), (
        "Final public HTML was published but omitted from rollback ownership")
    assert not list(coded.parent.glob(".pfl-stage-*.tmp"))
    assert not list(handout.parent.glob(".pfl-stage-*.tmp"))


@WINDOWS_ONLY
def test_contract_prepare_form_preserves_third_party_html_on_postwrite_name_swap(
    tmp_path, monkeypatch, protocol,
):
    """Forward-looking contract, not a claim of historical PREPATCH RED.

    Interpose AFTER the real third writer succeeds and records its original
    inode, but BEFORE the caller compares that inode with the destination.
    No stage bytes/identity are forged; the third-party file is preexisting.
    """
    coded, handout, rubric, existing_private, existing_public = _destinations(
        tmp_path, protocol, "publication identity contract")
    originals = (existing_private.read_bytes(), existing_public.read_bytes())
    foreign = handout.parent / "INDEPENDENT_PREEXISTING_THIRD_PARTY_Ω.html"
    foreign_bytes = b"<html>UNRELATED SYNTHETIC THIRD PARTY</html>\n"
    foreign.write_bytes(foreign_bytes)
    foreign_stat = foreign.stat()
    foreign_identity = (foreign_stat.st_dev, foreign_stat.st_ino)
    parked_own_html = tmp_path / "test-only parked generated participant sheet.html"
    original_write = protocol._write_external_utf8
    events = []

    def write_then_replace_name(path, content, **kwargs):
        result = original_write(path, content, **kwargs)
        if Path(path) == handout:
            assert not events and not parked_own_html.exists()
            published = kwargs["published_files"]
            assert len(published) == 3
            assert published[-1][0] == handout
            own_stat = handout.stat()
            own_identity = (own_stat.st_dev, own_stat.st_ino)
            assert published[-1][1:] == own_identity
            own_bytes = handout.read_bytes()
            assert result == (len(own_bytes), hashlib.sha256(own_bytes).hexdigest())
            handout.replace(parked_own_html)
            foreign.replace(handout)
            new_stat = handout.stat()
            assert (new_stat.st_dev, new_stat.st_ino) == foreign_identity
            assert foreign_identity != own_identity
            assert handout.read_bytes() == foreign_bytes
            events.append((own_identity, foreign_identity, own_bytes))
        return result

    monkeypatch.setattr(protocol, "_write_external_utf8", write_then_replace_name)
    try:
        code, receipt, stdout = _main(
            protocol, "--prepare-form", coded, handout, rubric)
        assert len(events) == 1, "The real final HTML write must have completed"
        assert code != 0 and receipt["status"] == "OPERATOR_REJECTED"
        assert receipt["error_code"] == "OPERATOR_FORM_PUBLICATION_IDENTITY_CHANGED"
        assert not coded.exists() and not rubric.exists(), (
            "Previously published private artifacts must roll back")
        assert handout.exists(), "Rollback must not delete the third-party replacement"
        observed = handout.stat()
        assert (observed.st_dev, observed.st_ino) == foreign_identity
        assert handout.read_bytes() == foreign_bytes
        assert parked_own_html.read_bytes() == events[0][2]
        assert existing_private.read_bytes() == originals[0]
        assert existing_public.read_bytes() == originals[1]
        assert not list(coded.parent.glob(".pfl-stage-*.tmp"))
        assert not list(handout.parent.glob(".pfl-stage-*.tmp"))
        assert stdout.count("\n") == 1
        assert all(str(p) not in stdout and p.name not in stdout for p in
                   (coded, handout, rubric, foreign, parked_own_html))
        assert "correct_answer_code" not in stdout
    finally:
        # The race harness moved the successfully generated (but now
        # deliberately untracked) HTML to a test-only parking name.
        if parked_own_html.exists():
            parked_own_html.unlink()


@WINDOWS_ONLY
def test_prepare_form_rolls_back_first_private_rubric_after_postwrite_stat_error(
    tmp_path, monkeypatch, protocol,
):
    """The FIRST successful publication must enter rollback ownership too."""
    coded, handout, rubric, existing_private, existing_public = _destinations(
        tmp_path, protocol, "first rubric postwrite")
    originals = (existing_private.read_bytes(), existing_public.read_bytes())
    original_write = protocol._write_external_utf8
    original_stat = Path.stat
    events = {"armed": False, "injected": 0, "published": None, "count": 0}

    def write_then_arm_first(path, content, **kwargs):
        events["count"] += 1
        result = original_write(path, content, **kwargs)
        if Path(path) == rubric:
            assert events["count"] == 1 and not events["armed"]
            assert len(kwargs["published_files"]) == 1
            assert kwargs["published_files"][0][0] == rubric
            assert rubric.is_file()
            raw = rubric.read_bytes()
            assert result == (len(raw), hashlib.sha256(raw).hexdigest())
            events["published"] = (rubric.stat().st_dev, rubric.stat().st_ino)
            events["armed"] = True
        return result

    def raise_once_after_first_commit(path, *args, **kwargs):
        if events["armed"] and Path(path) == rubric and not events["injected"]:
            events["injected"] += 1
            raise PermissionError(13, "SYNTHETIC_FIRST_POSTWRITE_STAT", str(path))
        return original_stat(path, *args, **kwargs)

    monkeypatch.setattr(protocol, "_write_external_utf8", write_then_arm_first)
    monkeypatch.setattr(Path, "stat", raise_once_after_first_commit)
    code, receipt, stdout = _main(
        protocol, "--prepare-form", coded, handout, rubric)
    assert events["armed"] and events["injected"] == 1 and events["count"] == 1
    assert events["published"] is not None
    assert code != 0 and receipt["status"] == "OPERATOR_REJECTED"
    assert receipt["error_code"] == "OPERATOR_FORM_WRITE_FAILED"
    assert not rubric.exists() and not coded.exists() and not handout.exists()
    assert existing_private.read_bytes() == originals[0]
    assert existing_public.read_bytes() == originals[1]
    assert not list(coded.parent.glob(".pfl-stage-*.tmp"))
    assert not list(handout.parent.glob(".pfl-stage-*.tmp"))
    assert stdout.count("\n") == 1
    assert all(str(p) not in stdout and p.name not in stdout for p in
               (coded, handout, rubric))
    assert "correct_answer_code" not in stdout


@WINDOWS_ONLY
def test_prepare_form_normal_three_artifact_commit_preserves_existing_files(
    tmp_path, protocol,
):
    coded, handout, rubric, existing_private, existing_public = _destinations(
        tmp_path, protocol, "normal commit")
    original_private = existing_private.read_bytes()
    original_public = existing_public.read_bytes()
    code, receipt, stdout = _main(
        protocol, "--prepare-form", coded, handout, rubric)
    assert code == 0 and receipt["status"] == "OPERATOR_FORM_PREPARED"
    assert receipt["participants_observed"] is False
    assert receipt["participant_count"] is None
    assert all(path.is_file() and path.stat().st_nlink == 1
               for path in (coded, handout, rubric))
    assert protocol._windows_dacl_safe(coded, require_protected=False)
    assert protocol._windows_dacl_safe(rubric, require_protected=False)
    assert "correct_answer_code" not in handout.read_text(encoding="utf-8")
    assert hashlib.sha256(handout.read_bytes()).hexdigest() == receipt["handout_sha256"]
    assert existing_private.read_bytes() == original_private
    assert existing_public.read_bytes() == original_public
    assert not list(coded.parent.glob(".pfl-stage-*.tmp"))
    assert not list(handout.parent.glob(".pfl-stage-*.tmp"))
    assert all(str(path) not in stdout for path in (coded, handout, rubric))
