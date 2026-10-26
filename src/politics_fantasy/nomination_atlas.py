"""Original-BOE public 2023 Congress nomination-list atlas.

Source rows are *electoral lists*, not legal party identities, individuals,
memberships, votes, representation, merit, or political influence.
Only 25/52 documented sections currently pass strict extraction.
"""
from __future__ import annotations
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
DEFAULT=ROOT/"data/observatory/boe_2023_multiterritory_reviewed.json"
SOURCE_SHA="d1c179fcfab9889df272753ad3d44513f86cec703805219834b7d048ef0eda20"
KEYS=("province_label","province_id","congress_candidacies","lists",
      "legal_registered_parties_confirmed","people_identified")
SECURE_ID=re.compile(r"^BOE-A-2023-15066:[A-Z0-9_]+:CONGRESO:\d{3}$")

def status(path:Path|None=None)->dict:
    p=Path(path) if path is not None else DEFAULT
    stopped={"ok":False,"source_kind":"OFFICIAL_2023_NOMINATION_ATLAS_PARTIAL",
        "real_people_joined":0,"legal_parties_verified":0,"real_people_scoring":False}
    try:
        if not p.is_file() or p.stat().st_size>150_000:
            return {**stopped,"error":"MISSING_OR_OVERSIZE"}
        d=json.loads(p.read_text(encoding="utf8"))
        items=d["provinces"]
        if (d["original_sha256"]!=SOURCE_SHA or
            d["id"]!="BOE_A_2023_15066_MULTIPROVINCE_EXTRACT" or
            d["province_sections_detected"]!=52 or
            d["province_sections_parsed"]!=25 or
            d["list_headings_extracted"]!=263 or
            d["registered_legal_parties_validated"]!=0 or
            d["no_person_names_in_export"] is not True or
            len(items)!=25 or not isinstance(d["issues"],list)):
            return {**stopped,"error":"SOURCE_PROVENANCE_OR_COUNTS_CHANGED"}
        found=set()
        out=[]
        for province in items:
            if any(k not in province for k in KEYS):
                return {**stopped,"error":"PROVINCE_SCHEMA"}
            pid=province["province_id"]
            if pid in found or not isinstance(pid,str) or not pid.isupper():
                return {**stopped,"error":"DUPLICATE_PROVINCE"}
            found.add(pid)
            lists=province["lists"]
            if (not isinstance(lists,list) or len(lists)!=province["congress_candidacies"]
                or province["people_identified"]!=0 or
                province["legal_registered_parties_confirmed"]!=0):
                return {**stopped,"error":"PROVINCE_INVALID"}
            rows=[]
            for index,row in enumerate(lists,1):
                if (row.get("position")!=index or
                    not SECURE_ID.fullmatch(row.get("candidacy_id","")) or
                    row["candidacy_id"]!=f"BOE-A-2023-15066:{pid}:CONGRESO:{index:03d}" or
                    row.get("legal_party_registration_id") is not None or
                    row.get("person_count_joined")!=0 or
                    row.get("entity_semantics")!="ELECTORAL_LIST_NOT_REGISTERED_PARTY" or
                    row.get("province_label")!=province["province_label"]):
                    return {**stopped,"error":"CANDIDACY_IDENTITY_UNSAFE"}
                acr=row.get("acronym")
                if not isinstance(acr,str) or not 1<len(acr)<70:
                    return {**stopped,"error":"INVALID_ACRONYM"}
                rows.append({"id":row["candidacy_id"],"acronym":acr,
                    "semantics":"ELECTORAL_CANDIDACY_LABEL_ONLY"})
            out.append({"province":province["province_label"],"province_id":pid,
                "n_candidacies":len(rows),"lists":rows})
        if sum(x["n_candidacies"] for x in out)!=263:
            return {**stopped,"error":"TOTAL_MISMATCH"}
        return {**stopped,"ok":True,"source_url":d["source"],
            "source_document":"BOE-A-2023-15066","original_sha256":SOURCE_SHA,
            "year":2023,"coverage":"25 of 52 distinct provincial sections accepted; other 27 unresolved",
            "n_provinces":len(out),"n_candidacies":263,"detected_provincial_sections":52,
            "unresolved_provincial_sections":52-len(out),
            "issues_count":len(d["issues"]),"provinces":out,
            "warning":"Electoral candidacies ≠ legal parties, affiliations, seats or people. 27 sections unresolved."}
    except (OSError,KeyError,ValueError,TypeError,AttributeError,OverflowError):
        return {**stopped,"error":"INVALID_SOURCE"}

if __name__=="__main__":
    print(json.dumps(status(),ensure_ascii=False))
