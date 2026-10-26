"""Provenance/quality accounting for the original 2023 BOE nomination atlas.

Separates documentary extraction coverage from legal-party coverage and
refuses to promote quarantined labels to eligible lists.
"""
from __future__ import annotations
import json
from pathlib import Path
from .nomination_atlas import DEFAULT, SOURCE_SHA

def audit(path: Path|None=None)->dict:
    p=Path(path) if path is not None else DEFAULT
    stop={"ok":False,"current_registered_parties":None,"public_people_confirmed":0,
          "eligible_real_people_for_fantasy":0,"percentage_of_spanish_parties":None}
    try:
        if not p.is_file() or p.stat().st_size>350_000:
            return {**stop,"error":"MISSING_OR_OVERSIZED"}
        x=json.loads(p.read_text(encoding="utf8"))
        if x.get("original_sha256")!=SOURCE_SHA or x.get("no_person_names_in_export") is not True:
            return {**stop,"error":"PROVENANCE_NOT_ACCEPTED"}
        provinces=x["provinces"]
        issues=x["issues"]
        if (len(provinces)!=25 or x["province_sections_detected"]!=52 or
            x["province_sections_parsed"]!=25 or sum(v["congress_candidacies"] for v in provinces)!=263):
            return {**stop,"error":"APPROVED_COUNTS_MISMATCH"}
        issue_n={t["province"] for t in issues if t["code"]=="CONTAINS_NON_PROCLAMATION_NOTICE_REVIEW"}
        accepted_ids={v["province_id"] for v in provinces}
        if len(accepted_ids)!=25 or len(issue_n)!=9:
            return {**stop,"error":"REVIEW_STRUCTURE_MISMATCH"}
        clean=sum(v["province_label"] not in issue_n for v in provinces)
        q=x.get("quarantined_provinces")
        if q is None:
            return {**stop,"error":"QUARANTINE_NOT_YET_CAPTURED","clean_sections":clean,
                    "review_notice_sections":len(issue_n)}
        if len(q)!=27 or len({t["province_id"] for t in q})!=27:
            return {**stop,"error":"QUARANTINE_INCOMPLETE"}
        if accepted_ids.intersection(t["province_id"] for t in q):
            return {**stop,"error":"QUARANTINE_ACCEPTED_OVERLAP"}
        nobs=0
        for v in q:
            rows=v.get("observed_labels_only",[])
            ids=v.get("observed_positions",[])
            if (v.get("quality_status")!="UNRESOLVED_NON_SEQUENTIAL" or
                v.get("not_a_complete_candidacy_list") is not True or
                not isinstance(rows,list) or len(rows)!=v.get("observed_list_headings") or
                [t.get("position") for t in rows]!=ids or
                not v.get("missing_ordinal_positions")):
                return {**stop,"error":"QUARANTINE_CANNOT_BE_CERTIFIED"}
            if any(t.get("legal_party_registration_id") is not None
                   or t.get("person_count_joined")!=0 for t in rows):
                return {**stop,"error":"PRIVATE_OR_LEGAL_IDENTITY_IN_SOURCE"}
            nobs+=len(rows)
        if nobs!=x["quarantined_observed_list_headings"]:
            return {**stop,"error":"QUARANTINE_COUNT_MISMATCH"}
        return {**stop,"ok":True,"document":"BOE-A-2023-15066",
            "source_sha256":SOURCE_SHA,
            "original_election":"2023-07-23",
            "documentary_sections":52,
            "accepted_headings":25,"accepted_list_records":263,
            "accepted_without_known_notice":clean,
            "accepted_with_review_notice":len(issue_n),
            "quarantined_provinces":27,
            "observed_but_noncertified_list_headings":nobs,
            "eligible_inferred_party_identities":0,
            "legal_entity_data_available":False,
            "national_population_coverage_pct":None,
            "warning":"25+27 is coverage of this BOE document's sections, NOT of all Spanish political actors or parties. A strict list must not imply party affiliation."}
    except (OSError,KeyError,ValueError,TypeError,AttributeError,OverflowError):
        return {**stop,"error":"MALFORMED_SOURCE"}
