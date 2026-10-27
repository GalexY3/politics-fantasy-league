"""Operator audit tests use fictional bytes only and no network."""
import hashlib
import json
from pathlib import Path
import pytest

from politics_fantasy.secure_store import store_bytes, append_private_jsonl
from politics_fantasy.private_audit import audit_private_root

DATA=b'{"fake":"politics"}'
SHA=hashlib.sha256(DATA).hexdigest()
CAPTURE_ID="a"*32


def make_fixture(root):
    rel=store_bytes(root,DATA,SHA)
    append_private_jsonl(root,"manifest.jsonl",{"raw_object":rel,"sha256":SHA,"source_id":"congreso","capture_id":CAPTURE_ID})
    return rel


def test_audit_valid_captured_fictional_object_and_quarantine(tmp_path):
    make_fixture(tmp_path)
    append_private_jsonl(tmp_path,"quarantine_reviews.jsonl",{
        "sha256":SHA,"capture_id":CAPTURE_ID,"quarantine_state":"QUARANTINED_SCHEMA_PASSED"})
    a=audit_private_root(tmp_path)
    assert a["object_integrity"]=={"VALID_OBJECT":1}
    assert a["quarantine_states"]=={"QUARANTINED_SCHEMA_PASSED":1}
    assert a["unreviewed_captures"]==0
    assert not a["real_person_scoring"]
    assert "congreso" not in json.dumps(a)


def test_audit_detects_modified_raw_sha_without_export(tmp_path):
    rel=make_fixture(tmp_path)
    (tmp_path/rel).write_bytes(b'{"attacker":true}')
    assert audit_private_root(tmp_path)["object_integrity"]=={"BAD_RAW_SHA":1}


def test_audit_bad_path_does_not_follow_external(tmp_path):
    append_private_jsonl(tmp_path,"manifest.jsonl",{
        "raw_object":"../../private_secret","sha256":SHA})
    assert audit_private_root(tmp_path)["object_integrity"]=={"BAD_OBJECT_REFERENCE":1}


def test_audit_missing_review_is_not_approval(tmp_path):
    make_fixture(tmp_path)
    a=audit_private_root(tmp_path)
    assert a["unreviewed_captures"]==1
    assert a["release_grade"] is False


def test_audit_rejects_ledger_symlink(tmp_path):
    outside=tmp_path.parent/(tmp_path.name+"_outside")
    outside.write_bytes(b'private')
    (tmp_path/"manifest.jsonl").symlink_to(outside)
    with pytest.raises(ValueError,match="UNSAFE_LEDGER"):
        audit_private_root(tmp_path)
    assert outside.read_bytes()==b'private'


def test_audit_unknown_review_is_not_adjudication(tmp_path):
    make_fixture(tmp_path)
    append_private_jsonl(tmp_path,"quarantine_reviews.jsonl",{
        "sha256":SHA,"capture_id":CAPTURE_ID,"quarantine_state":"RELEASE_READY"})
    assert audit_private_root(tmp_path)["quarantine_states"]=={"UNKNOWN_REVIEW_STATE":1}

def test_missing_object_audit_does_not_create_shard(tmp_path):
    append_private_jsonl(tmp_path,'manifest.jsonl',{
        'raw_object': f'objects/{SHA[:2]}/{SHA}', 'sha256':SHA})
    a=audit_private_root(tmp_path)
    assert a['object_integrity']=={'MISSING_OR_UNSAFE_OBJECT':1}
    assert not (tmp_path/'objects'/SHA[:2]).exists()


def test_empty_store_audit_does_not_create_objects(tmp_path):
    a=audit_private_root(tmp_path)
    assert a['manifest_rows']==0
    assert not (tmp_path/'objects').exists()

def test_same_digest_two_captures_one_review_is_unmatched(tmp_path):
    rel=make_fixture(tmp_path)
    append_private_jsonl(tmp_path,"manifest.jsonl",{
        "raw_object":rel,"sha256":SHA,"capture_id":"b"*32})
    append_private_jsonl(tmp_path,"quarantine_reviews.jsonl",{
        "sha256":SHA,"capture_id":CAPTURE_ID,
        "quarantine_state":"QUARANTINED_SCHEMA_PASSED"})
    a=audit_private_root(tmp_path)
    assert a["manifest_rows"]==2
    assert a["unreviewed_captures"]==1


def test_unknown_review_capture_id_flagged(tmp_path):
    make_fixture(tmp_path)
    append_private_jsonl(tmp_path,"quarantine_reviews.jsonl",{
        "sha256":SHA,"capture_id":"f"*32,
        "quarantine_state":"QUARANTINED_SCHEMA_PASSED"})
    a=audit_private_root(tmp_path)
    assert a["quarantine_states"]=={"ORPHAN_REVIEW":1}
    assert a["unreviewed_captures"]==1


def test_duplicate_review_capture_id_flagged(tmp_path):
    make_fixture(tmp_path)
    for _ in range(2):
        append_private_jsonl(tmp_path,"quarantine_reviews.jsonl",{
            "sha256":SHA,"capture_id":CAPTURE_ID,
            "quarantine_state":"QUARANTINED_SCHEMA_PASSED"})
    a=audit_private_root(tmp_path)
    assert a["quarantine_states"]["DUPLICATE_REVIEW"]==1
    assert a["unreviewed_captures"]==1


def test_legacy_manifest_capture_unlinked(tmp_path):
    rel=store_bytes(tmp_path,DATA,SHA)
    append_private_jsonl(tmp_path,"manifest.jsonl",{"raw_object":rel,"sha256":SHA})
    append_private_jsonl(tmp_path,"quarantine_reviews.jsonl",{
        "sha256":SHA,"quarantine_state":"QUARANTINED_SCHEMA_PASSED"})
    a=audit_private_root(tmp_path)
    assert a["legacy_captures_unlinked"]==1
    assert a["quarantine_states"]=={"LEGACY_REVIEW_WITHOUT_ID":1}
    assert not a["release_grade"]

def test_nonexistent_root_readonly_audit_does_not_create_it(tmp_path):
    missing=tmp_path/"never_created"
    with pytest.raises(ValueError,match="MISSING_STORE_ROOT"):
        audit_private_root(missing)
    assert not missing.exists()


def test_duplicate_manifest_ids_count_both_uncertain_occurrences(tmp_path):
    rel=make_fixture(tmp_path)
    append_private_jsonl(tmp_path,"manifest.jsonl",{"capture_id":CAPTURE_ID,"sha256":SHA,"raw_object":rel})
    append_private_jsonl(tmp_path,"quarantine_reviews.jsonl",{"capture_id":CAPTURE_ID,"sha256":SHA,"quarantine_state":"QUARANTINED_SCHEMA_PASSED"})
    a=audit_private_root(tmp_path)
    assert a["duplicate_manifest_capture_ids"]==1
    assert a["unreviewed_captures"]==2
    assert a["quarantine_states"]=={"AMBIGUOUS_MANIFEST_CAPTURE_ID":1}


def test_manifest_forged_byte_length_not_accepted(tmp_path):
    rel=store_bytes(tmp_path,DATA,SHA)
    append_private_jsonl(tmp_path,"manifest.jsonl",{"raw_object":rel,"sha256":SHA,"bytes":999})
    a=audit_private_root(tmp_path)
    assert a["object_integrity"]=={"DECLARED_LENGTH_MISMATCH":1}

def test_manifest_invalid_declared_bytes_not_accepted(tmp_path):
    rel=store_bytes(tmp_path,DATA,SHA)
    append_private_jsonl(tmp_path,"manifest.jsonl",{"raw_object":rel,"sha256":SHA,"bytes":True})
    a=audit_private_root(tmp_path)
    assert a["object_integrity"]=={"INVALID_DECLARED_BYTES":1}

def test_manifest_valid_declared_bytes_verified(tmp_path):
    rel=store_bytes(tmp_path,DATA,SHA)
    append_private_jsonl(tmp_path,"manifest.jsonl",{"raw_object":rel,"sha256":SHA,"bytes":len(DATA)})
    assert audit_private_root(tmp_path)["object_integrity"]=={"VALID_OBJECT":1}


def test_missing_jsonl_terminating_newline_rejected(tmp_path):
    append_private_jsonl(tmp_path,"manifest.jsonl",{"fake":1})
    f=tmp_path/"manifest.jsonl"
    f.write_bytes(f.read_bytes().rstrip(b"\n"))
    with pytest.raises(ValueError, match="INCOMPLETE_LEDGER_RECORD"):
        audit_private_root(tmp_path)

def test_complete_jsonl_with_newline_accepted_as_legacy(tmp_path):
    append_private_jsonl(tmp_path,"manifest.jsonl",{"fake":1})
    result=audit_private_root(tmp_path)
    assert result["manifest_rows"]==1
    assert result["legacy_captures_unlinked"]==1


def test_duplicate_json_member_in_manifest_rejected(tmp_path):
    """Two fields with the same name cannot silently override capture identity."""
    (tmp_path / "manifest.jsonl").write_bytes(
        b'{"capture_id":"111","capture_id":"222","sha256":"fictional"}' + bytes([10])
    )
    with pytest.raises(ValueError, match="BAD_LEDGER_JSON"):
        audit_private_root(tmp_path)


def test_duplicate_json_member_in_review_rejected(tmp_path):
    append_private_jsonl(tmp_path, "manifest.jsonl", {"fictional": True})
    (tmp_path / "quarantine_reviews.jsonl").write_bytes(
        b'{"quarantine_state":"QUARANTINED_SCHEMA_PASSED","quarantine_state":"RELEASE_READY"}' + bytes([10])
    )
    with pytest.raises(ValueError, match="BAD_LEDGER_JSON"):
        audit_private_root(tmp_path)


def test_nonfinite_json_constants_in_private_ledger_rejected(tmp_path):
    """Python accepts NaN/Infinity by default; private JSONL must not."""
    for token in ("NaN", "Infinity", "-Infinity"):
        (tmp_path / "manifest.jsonl").write_bytes(
            ('{"bytes":' + token + '}').encode("ascii") + bytes([10])
        )
        with pytest.raises(ValueError, match="BAD_LEDGER_JSON"):
            audit_private_root(tmp_path)


def test_audit_waits_for_cooperative_writer_to_finish_private_jsonl(tmp_path, monkeypatch):
    """Shared read lock sees whole row, not a temporary partial prefix."""
    import os
    import threading
    import politics_fantasy.secure_store as store

    first_half = threading.Event()
    continue_writer = threading.Event()
    read_done = threading.Event()
    errors = []
    result = {}

    def fragmented_write(fd, payload):
        split = max(1, len(payload) // 2)
        os.write(fd, payload[:split])
        first_half.set()
        if not continue_writer.wait(timeout=5):
            raise RuntimeError("SYNTHETIC_WRITER_TIMEOUT")
        os.write(fd, payload[split:])

    monkeypatch.setattr(store, "_write_all", fragmented_write)
    def writer():
        try:
            store.append_private_jsonl(tmp_path, "manifest.jsonl",
                                       {"synthetic": True})
        except BaseException as exc:
            errors.append(str(exc))
    def reader():
        try:
            result.update(audit_private_root(tmp_path))
        except BaseException as exc:
            errors.append(str(exc))
        finally:
            read_done.set()

    wt = threading.Thread(target=writer)
    rt = threading.Thread(target=reader)
    wt.start()
    try:
        assert first_half.wait(timeout=5)
        rt.start()
        assert not read_done.wait(timeout=0.04)
    finally:
        continue_writer.set()
    wt.join(timeout=5)
    rt.join(timeout=5)
    assert not wt.is_alive() and not rt.is_alive()
    assert not errors
    assert result["manifest_rows"] == 1
    assert result["legacy_captures_unlinked"] == 1
