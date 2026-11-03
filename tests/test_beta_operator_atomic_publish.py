"""Exact-byte private/public file publication, synthetic local files only.

The stage is never the final name before os.fsync completes. Failure
injection tests contract behavior; it is NOT evidence of actual power loss.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import beta_science_operator_protocol as protocol  # noqa: E402


def _stages(folder: Path) -> list[Path]:
    return list(folder.glob(".pfl-stage-*.tmp"))


def test_atomic_publish_new_destination_complete_utf8_and_no_stages(tmp_path):
    destination = tmp_path / "publicación completa Ω.json"
    content = '{"schema":"synthetic","á":"β"}\n'
    count, sha = protocol._write_external_utf8(
        str(destination), content, maximum=65536,
        error_prefix="OPERATOR_OUTPUT",
    )
    assert destination.read_bytes() == content.encode("utf-8")
    assert count == len(content.encode("utf-8"))
    assert sha == hashlib.sha256(content.encode("utf-8")).hexdigest()
    assert not _stages(tmp_path)
    assert destination.stat().st_nlink == 1
    before = destination.read_bytes()
    with pytest.raises(protocol.ProtocolError) as rejected:
        protocol._write_external_utf8(
            str(destination), "different", maximum=65536,
            error_prefix="OPERATOR_OUTPUT",
        )
    assert rejected.value.code == "OPERATOR_OUTPUT_EXISTS"
    assert destination.read_bytes() == before and not _stages(tmp_path)


def test_atomic_publish_fsync_failure_never_exposes_final_name(tmp_path, monkeypatch):
    destination = tmp_path / "must-not-publish-private-score.json"
    def fail_sync(_fd):
        raise OSError("SYNTHETIC_FSYNC_FAILURE_WITH_PRIVATE_PATH")
    monkeypatch.setattr(protocol.os, "fsync", fail_sync)
    with pytest.raises(protocol.ProtocolError) as rejected:
        protocol._write_external_utf8(
            str(destination), '{"private":"synthetic"}\n',
            maximum=65536, error_prefix="OPERATOR_OUTPUT",
        )
    assert rejected.value.code == "OPERATOR_OUTPUT_WRITE_FAILED"
    assert not destination.exists() and not _stages(tmp_path)


def test_atomic_publish_competing_final_name_is_preserved(tmp_path, monkeypatch):
    destination = tmp_path / "competing-existing.json"
    sentinel = b"EXTERNAL_SYNTHETIC_SENTINEL_UNTOUCHED"
    def race_link(_source, published):
        Path(published).write_bytes(sentinel)
        raise FileExistsError("SIMULATED_CONCURRENT_CREATE")
    monkeypatch.setattr(protocol.os, "link", race_link)
    with pytest.raises(protocol.ProtocolError) as rejected:
        protocol._write_external_utf8(
            str(destination), '{"unpublished":"private"}\n',
            maximum=65536, error_prefix="OPERATOR_OUTPUT",
        )
    assert rejected.value.code == "OPERATOR_OUTPUT_EXISTS"
    assert destination.read_bytes() == sentinel
    assert not _stages(tmp_path)
