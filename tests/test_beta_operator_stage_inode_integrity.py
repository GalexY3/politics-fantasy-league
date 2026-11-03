"""Independent private-output stage substitution: only synthetic NTFS/POSIX temp files.

The stage pathname may be changed between its fsynced handle being closed and
the create-only hardlink. ACL safety alone does not bind the published bytes to
the SHA returned by the operator. The deterministic hook uses the REAL link and
different real inodes; this is not a second-user penetration test.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from test_beta_operator_instrument_versioning import _prepared_v2
from test_beta_operator_private_write_race import _main, protocol


def test_prepatch_red_record_form_rejects_replaced_stage_inode_before_hardlink(
    tmp_path, monkeypatch, protocol,
):
    _, _, _, source, _, _ = _prepared_v2(tmp_path, "staging identity Ω")
    original_source = source.read_bytes()
    destination = source.parent / "successor original SHA vs published bytes.json"
    real_link = os.link
    events = []
    forgery = b'{"schema":"synthetic_stage_replacement","content":"NOT_AUTHENTIC"}\n'

    def swap_stage_then_link(stage, published, *args, **kwargs):
        if Path(published) == destination and not events:
            stage = Path(stage)
            original = stage.read_bytes()
            original_inode = stage.stat()
            parked = stage.parent / "parked original stage synthetic Ω.tmp"
            stage.replace(parked)
            stage.write_bytes(forgery)
            replacement_inode = stage.stat()
            assert (original_inode.st_dev, original_inode.st_ino) != (
                replacement_inode.st_dev, replacement_inode.st_ino)
            events.append((original, original_inode, replacement_inode, parked))
        return real_link(stage, published, *args, **kwargs)

    monkeypatch.setattr(protocol.os, "link", swap_stage_then_link)
    code, response, stdout = _main(
        protocol, "--record-form", source, destination,
        "OP01", "TECH_COMPLETED", "A", "UX_CLEAR",
    )
    assert len(events) == 1, "The real stage publication must be intercepted"
    expected_bytes, old_inode, injected_inode, _ = events[0]
    assert expected_bytes != forgery
    assert hashlib.sha256(expected_bytes).hexdigest() != hashlib.sha256(forgery).hexdigest()
    if code == 0:
        # Forensic PREPATCH evidence: the user receives a success receipt for
        # bytes that are NOT the actual content of the published inode.
        assert destination.read_bytes() == forgery
        assert destination.stat().st_ino == injected_inode.st_ino
        assert response["destination_sha256"] == hashlib.sha256(expected_bytes).hexdigest()
        assert response["destination_sha256"] != hashlib.sha256(
            destination.read_bytes()).hexdigest()
    assert code != 0, "The publisher must not acknowledge substituted bytes/inode"
    assert response["status"] == "OPERATOR_REJECTED"
    assert not destination.exists()
    assert source.read_bytes() == original_source
    assert str(source) not in stdout and str(destination) not in stdout


def test_normal_private_record_successor_digest_matches_persisted_bytes(
    tmp_path, protocol,
):
    _, _, _, source, _, _ = _prepared_v2(tmp_path, "staging identity control á")
    destination = source.parent / "normal successor.json"
    code, response, _ = _main(
        protocol, "--record-form", source, destination,
        "OP01", "TECH_COMPLETED", "A", "UX_CLEAR",
    )
    assert code == 0 and response["status"] == "OPERATOR_FORM_OBSERVATION_RECORDED"
    assert destination.is_file() and destination.stat().st_nlink == 1
    assert response["destination_sha256"] == hashlib.sha256(
        destination.read_bytes()).hexdigest()
    assert json.loads(destination.read_bytes())["predecessor_sha256"] == hashlib.sha256(
        source.read_bytes()).hexdigest()


def test_prepatch_red_evaluate_form_rejects_inplace_stage_byte_tampering(
    tmp_path, monkeypatch, protocol,
):
    _, _, _, source, _, rubric_path = _prepared_v2(tmp_path, "staging mutable bytes á")
    coded = source.parent / "coded original.json"
    code, _, _ = _main(
        protocol, "--record-form", source, coded,
        "OP01", "TECH_COMPLETED", "A", "UX_CLEAR",
    )
    assert code == 0
    destination = source.parent / "score with tampered stage content.json"
    original_link = os.link
    events = []
    forged = b'{"schema":"synthetic_mutation_in_same_inode"}\n'

    def modify_stage_then_link(stage, published, *args, **kwargs):
        if Path(published) == destination and not events:
            stage = Path(stage)
            original_data = stage.read_bytes()
            identity = stage.stat()
            stage.write_bytes(forged)
            assert identity.st_ino == stage.stat().st_ino
            events.append((original_data, identity.st_ino))
        return original_link(stage, published, *args, **kwargs)

    monkeypatch.setattr(protocol.os, "link", modify_stage_then_link)
    code, response, stdout = _main(
        protocol, "--evaluate-form", coded, rubric_path, destination)
    assert len(events) == 1
    expected_bytes, original_inode = events[0]
    assert expected_bytes != forged
    if code == 0:
        assert destination.read_bytes() == forged
        assert destination.stat().st_ino == original_inode
        assert response["sha256"] == hashlib.sha256(expected_bytes).hexdigest()
        assert response["sha256"] != hashlib.sha256(destination.read_bytes()).hexdigest()
    assert code != 0, "The evaluator must not receipt a modified same-inode stage"
    assert response["status"] == "OPERATOR_REJECTED"
    assert not destination.exists()
    assert coded.is_file() and source.is_file()
    assert str(destination) not in stdout
