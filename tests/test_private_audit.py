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
