"""Synthetic snapshots only; no real outcomes opened or analyzed."""
from __future__ import annotations

import csv
from datetime import datetime,timezone
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from build_parcan_local_processes import IngestError,EXPECTED_HEADERS
from diff_parcan_capture_vintages import compare,read_vintage
import diff_parcan_capture_vintages as engine


@pytest.fixture(autouse=True)
def mock_approved_workspace(tmp_path:Path,monkeypatch):
    """Synthetic originals must still live outside a mock Git directory."""
    fake_repo=tmp_path/"PFL-trabajo"
    fake_repo.mkdir()
    monkeypatch.setattr(engine,"REPO",fake_repo)


def make_vintage(folder:Path,ids:dict[str,str],captured:str,*,leg=11,year=2026,
                 kind="PE",mutator=None):
    folder.mkdir()
    out=StringIO(newline="")
    csvout=csv.writer(out)
    csvout.writerow(EXPECTED_HEADERS)
    for ident,created in ids.items():
        csvout.writerow([ident,str(leg),"Text private not exported",created,
                         "SITUACION_SECRETA","PROCEDIMIENTO","RESULTADO_SECRETO","DETALLE"])
    raw=out.getvalue().encode("utf-8")
    filename="parcan_2026_XI_PE_original.csv"
    (folder/filename).write_bytes(raw)
    receipt={
        "schema":"pfl.parcan.prospective_capture_receipt.v1",
        "source_publisher":"Parlamento de Canarias",
        "scope":{"year":year,"legislature":leg,"type":kind},
        "canonical_url":f"https://www.parcan.es/api/iniciativas/{year}/{leg}/{kind}/?format=csv",
        "catalogue_url":"https://datos.parcan.es/dataset/iniciativas_tipope_anio2026_xilegislatura",
        "catalogue_licence_label":"odc-pddl",
        "rights_review_state":"CATALOGUE_LABEL_ONLY_NO_PERSONAL_USE_ADJUDICATION",
        "terms_accepted":False,"http_status":200,
        "original_filename":filename,
        "original_sha256":sha256(raw).hexdigest(),
        "original_bytes":len(raw),
        "capture_completed_at":captured,
        "first_public_at":None,"outcomes_analyzed":False,
    }
    if mutator: mutator(receipt)
    payload=(json.dumps(receipt,sort_keys=True)+"\n").encode()
    (folder/"capture_receipt.json").write_bytes(payload)
    return sha256(payload).hexdigest()


def test_prospective_diff_does_not_infer_outcomes_or_first_public(tmp_path:Path):
    old=tmp_path/"old"
    recent=tmp_path/"new"
    h1=make_vintage(old,{"11L/PE-0001":"2026-01-03","11L/PE-0002":"2026-03-04",
                         "11L/PE-0004":"2026-05-06"},"2026-10-31T08:30:00Z")
    h2=make_vintage(recent,{"11L/PE-0001":"2026-01-03","11L/PE-0002":"2026-03-05",
                             "11L/PE-0003":"2026-07-08"},"2026-11-30T09:10:00Z")
    result=compare(read_vintage(old,receipt_sha256=h1),
                   read_vintage(recent,receipt_sha256=h2))
    assert result["earlier_observed_rows"]==3
    assert result["later_observed_rows"]==3
    assert result["same_source_id_and_creation_date"]==1
    assert result["source_ids_present_only_in_later_capture"]==1
    assert result["source_ids_absent_in_later_capture"]==1
    assert result["source_reported_creation_date_changed"]==1
    assert result["absence_is_not_terminal_outcome"]
    assert result["new_presence_is_not_newly_registered_at_capture"]
    assert result["first_public_at_confirmed"] is None
    assert result["historical_asof_eligible"] is False
    assert result["outcome_transitions_examined"] is False
    assert result["scientific_abh_cycles"]==0
    text=json.dumps(result)
    for denied in ("11L/PE", "RESULTADO_SECRETO", "Text private", "SITUACION_SECRETA"):
        assert denied not in text


def test_identical_bytes_at_different_captures_is_not_claimed_new(tmp_path:Path):
    old,recent=tmp_path/"old",tmp_path/"new"
    h1=make_vintage(old,{"11L/PE-0001":"2026-01-03"},"2026-10-31T08:30:00Z")
    h2=make_vintage(recent,{"11L/PE-0001":"2026-01-03"},"2026-11-01T08:30:00Z")
    result=compare(read_vintage(old,receipt_sha256=h1),read_vintage(recent,receipt_sha256=h2))
    assert result["source_ids_present_only_in_later_capture"]==0
    assert result["source_ids_absent_in_later_capture"]==0
    assert result["source_reported_creation_date_changed"]==0


@pytest.mark.parametrize("mutation,code",[
 (lambda r:r.update(first_public_at="2026-01-01T00:00:00Z"),"UNTRUSTED_OR_CHANGED_SOURCE_SCOPE"),
 (lambda r:r.update(outcomes_analyzed=True),"UNTRUSTED_OR_CHANGED_SOURCE_SCOPE"),
 (lambda r:r.update(terms_accepted=True),"UNTRUSTED_OR_CHANGED_SOURCE_SCOPE"),
 (lambda r:r.update(catalogue_licence_label="custom"),"UNTRUSTED_OR_CHANGED_SOURCE_SCOPE"),
 (lambda r:r.update(rights_review_state="APPROVED_FOR_SCORING"),"UNTRUSTED_OR_CHANGED_SOURCE_SCOPE"),
 (lambda r:r.update(original_filename="../../secret.csv"),"UNSAFE_RAW_FILENAME"),
])
def test_no_unreviewed_rights_history_outcome_or_paths(tmp_path:Path,mutation,code):
    folder=tmp_path/"old"
    sha=make_vintage(folder,{"11L/PE-0001":"2026-01-03"},
         "2026-10-31T08:30:00Z",mutator=mutation)
    with pytest.raises(IngestError,match=code):
        read_vintage(folder,receipt_sha256=sha)


def test_distinct_institutional_scope_or_wrong_order_denied(tmp_path:Path):
    a,b=tmp_path/"a",tmp_path/"b"
    ha=make_vintage(a,{"11L/PE-0001":"2026-01-03"},"2026-11-01T00:00:00Z")
    hb=make_vintage(b,{"11L/PE-0002":"2026-01-03"},"2026-10-31T00:00:00Z")
    av=read_vintage(a,receipt_sha256=ha)
    bv=read_vintage(b,receipt_sha256=hb)
    with pytest.raises(IngestError,match="OUT_OF_ORDER_SOURCE_VINTAGES"):
        compare(av,bv)
    bv["scope"]={"year":2024,"legislature":11,"type":"PE"}
    with pytest.raises(IngestError,match="CROSS_INSTITUTION_OR_COHORT_JOIN_FORBIDDEN"):
        compare(av,bv)


def test_pin_and_raw_mismatch_detected(tmp_path:Path):
    folder=tmp_path/"old"
    pin=make_vintage(folder,{"11L/PE-0001":"2026-01-03"},"2026-10-31T08:30:00Z")
    with pytest.raises(IngestError,match="RECEIPT_PIN_MISMATCH"):
        read_vintage(folder,receipt_sha256="f"*64)
    with (folder/"parcan_2026_XI_PE_original.csv").open("ab") as f:
        f.write(b"CHANGED\n")
    with pytest.raises(IngestError,match="ORIGINAL_SHA_AND_BYTES_MISMATCH"):
        read_vintage(folder,receipt_sha256=pin)


def test_bad_year_and_duplicate_ids_are_quarantined(tmp_path:Path):
    folder=tmp_path/"old"
    pin=make_vintage(folder,{"11L/PE-0001":"2025-01-03"},"2026-10-31T08:30:00Z")
    with pytest.raises(IngestError,match="SOURCE_YEAR_MISMATCH"):
        read_vintage(folder,receipt_sha256=pin)


def test_output_written_once_only_outside_git_and_without_ids(tmp_path:Path):
    a,b=tmp_path/"old",tmp_path/"new"
    ha=make_vintage(a,{"11L/PE-0001":"2026-01-03"},"2026-10-31T08:30:00Z")
    hb=make_vintage(b,{"11L/PE-0001":"2026-01-03",
                       "11L/PE-0002":"2026-02-03"},"2026-11-30T09:10:00Z")
    output=tmp_path/"scratch"/"aggregate.json"
    output.parent.mkdir()
    result=engine.run(earlier=a,later=b,earlier_receipt_sha=ha,later_receipt_sha=hb,
                      output=output)
    assert result["later"]==2 and result["previous"]==1
    assert result["sha256"]==sha256(output.read_bytes()).hexdigest()
    assert "11L/PE" not in output.read_text(encoding="utf-8")
    with pytest.raises(IngestError,match="OUTPUT_MUST_BE_NEW_OUTSIDE_GIT"):
        engine.run(earlier=a,later=b,earlier_receipt_sha=ha,later_receipt_sha=hb,
                   output=output)
    with pytest.raises(IngestError,match="OUTPUT_MUST_BE_NEW_OUTSIDE_GIT"):
        engine.run(earlier=a,later=b,earlier_receipt_sha=ha,later_receipt_sha=hb,
                   output=engine.REPO/"unsafe.json")
