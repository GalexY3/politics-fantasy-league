"""Source-backed PUBLIC candidacy labels for one 2023 province only.

The BOE original was downloaded over institutional HTTPS in verified CI.
Only acronyms and aggregate proof: no person names, political profiles,
legal-party identities, or inference about private membership.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DEFAULT=ROOT/"data/observatory/boe_2023_albacete_verified.json"
SHA="d1c179fcfab9889df272753ad3d44513f86cec703805219834b7d048ef0eda20"
ACRONYMS=("PSOE","FO","PP","PACMA","PUM+J","SUMAR","VOX","RECORTES CERO")


def status(path: Path | None=None)->dict:
    p=Path(path) if path is not None else DEFAULT
    blocked={"ok":False,"dataset_class":"OFFICIAL_2023_SINGLE_PROVINCE_CANDIDACY_LIST_LABELS",
        "real_person_scoring":False,"verified_legal_parties":0,
        "named_people_exposed":0}
    try:
        if not p.is_file() or p.stat().st_size>20_000:
            return {**blocked,"error":"SOURCE_NOT_FOUND_OR_TOO_LARGE"}
        src=json.loads(p.read_text(encoding="utf8"))
        if (src.get("dataset_class")!=blocked["dataset_class"] or
            src.get("source_document")!="BOE-A-2023-15066" or
            src.get("original_sha256")!=SHA or
            src.get("scope",{}).get("province")!="Albacete" or
            src.get("scope",{}).get("chamber")!="Congreso de los Diputados" or
            src.get("verification",{}).get("legal_party_registry_checked") is not False):
            return {**blocked,"error":"SOURCE_PROVENANCE_INVALID"}
        rows=src.get("lists")
        if (not isinstance(rows,list) or len(rows)!=8 or
            tuple(x.get("acronym") for x in rows)!=ACRONYMS or
            any(x.get("entity_type")!="ELECTORAL_CANDIDACY_LABEL" or
                x.get("registered_party_id") is not None or
                x.get("named_person_count")!=0 for x in rows)):
            return {**blocked,"error":"SOURCE_ROWS_INVALID"}
        return {"ok":True,"dataset_class":blocked["dataset_class"],
            "source_document":src["source_document"],
            "source_url":src["source_url"],
            "source_sha256":src["original_sha256"],
            "published_on":src["publication_date"],
            "province":"Albacete","chamber":"Congreso",
            "proclaimed_candidacy_lists":8,
            "lists":[{"acronym":x["acronym"],"type":"ELECTORAL_CANDIDACY_NOT_LEGAL_PARTY"}
                    for x in rows],
            "people_joined":0,"verified_legal_parties":0,
            "real_person_scoring":False,
            "named_people_exposed":0,
            "status":"SOURCE_ORIGINAL_BOUNDED_TO_2023_ONE_PROVINCE"}
    except (OSError,KeyError,ValueError,TypeError,AttributeError):
        return {**blocked,"error":"INVALID_SOURCE"}
