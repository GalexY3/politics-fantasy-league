"""Source-backed 2023 province nomination atlas; no personal political profiling."""
from __future__ import annotations
import json
from pathlib import Path
from politics_fantasy.nomination_atlas import status,DEFAULT

def mutate(tmp_path,fn):
    x=json.loads(DEFAULT.read_text(encoding="utf8"))
    fn(x)
    p=tmp_path/"changed.json";p.write_text(json.dumps(x),encoding="utf8")
    return status(p)

def test_verified_bounded_source_25_provinces_263_distinct_lists():
    d=status()
    assert d["ok"] is True,d
    assert d["n_provinces"]==25
    assert d["n_candidacies"]==263
    assert d["detected_provincial_sections"]==52
    assert d["unresolved_provincial_sections"]==27
    assert d["real_people_joined"]==0
    assert d["legal_parties_verified"]==0
    assert d["real_people_scoring"] is False

def test_same_acronym_not_same_candidacy_and_no_person_data():
    d=status()
    p=[x for x in d["provinces"] if x["province_id"]=="ALBACETE"][0]
    assert p["n_candidacies"]==8
    fo=[x for x in p["lists"] if x["acronym"]=="FO"][0]
    matches=[a for v in d["provinces"] for a in v["lists"] if a["acronym"]=="FO"]
    assert len(matches)>1
    assert len({x["id"] for x in matches})==len(matches)
    assert all(x["semantics"]=="ELECTORAL_CANDIDACY_LABEL_ONLY" for x in matches)

def test_unsafe_legal_party_id_rejected(tmp_path):
    r=mutate(tmp_path,lambda d:d["provinces"][0]["lists"][0].update(
        {"legal_party_registration_id":"RPP:guess"}))
    assert not r["ok"]
    assert r["error"]=="CANDIDACY_IDENTITY_UNSAFE"

def test_source_sha_tamper_rejected(tmp_path):
    r=mutate(tmp_path,lambda d:d.update({"original_sha256":"f"*64}))
    assert not r["ok"]
    assert r["error"]=="SOURCE_PROVENANCE_OR_COUNTS_CHANGED"

def test_fake_person_count_rejected(tmp_path):
    r=mutate(tmp_path,lambda d:d["provinces"][0]["lists"][0].update(
        {"person_count_joined":1}))
    assert not r["ok"]

def test_duplicate_province_rejected(tmp_path):
    def duplicate(d):d["provinces"][1]["province_id"]=d["provinces"][0]["province_id"]
    r=mutate(tmp_path,duplicate)
    assert not r["ok"]

def test_duplicate_ordinals_rejected(tmp_path):
    r=mutate(tmp_path,lambda d:d["provinces"][0]["lists"][1].update({"position":1}))
    assert not r["ok"]

def test_false_claim_of_completeness_rejected(tmp_path):
    r=mutate(tmp_path,lambda d:d.update({"province_sections_parsed":52}))
    assert not r["ok"]

def test_missing_data_fails_closed(tmp_path):
    r=status(tmp_path/"missing.json")
    assert r["ok"] is False
    assert r["real_people_scoring"] is False
