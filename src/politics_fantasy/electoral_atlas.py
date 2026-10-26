"""Historical SECONDARY aggregate electoral options, not a registry of people or current parties.
Read only. No ranking, scores, political merits or inferred individual beliefs.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / "data/observatory/electoral_atlas_2023.json"
ALLOWED_STATUS = {"VOTES_WITHOUT_CONGRESS_SEAT", "CONGRESS_SEAT_RECORDED", "NO_VOTES_RECORDED"}


def atlas_status(path: Path | None = None) -> dict:
    p = DEFAULT if path is None else Path(path)
    blocked = {"ok": False, "dataset_class": "HISTORICAL_SECONDARY_AGGREGATE",
               "real_person_scores_enabled": False, "source_official_verified": False}
    if not p.is_file():
        return {**blocked, "error": "ATLAS_NOT_FOUND"}
    try:
        if p.stat().st_size > 250_000:
            return {**blocked, "error": "ATLAS_TOO_LARGE"}
        obj = json.loads(p.read_text(encoding="utf-8"))
        if (obj.get("dataset_class") != "HISTORICAL_SECONDARY_AGGREGATE"
                or obj.get("date") != "2023-07"
                or obj.get("verification") != "SECONDARY_SOURCE_ONLY"
                or not isinstance(obj.get("labels"), list)):
            return {**blocked, "error": "ATLAS_PROVENANCE_INVALID"}
        rows = obj["labels"]
        if (len(rows) == 0 or len(rows) > 500
                or any(not isinstance(x, dict) for x in rows)
                or len({x.get("id") for x in rows}) != len(rows)):
            return {**blocked, "error": "ATLAS_ROWS_INVALID"}
        for r in rows:
            if (not isinstance(r.get("name"), str) or not r["name"] or len(r["name"]) > 200
                    or not isinstance(r.get("votes"), int) or isinstance(r.get("votes"), bool)
                    or not isinstance(r.get("seats"), int) or isinstance(r.get("seats"), bool)
                    or r["votes"] < 0 or r["seats"] < 0
                    or r.get("seat_status") not in ALLOWED_STATUS
                    or (r["votes"] > 0 and r["seats"] == 0 and r["seat_status"] != "VOTES_WITHOUT_CONGRESS_SEAT")
                    or (r["seats"] > 0 and r["seat_status"] != "CONGRESS_SEAT_RECORDED")):
                return {**blocked, "error": "ATLAS_ROW_BAD"}
        audit = obj.get("documentary_audit", {})
        if audit and (audit.get("reference_original_pdf_bytes_verified") is not False
                or audit.get("metric_cells_matched") != 312
                or audit.get("districts_matched") != 52):
            return {**blocked, "error": "ATLAS_DOCUMENTARY_AUDIT_INVALID"}
        public = []
        for x in rows:
            link = x.get("official_coalition_acronym_link")
            if link is not None and (not isinstance(link, dict)
                    or link.get("matching_method") != "EXACT_UNIQUE_ACRONYM_NOT_LEGAL_IDENTITY"
                    or not isinstance(link.get("JEC_reference_id"), str)):
                return {**blocked, "error": "ATLAS_COALITION_LINK_INVALID"}
            public.append({"id":x["id"], "name":x["name"], "votes":x["votes"],
                           "seats":x["seats"], "seat_status":x["seat_status"],
                           "coalition_acronym_documented":link is not None,
                           "official_national_votes_documentarily_checked":
                               x.get("jec_table_iii_national_total_match") is True})
        public.sort(key=lambda x: x["name"].casefold())
        return {"ok": True, "year": 2023, "election": "Congreso, julio de 2023",
                "dataset_class": "HISTORICAL_SECONDARY_AGGREGATE",
                "source_official_verified": False,
                "real_person_scores_enabled": False,
                "source_url": obj["source_url"],
                "source_blob_sha": obj["source_blob_sha"],
                "electoral_labels": len(public),
                "labels_with_votes_no_congress_seat": sum(x["seat_status"] == "VOTES_WITHOUT_CONGRESS_SEAT" for x in public),
                "labels_with_congress_seat": sum(x["seat_status"] == "CONGRESS_SEAT_RECORDED" for x in public),
                "labels": public,
                "jec_documentary_check": {
                    "provinces": audit.get("districts_matched", 0),
                    "aggregate_comparisons": audit.get("metric_cells_matched", 0),
                    "pdf_original_bytes_certified": False,
                    "party_option_votes_checked": sum(
                        x["official_national_votes_documentarily_checked"] for x in public),
                    "official_coalition_acronyms_matched": sum(
                        x["coalition_acronym_documented"] for x in public)},
                "limitations": obj.get("limitations", [])}
    except (ValueError, OSError, UnicodeError, TypeError, KeyError):
        return {**blocked, "error": "ATLAS_DATA_INVALID"}
