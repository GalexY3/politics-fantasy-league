"""BOE 2023 official Albacete candidacy labels: no party registry or persons inferred."""
from __future__ import annotations
import json

from politics_fantasy.candidacy_api import status

def test_known_eight_candidacy_labels_source_provenance():
    r=status()
    assert r["ok"] is True
    assert r["proclaimed_candidacy_lists"]==8
    assert r["source_document"]=="BOE-A-2023-15066"
    assert r["source_sha256"]=="d1c179fcfab9889df272753ad3d44513f86cec703805219834b7d048ef0eda20"
    assert r["verified_legal_parties"]==0
    assert r["people_joined"]==0
    assert r["real_person_scoring"] is False
    assert [x["acronym"] for x in r["lists"]]==["PSOE","FO","PP","PACMA","PUM+J","SUMAR","VOX","RECORTES CERO"]
    assert all(x["type"]=="ELECTORAL_CANDIDACY_NOT_LEGAL_PARTY" for x in r["lists"])

def test_bad_hash_fails_closed(tmp_path):
    from politics_fantasy.candidacy_api import DEFAULT
    d=json.loads(DEFAULT.read_text(encoding="utf8"))
    d["original_sha256"]="bad"
    p=tmp_path/"bad.json";p.write_text(json.dumps(d),encoding="utf8")
    assert status(p)["ok"] is False

def test_cannot_attach_registered_party_or_people(tmp_path):
    from politics_fantasy.candidacy_api import DEFAULT
    d=json.loads(DEFAULT.read_text(encoding="utf8"))
    d["lists"][0]["registered_party_id"]="RPP:invented"
    p=tmp_path/"bad.json";p.write_text(json.dumps(d),encoding="utf8")
    assert status(p)["ok"] is False
    d["lists"][0]["registered_party_id"]=None
    d["lists"][0]["named_person_count"]=1
    p.write_text(json.dumps(d),encoding="utf8")
    assert status(p)["ok"] is False
