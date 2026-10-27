"""No-network negative tests of anchored local capture store; POSIX only."""
import hashlib
import os
from pathlib import Path
import threading
import pytest

from politics_fantasy.secure_store import store_bytes, append_private_jsonl, preflight_private_storage

PAYLOAD = b'{"synthetic": "politics fantasy"}'
DIGEST = hashlib.sha256(PAYLOAD).hexdigest()

pytestmark = pytest.mark.skipif(os.name != "posix", reason="POSIX anchored-dirfd store")


def test_normal_content_addressed_store_and_append(tmp_path):
    rel = store_bytes(tmp_path, PAYLOAD, DIGEST)
    assert rel == f"objects/{DIGEST[:2]}/{DIGEST}"
    assert (tmp_path / rel).read_bytes() == PAYLOAD
    assert store_bytes(tmp_path, PAYLOAD, DIGEST) == rel
    append_private_jsonl(tmp_path, "manifest.jsonl", {"synthetic": True})
    assert '"synthetic": true' in (tmp_path / "manifest.jsonl").read_text()


def test_objects_symlink_to_outside_fails_closed(tmp_path):
    outside = tmp_path.parent / (tmp_path.name + "_outside")
    outside.mkdir()
    (tmp_path / "objects").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="SYMLINK_OR_UNSAFE_STORE_DIRECTORY"):
        store_bytes(tmp_path, PAYLOAD, DIGEST)
    assert list(outside.iterdir()) == []


def test_hash_shard_symlink_to_outside_fails_closed(tmp_path):
    outside = tmp_path.parent / (tmp_path.name + "_outside")
    outside.mkdir()
    (tmp_path / "objects").mkdir(mode=0o700)
    (tmp_path / "objects" / DIGEST[:2]).symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="SYMLINK_OR_UNSAFE_STORE_DIRECTORY"):
        store_bytes(tmp_path, PAYLOAD, DIGEST)
    assert list(outside.iterdir()) == []


def test_existing_object_symlink_refused_without_modifying_target(tmp_path):
    outside = tmp_path.parent / (tmp_path.name + "_outside_data")
    outside.write_bytes(b"original outside")
    shard = tmp_path / "objects" / DIGEST[:2]
    shard.mkdir(parents=True,mode=0o700)
    (shard.parent).chmod(0o700)
    (shard / DIGEST).symlink_to(outside)
    with pytest.raises(ValueError, match="UNSAFE_EXISTING_OBJECT"):
        store_bytes(tmp_path, PAYLOAD, DIGEST)
    assert outside.read_bytes() == b"original outside"


def test_manifest_symlink_refused_without_modifying_target(tmp_path):
    outside = tmp_path.parent / (tmp_path.name + "_outside_manifest")
    outside.write_bytes(b"outside")
    (tmp_path / "manifest.jsonl").symlink_to(outside)
    with pytest.raises(ValueError, match="UNSAFE_PRIVATE_LEDGER"):
        append_private_jsonl(tmp_path, "manifest.jsonl", {"x": "fake"})
    assert outside.read_bytes() == b"outside"


def test_root_symlink_refused(tmp_path):
    link = tmp_path.parent / (tmp_path.name + "_link")
    link.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(ValueError, match="SYMLINK_STORAGE_ROOT"):
        store_bytes(link, PAYLOAD, DIGEST)


def test_wrong_digest_refused_before_any_write(tmp_path):
    with pytest.raises(ValueError, match="INVALID_STORE_DIGEST"):
        store_bytes(tmp_path, PAYLOAD, "0" * 64)
    assert list(tmp_path.iterdir()) == []


def test_device_like_directory_rejected(tmp_path):
    (tmp_path / "objects").write_bytes(b"not directory")
    with pytest.raises(ValueError, match="SYMLINK_OR_UNSAFE_STORE_DIRECTORY"):
        store_bytes(tmp_path, PAYLOAD, DIGEST)


def test_parallel_same_hash_writers_dont_clobber(tmp_path):
    results, errors = [], []
    def worker():
        try: results.append(store_bytes(tmp_path, PAYLOAD, DIGEST))
        except BaseException as exc: errors.append(repr(exc))
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join(timeout=10)
    assert errors == []
    assert len(results) == 10
    assert len(set(results)) == 1
    shard = tmp_path / "objects" / DIGEST[:2]
    assert [p.name for p in shard.iterdir()] == [DIGEST]


def test_preflight_denies_bad_manifest_before_contact(tmp_path):
    outside=tmp_path.parent / (tmp_path.name+"_outside_preflight")
    outside.write_bytes(b"outside")
    (tmp_path/"manifest.jsonl").symlink_to(outside)
    with pytest.raises(ValueError, match="UNSAFE_PRIVATE_LEDGER"):
        preflight_private_storage(tmp_path,"manifest.jsonl")
    assert outside.read_bytes()==b"outside"

def test_world_writable_store_root_rejected(tmp_path):
    tmp_path.chmod(0o777)
    with pytest.raises(ValueError, match="UNSAFE_STORE_OWNERSHIP_OR_PERMISSIONS"):
        store_bytes(tmp_path, PAYLOAD, DIGEST)


def test_group_writable_object_directory_rejected(tmp_path):
    objects=tmp_path/"objects"
    objects.mkdir()
    objects.chmod(0o770)
    with pytest.raises(ValueError, match="UNSAFE_STORE_OWNERSHIP_OR_PERMISSIONS"):
        store_bytes(tmp_path, PAYLOAD, DIGEST)


def test_world_readable_preexisting_digest_rejected(tmp_path):
    obj=tmp_path/"objects"/DIGEST[:2]/DIGEST
    obj.parent.mkdir(parents=True,mode=0o700)
    obj.parent.parent.chmod(0o700)
    obj.write_bytes(PAYLOAD)
    obj.chmod(0o644)
    with pytest.raises(ValueError, match="UNSAFE_STORE_OWNERSHIP_OR_PERMISSIONS"):
        store_bytes(tmp_path, PAYLOAD, DIGEST)


def test_unsafe_existing_manifest_rejected(tmp_path):
    manifest=tmp_path/"manifest.jsonl"
    manifest.write_text("private")
    manifest.chmod(0o666)
    with pytest.raises(ValueError, match="UNSAFE_STORE_OWNERSHIP_OR_PERMISSIONS"):
        append_private_jsonl(tmp_path,"manifest.jsonl",{"fake":1})

def test_write_failure_does_not_leave_partial_temporary_file(tmp_path, monkeypatch):
    import politics_fantasy.secure_store as module
    def failure(fd, data):
        os.write(fd, b"PARTIAL_PRIVATE_FAKE")
        raise OSError("SYNTHETIC_DISK_FAILURE")
    monkeypatch.setattr(module, "_write_all", failure)
    with pytest.raises(OSError, match="SYNTHETIC_DISK_FAILURE"):
        store_bytes(tmp_path, PAYLOAD, DIGEST)
    shard=tmp_path/"objects"/DIGEST[:2]
    assert not list(shard.iterdir())
    assert not (tmp_path/"manifest.jsonl").exists()


def test_parallel_private_jsonl_appends_never_interleave_partial_writes(tmp_path, monkeypatch):
    """One line may require multiple syscalls; lock the entire record on POSIX."""
    import json
    import time
    import politics_fantasy.secure_store as module

    original_write = module._write_all

    def split_write(fd, payload):
        midway = max(1, len(payload) // 2)
        original_write(fd, payload[:midway])
        time.sleep(0.003)  # force a scheduling window between syscalls
        original_write(fd, payload[midway:])

    monkeypatch.setattr(module, "_write_all", split_write)
    errors = []

    def worker(i):
        try:
            append_private_jsonl(tmp_path, "manifest.jsonl", {"synthetic_id": i})
        except BaseException as exc:
            errors.append(repr(exc))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(16)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)
    assert all(not thread.is_alive() for thread in threads)
    assert errors == []
    lines = (tmp_path / "manifest.jsonl").read_text().splitlines()
    assert len(lines) == 16
    values = [json.loads(line)["synthetic_id"] for line in lines]
    assert sorted(values) == list(range(16))


def test_private_capture_metadata_calls_directory_fsync(tmp_path, monkeypatch):
    """Observable barriers, not a hardware power-loss recovery certification."""
    import stat
    import politics_fantasy.secure_store as module

    actual_fsync = os.fsync
    calls = []

    def record_fsync(fd):
        calls.append("directory" if stat.S_ISDIR(os.fstat(fd).st_mode) else "file")
        return actual_fsync(fd)

    monkeypatch.setattr(module.os, "fsync", record_fsync)
    rel = store_bytes(tmp_path, PAYLOAD, DIGEST)
    assert (tmp_path / rel).read_bytes() == PAYLOAD
    # objects/, SHA shard and final object name each require a directory sync.
    assert calls.count("directory") >= 3
    before = calls.count("directory")
    append_private_jsonl(tmp_path, "manifest.jsonl", {"synthetic": True})
    assert calls.count("directory") > before
    assert (tmp_path / "manifest.jsonl").read_text().endswith("\n")


def test_new_directory_fsync_failure_does_not_claim_stored_success(tmp_path, monkeypatch):
    """If directory sync is unsupported/fails, do not silently downgrade."""
    import stat
    import politics_fantasy.secure_store as module

    actual_fsync = os.fsync

    def fail_dir(fd):
        if stat.S_ISDIR(os.fstat(fd).st_mode):
            raise OSError("SYNTHETIC_DIRECTORY_SYNC_FAILURE")
        return actual_fsync(fd)

    monkeypatch.setattr(module.os, "fsync", fail_dir)
    with pytest.raises(OSError, match="SYNTHETIC_DIRECTORY_SYNC_FAILURE"):
        store_bytes(tmp_path, PAYLOAD, DIGEST)
    assert not (tmp_path / "manifest.jsonl").exists()


def test_private_append_rejects_nonfinite_numbers_before_file_creation(tmp_path):
    import math
    for number in (float("nan"), float("inf"), -float("inf")):
        with pytest.raises(ValueError):
            append_private_jsonl(tmp_path, "manifest.jsonl", {"bytes": number})
        assert not (tmp_path / "manifest.jsonl").exists()


def test_first_created_root_syncs_existing_parent_directory(tmp_path, monkeypatch):
    """A new root needs metadata sync of its pre-existing operator parent."""
    import stat
    import politics_fantasy.secure_store as module
    original = os.fsync
    synced_parent = []
    parent_ino = tmp_path.stat().st_ino

    def tracing_fsync(fd):
        attr = os.fstat(fd)
        if stat.S_ISDIR(attr.st_mode) and attr.st_ino == parent_ino:
            synced_parent.append(True)
        return original(fd)

    monkeypatch.setattr(module.os, "fsync", tracing_fsync)
    fresh = tmp_path / "new_private_capture"
    rel = store_bytes(fresh, PAYLOAD, DIGEST)
    assert (fresh / rel).read_bytes() == PAYLOAD
    assert synced_parent


def test_missing_private_root_ancestor_rejected_without_creating_tree(tmp_path):
    nested = tmp_path / "missing_parent" / "new_root"
    with pytest.raises(ValueError, match="MISSING_TRUSTED_STORE_PARENT"):
        store_bytes(nested, PAYLOAD, DIGEST)
    assert not (tmp_path / "missing_parent").exists()


def test_caught_partial_jsonl_append_rolls_back_to_previous_complete_record(tmp_path, monkeypatch):
    """Caught I/O errors do not poison later rows; does not simulate SIGKILL."""
    import politics_fantasy.secure_store as module
    append_private_jsonl(tmp_path, "manifest.jsonl", {"synthetic_id": 1})
    ledger = tmp_path / "manifest.jsonl"
    original = ledger.read_bytes()

    def half_then_fail(fd, payload):
        os.write(fd, payload[:max(1, len(payload) // 2)])
        raise OSError("SYNTHETIC_PARTIAL_WRITE")

    with monkeypatch.context() as patcher:
        patcher.setattr(module, "_write_all", half_then_fail)
        with pytest.raises(OSError, match="SYNTHETIC_PARTIAL_WRITE"):
            append_private_jsonl(tmp_path, "manifest.jsonl", {"synthetic_id": 2})
    assert ledger.read_bytes() == original
    append_private_jsonl(tmp_path, "manifest.jsonl", {"synthetic_id": 3})
    import json
    assert [json.loads(x)["synthetic_id"] for x in ledger.read_text().splitlines()] == [1, 3]
