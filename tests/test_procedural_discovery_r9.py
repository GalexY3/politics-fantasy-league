"""Real worker-matrix SHA lineage, redaction and fail-closed temporal gates."""
from hashlib import sha256
import json
from pathlib import Path

import pytest

from politics_fantasy.procedural_discovery_r9 import (
    REGIONAL,NATIONAL,REGIONAL_SHA,NATIONAL_SHA,status,
)


def test_r9_real_sanitized_documents_are_pinned_but_not_real_source_originals():
    assert sha256(REGIONAL.read_bytes()).hexdigest()==REGIONAL_SHA
    assert sha256(NATIONAL.read_bytes()).hexdigest()==NATIONAL_SHA
    x=status()
    assert x["status"]=="R9_DISCOVERY_ONLY_RIGHTS_AND_DENOMINATORS_BLOCKED"
    assert x["regional_source_count"]==8
    assert x["national_source_count"]==11
    assert len(x["regional_highlights"])==4
    assert len(x["national_highlights"])==4
    assert not x["new_outcomes_admitted"]
    assert x["institutional_population_denominator"] is None
    assert x["R9_real_originals_acquired"]==0
    assert x["pre_registration_outcome_header_exposure"]
    assert x["original_register_identifiers_not_republished"]
    content=json.dumps(x,ensure_ascii=False)
    assert "09/PPLI" not in content
    assert "9155" not in content and "9160" not in content
    assert "30374" not in content and "3833" not in content


def test_earlier_cut_hides_source_names_hash_reasons_and_counts():
    for t in ("2016-01-01T00:00:00Z","2026-10-31T23:59:59.999Z"):
        x=status(as_of=t)
        assert x["status"]=="R9_DISCOVERY_NOT_KNOWN_AT_CUT"
        assert x["regional_source_count"] is None
        assert x["regional_highlights"]==[]
        assert x["national_highlights"]==[]
        assert x["observed_source_matrix_sha256"] is None
        assert x["pre_registration_outcome_header_exposure"] is None
        assert x["source_metadata_safe_by"] is None
        assert "Galicia" not in str(x) and "TC_" not in str(x)
    assert status(as_of="2026-11-01T00:00:00Z")["regional_source_count"]==8


@pytest.mark.parametrize("field,value",[
    ("rights_for_bulk_reuse_proven",True),
    ("all_received_denominator",9),
    ("source_original_sha256","a"*64),
    ("outcomes_for_inference_admitted",True),
])
def test_regional_tampering_never_promotes_scientific_source(tmp_path:Path,field,value):
    obj=json.loads(REGIONAL.read_text(encoding="utf8"))
    obj["entries"][0][field]=value
    p=tmp_path/"forged_region.json"
    p.write_text(json.dumps(obj),encoding="utf8")
    assert status(regional_path=p)["status"]=="R9_DOCUMENTARY_SOURCE_QUARANTINED"


def test_national_reclassify_grain_or_claim_count_quarantines(tmp_path:Path):
    obj=json.loads(NATIONAL.read_text(encoding="utf8"))
    obj["entries"][1]["intake_count_from_unreplayed_original"]=9155
    p=tmp_path/"forged_national.json"
    p.write_text(json.dumps(obj),encoding="utf8")
    assert status(national_path=p)["status"]=="R9_DOCUMENTARY_SOURCE_QUARANTINED"


def test_worker_inherited_details_do_not_leak_via_api():
    r=status()
    assert any(s["documentary_limit"]=="CONTRADICTORY_EDITORIAL_HEADING_AND_ENNUMERATION"
               for s in r["regional_highlights"])
    assert len({s["documentary_unit"] for s in r["national_highlights"]})>1
    assert all(s["risk_population_denominator"] is None for s in
               r["regional_highlights"]+r["national_highlights"])


@pytest.mark.parametrize("bad",["", "not-a-date","2026-10-31","2026-10-31T23:59:59"])
def test_invalid_asof_must_not_default_to_now(bad):
    with pytest.raises(ValueError):
        status(as_of=bad)
