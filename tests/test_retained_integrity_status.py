"""An immutable R9 binary integrity receipt is not a source-vintage archive."""
from hashlib import sha256
import json
from pathlib import Path

import pytest

from politics_fantasy.retained_integrity_status import RECEIPT,PINNED_SHA,status


def test_actual_sha_locked_receipt_covers_seven_and_never_accepts_science():
    assert sha256(RECEIPT.read_bytes()).hexdigest()==PINNED_SHA
    report=status()
    assert report["status"]=="PAST_LOCAL_BINARY_INTEGRITY_CONFIRMED"
    assert report["originals_verified"]==5
    assert report["private_derivatives_verified"]==2
    assert len(report["source_rows"])==7
    assert report["complete_institutional_denominator"] is None
    assert not report["source_use_rights_for_inference_established"]
    assert not report["verified_historical_vintages"]
    assert not report["case_identifiers_in_response"]
    assert not report["individual_outcomes_in_response"]
    assert "original.csv" not in str(report)
    assert "PFL-scratch" not in str(report)


def test_asof_before_real_audit_hides_every_count_and_hash():
    for when in ("2024-01-01T00:00:00Z","2026-10-31T07:08:41.999Z"):
        d=status(as_of=when)
        assert d["status"]=="INTEGRITY_AUDIT_NOT_KNOWN_AT_CUT"
        assert d["source_rows"]==[]
        assert d["total_files_verified"] is None
        assert d["local_audit_safe_by"] is None
        assert d["receipt_sha256"] is None
        assert "PARCAN_XI" not in str(d)
        assert "67ae2bc" not in str(d)
    assert status(as_of="2026-10-31T07:08:42Z")["total_files_verified"]==7


@pytest.mark.parametrize("field,value",[
    ("scientific_cycles",1),
    ("historical_public_vintage_verified",True),
    ("institutional_all_received_denominator",1754),
    ("source_originals_published_in_git",True),
])
def test_attacker_cannot_promote_receipt_to_science(tmp_path:Path,field,value):
    doc=json.loads(RECEIPT.read_text(encoding="utf8"))
    doc[field]=value
    path=tmp_path/"forged.json"
    path.write_text(json.dumps(doc),encoding="utf8")
    assert status(path=path)["status"]=="INTEGRITY_RECEIPT_QUARANTINED"


def test_attacker_cannot_rewrite_per_file_hash_or_number(tmp_path:Path):
    doc=json.loads(RECEIPT.read_text(encoding="utf8"))
    doc["sources"][0]["sha256"]="f"*64
    file=tmp_path/"forged.json"
    file.write_text(json.dumps(doc),encoding="utf8")
    assert status(path=file)["source_rows"]==[]


def test_invalid_cut_is_rejected_not_replaced_with_current():
    with pytest.raises(ValueError):
        status(as_of="2026-10-31")
