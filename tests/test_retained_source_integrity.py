"""Binary-only real-original hash audit and synthetic tampering exercises."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

import pytest

from politics_fantasy.procedural_index_contract import GateError
from politics_fantasy.retained_source_integrity import (
    FilePin, PINS, ROOT, audited_receipt, write_receipt,
)


def test_real_seven_sources_revalidated_without_parsing_contents():
    report=audited_receipt()
    assert report["source_total_files"]==7
    assert report["official_original_files"]==5
    assert report["private_derivatives_files"]==2
    assert report["all_pinned_files_byte_verified"]
    assert report["records_decoded_or_case_ids_exposed"]==0
    assert report["source_content_examined_for_outcomes"] is False
    assert report["historical_public_vintage_verified"] is False
    assert report["institutional_all_received_denominator"] is None
    assert report["first_public_at"] is None
    assert report["source_originals_published_in_git"] is False
    assert all(s["matching_original_on_this_local_PC"] for s in report["sources"])
    assert "PFL-scratch" not in str(report)
    assert "Nitropc" not in str(report)


def toy(tmp_path, content: bytes, *, sha=None, size=None):
    root=tmp_path/"PFL-work"
    root.mkdir()
    path=tmp_path/"PFL-fixture"
    path.mkdir()
    (path/"artifact.bin").write_bytes(content)
    pin=FilePin("TOY_TEST","../PFL-fixture/artifact.bin",
                sha or sha256(content).hexdigest(),
                len(content) if size is None else size,
                "OFFICIAL_CAPTURE_ORIGINAL")
    return root, pin, path/"artifact.bin"


def test_synthetic_tampered_bytes_are_rejected_without_decoding(tmp_path):
    root,pin,path=toy(tmp_path,b"a sample")
    report=audited_receipt(root=root,pins=(pin,),at=datetime(2026,10,31,tzinfo=timezone.utc))
    assert report["official_original_files"]==1
    assert report["local_audit_safe_by"]=="2026-10-31T00:00:01+00:00"
    path.write_bytes(b"a samp1e")
    with pytest.raises(GateError,match="RETAINED_SOURCE_SHA256_MISMATCH"):
        audited_receipt(root=root,pins=(pin,))


def test_size_drift_and_missing_are_fail_closed(tmp_path):
    root,pin,path=toy(tmp_path,b"12345")
    path.write_bytes(b"1234")
    with pytest.raises(GateError,match="RETAINED_SOURCE_SIZE_DRIFT"):
        audited_receipt(root=root,pins=(pin,))
    path.unlink()
    with pytest.raises(GateError,match="RETAINED_SOURCE_MISSING_OR_LINK"):
        audited_receipt(root=root,pins=(pin,))


def test_duplicate_source_and_scope_changes_rejected(tmp_path):
    root,pin,_=toy(tmp_path,b"abc")
    with pytest.raises(GateError,match="REPLAYED_RETAINED_SOURCE_PIN"):
        audited_receipt(root=root,pins=(pin,pin))
    with pytest.raises(GateError,match="INVALID_RETAINED_FILE_PIN"):
        FilePin("BAD","../../etc/passwd","a"*64,100,"OFFICIAL_CAPTURE_ORIGINAL")
    with pytest.raises(GateError,match="INVALID_RETAINED_FILE_PIN"):
        FilePin("BAD","../PFL-fixture/binary", "a"*64,0,"OFFICIAL_CAPTURE_ORIGINAL")


def test_receipt_generator_cannot_substitute_synthetic_pins(tmp_path):
    root,pin,_=toy(tmp_path,b"abc")
    intended=ROOT/"data/source_manifests/r9_retained_sources_integrity_20261031.json"
    with pytest.raises(GateError,match="RECEIPT_OUTPUT_OR_PINS_NOT_ALLOWLISTED"):
        write_receipt(path=intended,root=root,pins=(pin,))
    with pytest.raises(GateError,match="RECEIPT_OUTPUT_OR_PINS_NOT_ALLOWLISTED"):
        write_receipt(path=tmp_path/"hijack.json")
