"""Offline CLI smoke: no sensitive source data leaves JSON aggregate output."""
import json
import os
from pathlib import Path
import subprocess
import sys
import hashlib
from politics_fantasy.secure_store import store_bytes, append_private_jsonl

DATA=b'{"fake":"yes"}'
SHA=hashlib.sha256(DATA).hexdigest()
CID='1'*32


def run_cli(root):
    env=os.environ.copy()
    src=Path(__file__).resolve().parents[1]/'src'
    env['PYTHONPATH']=str(src)
    p=subprocess.run([sys.executable,'-m','politics_fantasy.private_audit_cli','--root',str(root)],
                     capture_output=True,text=True,env=env,timeout=10)
    return p, json.loads(p.stdout)


def fixture(root):
    rel=store_bytes(root, DATA, SHA)
    append_private_jsonl(root,'manifest.jsonl',{'capture_id':CID,'sha256':SHA,'bytes':len(DATA),'raw_object':rel,'url':'private-url'})
    return rel


def test_clean_fake_quarantine_cli_success_no_sensitive_output(tmp_path):
    fixture(tmp_path)
    append_private_jsonl(tmp_path,'quarantine_reviews.jsonl',{
        'capture_id':CID,'sha256':SHA,'quarantine_state':'QUARANTINED_SCHEMA_PASSED'})
    process,report=run_cli(tmp_path)
    assert process.returncode==0
    assert report['object_integrity']=={'VALID_OBJECT':1}
    assert report['release_grade'] is False
    assert 'private-url' not in process.stdout
    assert CID not in process.stdout
    assert SHA not in process.stdout


def test_corrupted_fake_object_cli_nonzero(tmp_path):
    rel=fixture(tmp_path)
    (tmp_path/rel).write_bytes(b'changed')
    process,report=run_cli(tmp_path)
    assert process.returncode==2
    assert report['object_integrity']=={'BAD_RAW_SHA':1}
    assert SHA not in process.stdout


def test_missing_root_fails_without_creation_or_path_echo(tmp_path):
    missing=tmp_path/'absent-private-folder'
    process,report=run_cli(missing)
    assert process.returncode==2
    assert report=={'audit_error':'PRIVATE_AUDIT_UNAVAILABLE','release_grade':False}
    assert not missing.exists()
    assert str(missing) not in process.stdout+process.stderr


def test_unreviewed_capture_cli_nonzero(tmp_path):
    fixture(tmp_path)
    process,report=run_cli(tmp_path)
    assert process.returncode==2
    assert report['unreviewed_captures']==1


def test_symlinked_ledger_generic_error_no_outside_read(tmp_path):
    outside=tmp_path.parent/(tmp_path.name+'_secret')
    outside.write_bytes(b'not for CLI')
    (tmp_path/'manifest.jsonl').symlink_to(outside)
    process,report=run_cli(tmp_path)
    assert process.returncode==2
    assert report['audit_error']=='PRIVATE_AUDIT_UNAVAILABLE'
    assert b'not for CLI'==outside.read_bytes()
    assert 'not for CLI' not in process.stdout


def test_legacy_missing_declared_size_cli_fails_closed(tmp_path):
    """A matching SHA cannot stand in for a missing captured byte length."""
    rel = store_bytes(tmp_path, DATA, SHA)
    append_private_jsonl(tmp_path, 'manifest.jsonl', {
        'capture_id': CID, 'sha256': SHA, 'raw_object': rel,
        'url': 'private-url',  # Deliberately no 'bytes' field.
    })
    append_private_jsonl(tmp_path, 'quarantine_reviews.jsonl', {
        'capture_id': CID, 'sha256': SHA,
        'quarantine_state': 'QUARANTINED_SCHEMA_PASSED',
    })
    process, report = run_cli(tmp_path)
    assert report['object_integrity'] == {'VALID_OBJECT': 1}
    assert report['legacy_size_without_bytes'] == 1
    assert process.returncode == 2
    assert report['release_grade'] is False
    assert 'private-url' not in process.stdout
    assert CID not in process.stdout
    assert SHA not in process.stdout
