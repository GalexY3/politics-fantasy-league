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
