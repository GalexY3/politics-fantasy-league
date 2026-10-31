"""R14 scoped documentary metadata, never a certified procedural population.

Four new documentary routes remain non-additive; the SAIP evidence enriches
the *existing* R13 lead without counting it twice. Only a SHA-pinned, reviewed
redaction is read, not agent matrices or case/distribution originals.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlsplit

from .procedural_index_contract import utc

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data/source_manifests/r14_scoped_documentary_redacted_20261031.json"
PIN = "1a25b34117459fe5914293ca91701863ad02eefb1304be65528e9533e4df0c2a"
SAFE_BY = datetime(2026, 11, 1, tzinfo=timezone.utc)
MATRIX_SHAS = {
    "gencat_saip": "34a3b70f8fe75df54b3c5c4c8c7337c03af418d12c7afaacf111b0efddfd641a",
    "clm_aragon": "c1518477ded932d21dfef64f6f805afb8bbc3abb345b5d951221918e717be225",
}
RECEIPT_SHAS = {
    "gencat_saip": "38b3bbc1c4921312e9a64654b1d0de18ef6726a8ac303126477ee412dbdb0d32",
    "clm_aragon": "83923e40109789d62f09c58e9622525d3a92430d945a49a8acad84adf23d6396",
}
ALLOWED = {
    "CIUDADREAL_GENERAL_INCOMING_REGISTER": (
        "Ayuntamiento de Ciudad Real", "GENERAL_MUNICIPAL_REGISTER_ENTRY_ANY_SUBJECT",
        "NO_OFFICIAL_POLITICAL_CASE_FILTER_OR_REGISTER_TO_FILE_CROSSWALK",
        "CATALOGUE_REUSE_NOTICE_NOT_VERIFIED_DISTRIBUTION_RIGHTS",
        "gobiernoabierto.ciudadreal.es",
    ),
    "CLM_GENERAL_ACCESS_STATISTICS": (
        "Junta de Comunidades de Castilla-La Mancha", "GENERAL_ACCESS_REQUESTS_AGGREGATED_STATISTICS",
        "AGGREGATE_OR_OUTCOME_SELECTED_NOT_INITIAL_CASE_REGISTER",
        "GENERAL_TERMS_BIND_BY_USE_ASSET_LICENSE_UNVERIFIED",
        "datosabiertos.castillalamancha.es",
    ),
    "ARAGON_GENERAL_ACCESS_STATISTICS": (
        "Gobierno de Aragón", "ACCESS_REQUEST_REGISTER_LEGAL_RULE_AND_AGGREGATES",
        "STATUTORY_REGISTER_NOT_PUBLIC_COMPLETE_CASE_DISTRIBUTION",
        "OPEN_DATA_TERMS_BIND_ON_ACCESS_PDF_ASSET_RIGHTS_UNVERIFIED",
        "www.aragon.es",
    ),
    "CLM_ENVIRONMENTAL_ACCESS_STATISTICS": (
        "Junta de Comunidades de Castilla-La Mancha",
        "ENVIRONMENTAL_REQUESTS_ANNUAL_AGGREGATES_DIFFERENT_LEGAL_FAMILY",
        "ANNUAL_AGGREGATES_NOT_CASE_REGISTER_AND_NOT_GENERAL_AIP",
        "GENERAL_TERMS_BIND_BY_USE_ASSET_LICENSE_UNVERIFIED",
        "datosabiertos.castillalamancha.es",
    ),
}
ROOT_KEYS = {
    "schema", "local_documentary_audit_day", "source_private_matrix_sha256",
    "source_private_receipt_sha256", "documentary_only", "individual_case_originals_acquired",
    "case_outcomes_inspected", "terms_accepted", "AB_scientific_cycles",
    "all_received_denominator", "real_pending_or_censored_cases", "individual_first_public_at",
    "historical_original_vintage_pairs_verified", "case_cross_institutional_joins_verified",
    "existing_r13_saip_enrichment_not_new_cohort", "new_documentary_routes_not_new_cohorts",
}
ROW_KEYS = {
    "source_id", "institution", "documentary_unit", "limitation", "rights_scope",
    "official_catalogue_url", "source_originals_acquired", "independent_entry_denominator",
    "real_terminal_decisions", "real_pending_or_censored", "first_public_at",
}


def _unique_json(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError("R14_DUPLICATE_JSON_KEY")
        out[k] = v
    return out


def _validated(path: Path):
    if path.is_symlink() or not path.is_file() or not 1500 < path.stat().st_size < 13000:
        raise ValueError("R14_DOCUMENTARY_MANIFEST_MISSING")
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != PIN:
        raise ValueError("R14_MANIFEST_SHA_MISMATCH")
    d = json.loads(raw.decode("utf8"), object_pairs_hook=_unique_json)
    if (type(d) is not dict or set(d) != ROOT_KEYS
            or d["schema"] != "pfl.r14.documentary_nonadditive.v1"
            or d["local_documentary_audit_day"] != "2026-10-31"
            or d["source_private_matrix_sha256"] != MATRIX_SHAS
            or d["source_private_receipt_sha256"] != RECEIPT_SHAS
            or d["documentary_only"] is not True
            or d["terms_accepted"] is not False
            or any(type(d[k]) is not int or d[k] != 0 for k in (
                "individual_case_originals_acquired", "case_outcomes_inspected",
                "AB_scientific_cycles", "historical_original_vintage_pairs_verified",
                "case_cross_institutional_joins_verified"))
            or any(d[k] is not None for k in (
                "all_received_denominator", "real_pending_or_censored_cases",
                "individual_first_public_at"))):
        raise ValueError("R14_UNAUTHORIZED_EMPIRICAL_PROMOTION")
    e = d["existing_r13_saip_enrichment_not_new_cohort"]
    if (type(e) is not dict or set(e) != {
            "existing_source_id", "catalogue_id", "source_declared_columns",
            "column_names_visible_in_index", "column_names_not_verified",
            "approximate_index_row_count_not_denominator",
            "restore_point_metadata_entries_visible", "original_snapshots_compared",
            "first_public_at", "rights_by_csv_json_xml_and_restore_verified",
            "catalogue_variants_not_original_snapshots"}
            or e != {
                "existing_source_id": "GENCAT_SAIP_INITIAL_FILINGS",
                "catalogue_id": "yjpn-vcw8", "source_declared_columns": 35,
                "column_names_visible_in_index": 15, "column_names_not_verified": 20,
                "approximate_index_row_count_not_denominator": "23.4K",
                "restore_point_metadata_entries_visible": 2, "original_snapshots_compared": 0,
                "first_public_at": None, "rights_by_csv_json_xml_and_restore_verified": False,
                "catalogue_variants_not_original_snapshots": True}):
        raise ValueError("R14_SAIP_ENRICHMENT_NOT_ADMISSIBLE")
    rows = d["new_documentary_routes_not_new_cohorts"]
    if type(rows) is not list or len(rows) != 4 or {x.get("source_id") for x in rows} != set(ALLOWED):
        raise ValueError("R14_DOCUMENTARY_SCOPE_MISMATCH")
    result = []
    for r in rows:
        if type(r) is not dict or set(r) != ROW_KEYS:
            raise ValueError("R14_SOURCE_FIELDS_UNEXPECTED")
        unit = ALLOWED[r["source_id"]]
        if (tuple(r[k] for k in ("institution", "documentary_unit", "limitation", "rights_scope"))
                != unit[:4]):
            raise ValueError("R14_SOURCE_UNIT_DRIFT")
        u = urlsplit(r["official_catalogue_url"])
        if (u.scheme != "https" or u.hostname != unit[4]
                or u.username or u.password or u.port or u.fragment):
            raise ValueError("R14_UNTRUSTED_URL")
        if (type(r["source_originals_acquired"]) is not int
                or r["source_originals_acquired"] != 0
                or any(r[k] is not None for k in (
                    "independent_entry_denominator", "real_terminal_decisions",
                    "real_pending_or_censored", "first_public_at"))):
            raise ValueError("R14_SOURCE_OUTCOME_PROMOTION")
        result.append({
            "source_id": r["source_id"], "institution": r["institution"],
            "documentary_unit": r["documentary_unit"],
            "limitation": r["limitation"], "rights_scope": r["rights_scope"],
            "source_originals_acquired": 0, "independent_entry_denominator": None,
            "real_terminal_decisions": None, "real_pending_or_censored": None,
            "first_public_at": None})
    return result, e


def status(*, as_of: str | None = None, path: Path | None = None):
    cut = utc(as_of) if as_of is not None else datetime.now(timezone.utc)
    base = {
        "schema": "pfl.r14.documentary_discovery.v1", "as_of": as_of,
        "real_denominator": None, "real_terminal_outcomes": None,
        "real_censored_or_pending": None, "first_public_at": None,
        "real_original_vintage_pairs": None, "scientific_cycles": 0,
        "source_groups_additive": False,
    }
    hidden = {
        "new_documentary_routes_count": None, "source_rows": [],
        "existing_saip_enrichment": None, "manifest_sha256": None,
        "documentary_safe_by": None,
    }
    if cut < SAFE_BY:
        return {**base, **hidden, "status": "R14_NOT_KNOWN_AT_CUT"}
    try:
        rows, saip = _validated(path or MANIFEST)
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return {**base, **hidden, "status": "R14_SOURCE_QUARANTINED"}
    return {**base, "status": "R14_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED",
            "new_documentary_routes_count": len(rows), "source_rows": rows,
            "existing_saip_enrichment": saip, "manifest_sha256": PIN,
            "documentary_safe_by": SAFE_BY.isoformat()}
