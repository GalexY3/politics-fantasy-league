"""NTFS provenance race: re-resolved parent != the parent of audited input.

All payloads are synthetic, generated from a real local v2 form.  A junction
swap happens AFTER the actual private file handles have been audited/read,
but BEFORE CLI code re-resolves the source pathname to enforce same-parent
provenance.  This does not claim access by a second OS identity.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess

import pytest

from test_beta_operator_instrument_versioning import _prepared_v2
from test_beta_operator_private_write_race import _main, protocol


NTFS_ONLY = pytest.mark.skipif(os.name != "nt", reason="Windows NTFS junctions")


def _distinct_private_inputs(tmp_path: Path, protocol, name: str):
    """Two real secure parents and form-bound, DIFFERENT coded bytes."""
    _, rubric, _, blank, _, rubric_path = _prepared_v2(tmp_path, name)
    rubric_parent = rubric_path.parent
    source_parent = tmp_path / ("independent private source Ω " + name)
    os.mkdir(source_parent, mode=0o700)
    source = source_parent / ("synthetic coded Ω " + name + ".json")
    same_name_in_rubric_dir = rubric_parent / source.name
    blank_raw = blank.read_bytes()
    session = json.loads(blank_raw)
    row = next(item for item in session["observations"]
               if item["task_id"] == "OP01")
    row.update(
        technical="TECH_COMPLETED",
        scientific=next(item["correct_answer_code"] for item in rubric["tasks"]
                        if item["task_id"] == "OP01"),
        usability="UX_CLEAR",
    )
    coded_raw = (json.dumps(session, ensure_ascii=True, sort_keys=True,
                            separators=(",", ":")) + "\n").encode("ascii")
    assert coded_raw != blank_raw
    source.write_bytes(coded_raw)
    same_name_in_rubric_dir.write_bytes(blank_raw)
    assert (source.stat().st_dev, source.stat().st_ino) != (
        same_name_in_rubric_dir.stat().st_dev,
        same_name_in_rubric_dir.stat().st_ino)
    assert protocol._private_directory_status(source_parent) == (
        "WINDOWS_RESTRICTED_DACL_CHECKED")
    assert protocol._private_directory_status(rubric_parent) == (
        "WINDOWS_RESTRICTED_DACL_CHECKED")
    for item in (source, rubric_path, same_name_in_rubric_dir):
        assert protocol._windows_dacl_safe(item, require_protected=False)
    return source, rubric_path, same_name_in_rubric_dir, coded_raw, blank_raw


@NTFS_ONLY
def test_prepatch_red_evaluate_refuses_cross_private_parent_alias_rebinding(
    tmp_path, monkeypatch, protocol,
):
    source, rubric, shadow, coded_raw, shadow_raw = _distinct_private_inputs(
        tmp_path, protocol, "evaluate provenance")
    destination = rubric.parent / "no cross-parent score Ω.json"
    initial_source_identity = (source.stat().st_dev, source.stat().st_ino)
    parked = tmp_path / "original independent source dir parked Ω"
    real_reader = protocol._read_private_json_with_bytes
    reads = []
    swaps = []

    def read_then_swap(path):
        value = real_reader(path)
        reads.append(Path(path))
        if Path(path) == rubric and not swaps:
            assert reads == [source, rubric], "Both original fd audits completed"
            assert protocol._private_directory_status(source.parent) == (
                "WINDOWS_RESTRICTED_DACL_CHECKED")
            source.parent.rename(parked)
            result = subprocess.run(
                ["cmd.exe", "/c", "mklink", "/J", str(source.parent),
                 str(rubric.parent)],
                capture_output=True, check=False,
            )
            assert result.returncode == 0, result.stderr.decode(errors="replace")
            assert source.parent.is_junction()
            assert source.resolve(strict=True) == shadow.resolve(strict=True)
            swaps.append("after_real_source_and_rubric_fd_reads")
        return value

    monkeypatch.setattr(protocol, "_read_private_json_with_bytes", read_then_swap)
    try:
        code, report, stdout = _main(
            protocol, "--evaluate-form", source, rubric, destination)
        assert swaps == ["after_real_source_and_rubric_fd_reads"]
        if code == 0:
            # GENUINE PREPATCH FORENSICS: a score created under the rubric's
            # parent is actually about the *different* original source.
            assert destination.is_file()
            exported = json.loads(destination.read_bytes())
            assert exported["coded_input_sha256"] == hashlib.sha256(
                coded_raw).hexdigest()
            assert exported["coded_input_sha256"] != hashlib.sha256(
                shadow_raw).hexdigest()
            assert report["sha256"] == hashlib.sha256(
                destination.read_bytes()).hexdigest()
        assert code != 0, (
            "After auditing P1 source and P2 rubric, a junction must not "
            "launder P1's content as an evaluation under P2")
        assert report["status"] == "OPERATOR_REJECTED"
        assert not destination.exists()
        assert all(str(path) not in stdout and path.name not in stdout
                   for path in (source, rubric, destination))
        assert "correct_answer_code" not in stdout
    finally:
        if source.parent.is_junction():
            source.parent.rmdir()
        if parked.exists():
            parked.rename(source.parent)
    assert (source.stat().st_dev, source.stat().st_ino) == initial_source_identity
    assert source.read_bytes() == coded_raw and shadow.read_bytes() == shadow_raw
    assert not list(source.parent.glob(".pfl-stage-*.tmp"))
    assert not list(rubric.parent.glob(".pfl-stage-*.tmp"))


@NTFS_ONLY
def test_prepatch_red_record_form_refuses_source_parent_alias_rebinding(
    tmp_path, monkeypatch, protocol,
):
    """The private source's audited parent must bind the successor's parent."""
    source, rubric, shadow, coded_raw, shadow_raw = _distinct_private_inputs(
        tmp_path, protocol, "record provenance")
    destination = rubric.parent / "no foreign-parent successor Ω.json"
    old_id = (source.stat().st_dev, source.stat().st_ino)
    parked = tmp_path / "parked source for record Ω"
    baseline_rc, baseline, _ = _main(
        protocol, "--record-form", source, destination,
        "OP02", "TECH_COMPLETED", "A", "UX_CLEAR")
    assert baseline_rc != 0
    assert baseline["error_code"] == "OPERATOR_PRIVATE_OUTPUT_PARENT_MISMATCH"
    assert not destination.exists()

    real_reader = protocol._read_private_json_with_bytes
    reads = []
    events = []

    def source_read_then_junction(path):
        value = real_reader(path)
        reads.append(Path(path))
        if Path(path) == source and not events:
            assert reads == [source], "The original source fd was verified/read"
            assert protocol._private_directory_status(source.parent) == (
                "WINDOWS_RESTRICTED_DACL_CHECKED")
            source.parent.rename(parked)
            result = subprocess.run(
                ["cmd.exe", "/c", "mklink", "/J",
                 str(source.parent), str(rubric.parent)],
                capture_output=True, check=False)
            assert result.returncode == 0, result.stderr.decode(errors="replace")
            assert source.parent.is_junction()
            assert source.resolve(strict=True) == shadow.resolve(strict=True)
            events.append("after_real_coded_fd_read_before_parent_comparison")
        return value

    monkeypatch.setattr(
        protocol, "_read_private_json_with_bytes", source_read_then_junction)
    try:
        rc, response, stdout = _main(
            protocol, "--record-form", source, destination,
            "OP02", "TECH_COMPLETED", "A", "UX_CLEAR")
        assert events == ["after_real_coded_fd_read_before_parent_comparison"]
        if rc == 0:
            assert destination.is_file()
            revised = json.loads(destination.read_bytes())
            assert revised["predecessor_sha256"] == hashlib.sha256(
                coded_raw).hexdigest()
            assert revised["predecessor_sha256"] != hashlib.sha256(
                shadow_raw).hexdigest()
            assert response["source_sha256"] == hashlib.sha256(
                coded_raw).hexdigest()
            assert response["destination_sha256"] == hashlib.sha256(
                destination.read_bytes()).hexdigest()
        assert rc != 0, (
            "A source read under private P1 must not produce a P2 successor "
            "only because its parent pathname became a junction after the read")
        assert response["status"] == "OPERATOR_REJECTED"
        assert not destination.exists()
        assert all(str(path) not in stdout and path.name not in stdout
                   for path in (source, rubric, destination))
    finally:
        if source.parent.is_junction():
            source.parent.rmdir()
        if parked.exists():
            parked.rename(source.parent)
    assert (source.stat().st_dev, source.stat().st_ino) == old_id
    assert source.read_bytes() == coded_raw and shadow.read_bytes() == shadow_raw
    assert not list(source.parent.glob(".pfl-stage-*.tmp"))
    assert not list(rubric.parent.glob(".pfl-stage-*.tmp"))


@NTFS_ONLY
def test_prepatch_red_verify_chain_refuses_parent_alias_changed_between_check_and_read(
    tmp_path, monkeypatch, protocol,
):
    """Verify-chain validates path parents BEFORE reads, so race that boundary.

    The originally proposed after-read swap cannot precede a later
    same-parent check in verify_chain_to: its parent loop runs first.
    Instead this falsifier temporarily aliases the *checked* names to P2,
    restores the distinct P1 directory BEFORE any source/revision fd reads,
    and observes whether P1 bytes are verified/exported as though from P2.
    """
    _, _, _, p2_root, _, rubric = _prepared_v2(
        tmp_path, "verify-chain provenance Ω")
    p2_dir = p2_root.parent
    p2_rev = p2_dir / "synthetic revision Ω.json"
    p2_result = p2_dir / "synthetic scored Ω.json"
    rc, response, _ = _main(
        protocol, "--record-form", p2_root, p2_rev,
        "OP01", "TECH_COMPLETED", "A", "UX_CLEAR")
    assert rc == 0 and response["status"] == "OPERATOR_FORM_OBSERVATION_RECORDED"
    rc, response, _ = _main(
        protocol, "--evaluate-form", p2_rev, rubric, p2_result)
    assert rc == 0 and response["status"] == "OPERATOR_FORM_EVALUATION_EXPORTED"
    original_root = p2_root.read_bytes()
    original_revision = p2_rev.read_bytes()
    original_score = p2_result.read_bytes()
    assert protocol._windows_dacl_safe(p2_result, require_protected=False)

    p1_dir = tmp_path / "another restricted chain directory Ω"
    os.mkdir(p1_dir, mode=0o700)
    p1_root = p1_dir / p2_root.name
    p1_rev = p1_dir / p2_rev.name
    p1_root.write_bytes(original_root)
    p1_rev.write_bytes(original_revision)
    assert protocol._private_directory_status(p1_dir) == (
        "WINDOWS_RESTRICTED_DACL_CHECKED")
    # Distinct real inodes and exact code/score validity; P2's homonymous
    # source files remain real and parseable but carry DIFFERENT bytes.
    assert p1_root.stat().st_ino != p2_root.stat().st_ino
    assert p1_rev.stat().st_ino != p2_rev.stat().st_ino
    p2_root.write_bytes(original_root + b"\n")
    p2_rev.write_bytes(original_revision + b"\n")
    assert p1_root.read_bytes() != p2_root.read_bytes()
    assert p1_rev.read_bytes() != p2_rev.read_bytes()
    assert p2_result.read_bytes() == original_score
    assert all(protocol._windows_dacl_safe(item, require_protected=False)
               for item in (p1_root, p1_rev, rubric, p2_result))
    output = p2_dir / "chain must not mix private parents Ω.json"
    baseline_code, baseline, _ = _main(
        protocol, "--verify-chain-to", output, rubric, p2_result, p1_root, p1_rev)
    assert baseline_code != 0
    assert baseline["error_code"] == "OPERATOR_PRIVATE_OUTPUT_PARENT_MISMATCH"
    assert not output.exists()

    parked = tmp_path / "parked original P1 chain Ω"
    real_resolve = Path.resolve
    real_private_dir = protocol._private_directory_status
    events = []
    state = {"swapped": False, "restored": False, "parent_reads": []}

    def rename_then_resolve(path, *args, **kwargs):
        if Path(path) in (p1_root, p1_rev) and not state["restored"]:
            if not state["swapped"]:
                p1_dir.rename(parked)
                junction = subprocess.run(
                    ["cmd.exe", "/c", "mklink", "/J", str(p1_dir), str(p2_dir)],
                    capture_output=True, check=False)
                assert junction.returncode == 0, junction.stderr.decode(
                    errors="replace")
                assert p1_dir.is_junction()
                state["swapped"] = True
                events.append("P1_alias_to_P2_before_parent_identity_check")
            state["parent_reads"].append(Path(path).name)
        return real_resolve(path, *args, **kwargs)

    def restore_before_any_chain_private_reads(path):
        result = real_private_dir(path)
        if Path(path) == p2_dir and state["swapped"] and not state["restored"]:
            assert state["parent_reads"] == [p1_root.name, p1_rev.name]
            assert p1_dir.is_junction()
            p1_dir.rmdir()
            parked.rename(p1_dir)
            state["restored"] = True
            events.append("P1_restored_before_private_file_fd_reads")
        return result

    monkeypatch.setattr(Path, "resolve", rename_then_resolve)
    monkeypatch.setattr(
        protocol, "_private_directory_status", restore_before_any_chain_private_reads)
    try:
        rc, receipt, stdout = _main(
            protocol, "--verify-chain-to", output, rubric, p2_result,
            p1_root, p1_rev)
        assert events == [
            "P1_alias_to_P2_before_parent_identity_check",
            "P1_restored_before_private_file_fd_reads",
        ]
        assert state["restored"] and not p1_dir.is_junction()
        if rc == 0:
            report = json.loads(output.read_bytes())
            assert report["status"] == "OPERATOR_FORM_CHAIN_VERIFIED"
            assert report["links_verified"] == 1
            assert report["root_sha256"] == hashlib.sha256(original_root).hexdigest()
            assert report["final_sha256"] == hashlib.sha256(
                original_revision).hexdigest()
            assert report["root_sha256"] != hashlib.sha256(
                p2_root.read_bytes()).hexdigest()
            assert report["final_sha256"] != hashlib.sha256(
                p2_rev.read_bytes()).hexdigest()
            assert report["result_sha256"] == hashlib.sha256(
                original_score).hexdigest()
            assert receipt["sha256"] == hashlib.sha256(output.read_bytes()).hexdigest()
        assert rc != 0, (
            "Private chain inputs actually read from P1 must not be accepted "
            "under P2 merely because an earlier name resolution saw a junction")
        assert receipt["status"] == "OPERATOR_REJECTED"
        assert not output.exists()
        assert all(str(path) not in stdout for path in
                   (p1_root, p1_rev, rubric, p2_result, output))
    finally:
        if p1_dir.is_junction():
            p1_dir.rmdir()
        if parked.exists():
            parked.rename(p1_dir)
    assert p1_root.read_bytes() == original_root
    assert p1_rev.read_bytes() == original_revision
    assert p2_result.read_bytes() == original_score
    assert not list(p1_dir.glob(".pfl-stage-*.tmp"))
    assert not list(p2_dir.glob(".pfl-stage-*.tmp"))


@NTFS_ONLY
def test_different_private_parents_without_alias_swap_reject_mixing(
    tmp_path, protocol,
):
    source, rubric, shadow, coded_raw, shadow_raw = _distinct_private_inputs(
        tmp_path, protocol, "baseline mismatch")
    destination = rubric.parent / "baseline refuses mixed source Ω.json"
    rc, report, stdout = _main(
        protocol, "--evaluate-form", source, rubric, destination)
    assert rc != 0 and report["status"] == "OPERATOR_REJECTED"
    assert report["error_code"] == "OPERATOR_PRIVATE_OUTPUT_PARENT_MISMATCH"
    assert not destination.exists()
    assert source.read_bytes() == coded_raw and shadow.read_bytes() == shadow_raw
    assert all(str(path) not in stdout for path in (source, rubric, destination))
