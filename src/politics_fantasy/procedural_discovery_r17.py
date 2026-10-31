"""R17: SHA-pinned official descriptions of confidential register-first systems.

The OAAF obligation to maintain ALL external complaints is not a publicly
accessible, licensed, independently counted frame. AIPI and AVAF channels
are disjoint from OAAF and from the R16 transparency/complaint sources.
Never fetch URLs, accept terms, open cases or promote case outcomes here.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlsplit

from .procedural_index_contract import utc


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data/source_manifests/r17_confidential_all_received_documentary_redacted_20261031.json"
PIN = "65df140b921930d4860aca3ea51514fb223ff24d7f6a2a572a8fcd33d90160fe"
SAFE_BY = datetime(2026, 11, 1, tzinfo=timezone.utc)
MATRIX_SHA = "f656ccbb30d60e3e18c01d2c67a250fb83551923646cdc54628ca22102890de4"
RECEIPT_SHA = "1dd831b0aca2c5a3e31ad38c0e661453477fe9206217c12f9b840facc31e4d10"
FREEZE_SHA = "8ec4c7de3c556bf6ccfe19ee32cf9930f167fee8ac7c7449e595047df2567b12"

ROOT_KEYS = {
    "schema", "documentary_audit_day", "source_private_matrix_sha256",
    "source_private_receipt_sha256", "source_pretest_freeze_sha256",
    "documentary_only", "real_source_originals_acquired",
    "real_case_records_or_outcomes_inspected", "scientific_AB_cycles",
    "terms_or_cookies_accepted", "independent_all_received_denominator",
    "historical_first_public_at_by_case", "real_original_vintage_pairs",
    "verified_cross_institution_links", "nonadditive_documentary_routes",
}
ROUTE_KEYS = {
    "source_id", "institution", "documentary_unit", "procedural_stage_limit",
    "official_primary_url", "official_secondary_url", "legal_rights_scope",
    "terms_by_mere_access_status", "legal_channel_or_regime_break",
    "confidential_internal_all_received_registry_required",
    "public_preclassification_register_certified", "distribution_rights_certified",
    "case_originals_acquired", "independent_same_scope_denominator",
    "positive_negative_pending_censoring_states", "official_dual_id_crosswalk",
    "historical_case_first_public_at",
}
ALLOWED = {
    "R17_OAAF_ANDALUCIA_EXTERNAL_FRAUD": (
        "Oficina Andaluza contra el Fraude y la Corrupción",
        "EXTERNAL_COMPLAINT_RECEIVED_BEFORE_ADMISSION",
        "CONFIDENTIAL_ALL_RECEIVED_INTERNAL_REGISTER_MANDATED_NOT_PUBLIC_REGISTER",
        "www.juntadeandalucia.es", "www.juntadeandalucia.es",
        True, "UNVERIFIED_FOR_EACH_DISTRIBUTION",
    ),
    "R17_AIPI_NATIONAL_EXTERNAL_CHANNEL": (
        "Autoridad Independiente de Protección del Informante, A.A.I.",
        "EXTERNAL_CHANNEL_COMMUNICATION_REGISTERED_BEFORE_INITIAL_DECISION",
        "PROCEDURAL_REGISTRATION_WITH_TRACKING_CODE_NOT_PUBLIC_ALL_RECEIVED_CASE_REGISTER",
        "www.proteccioninformante.gob.es", "www.proteccioninformante.gob.es",
        None, "INDEXED_PORTAL_NOTICE_BINDING; DO_NOT_VISIT_OR_ACCEPT_FOR_ACQUISITION",
    ),
    "R17_AVAF_VALENCIAN_ANTIFRAUD": (
        "Agencia Valenciana Antifraude",
        "MULTICHANNEL_COMPLAINT_PRESENTED_BEFORE_EX_OFFICIO_INVESTIGATION",
        "PRESENTED_COMPLAINT_NOT_AUTOMATIC_INVESTIGATION_CASE_OR_CENSUS",
        "www.antifraucv.es", "www.boe.es",
        None, "UNVERIFIED_FOR_EACH_DISTRIBUTION",
    ),
}


def _no_duplicates(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError("R17_DUPLICATE_JSON_KEY")
        out[k] = v
    return out


def _public_official_url(raw: str, host: str) -> bool:
    if type(raw) is not str or len(raw) > 1500:
        return False
    try:
        u = urlsplit(raw)
        return (u.scheme == "https" and u.hostname == host and
                not u.username and not u.password and not u.port and
                not u.query and not u.fragment)
    except ValueError:
        return False


def _load(path: Path) -> list[dict]:
    if (path.is_symlink() or not path.is_file() or
            not 1400 < path.stat().st_size < 13000):
        raise ValueError("R17_MANIFEST_ABSENT_OR_OVERSIZED")
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != PIN:
        raise ValueError("R17_MANIFEST_SHA_UNREVIEWED")
    doc = json.loads(raw.decode("utf-8"),object_pairs_hook=_no_duplicates,
                     parse_constant=lambda x: (_ for _ in ()).throw(
                         ValueError("R17_NONFINITE_JSON")))
    if (type(doc) is not dict or set(doc) != ROOT_KEYS
            or doc["schema"] != "pfl.r17.confidential_registration_documentary.v1"
            or doc["documentary_audit_day"] != "2026-10-31"
            or doc["source_private_matrix_sha256"] != MATRIX_SHA
            or doc["source_private_receipt_sha256"] != RECEIPT_SHA
            or doc["source_pretest_freeze_sha256"] != FREEZE_SHA
            or doc["documentary_only"] is not True
            or doc["terms_or_cookies_accepted"] is not False
            or any(type(doc[k]) is not int or doc[k] != 0 for k in (
                "real_source_originals_acquired", "real_case_records_or_outcomes_inspected",
                "scientific_AB_cycles", "real_original_vintage_pairs",
                "verified_cross_institution_links"))
            or any(doc[k] is not None for k in (
                "independent_all_received_denominator",
                "historical_first_public_at_by_case"))):
        raise ValueError("R17_EMPIRICAL_OR_RIGHTS_PROMOTION")
    rows = doc["nonadditive_documentary_routes"]
    if (type(rows) is not list or len(rows) != 3
            or any(type(r) is not dict or set(r) != ROUTE_KEYS for r in rows)
            or {r["source_id"] for r in rows} != set(ALLOWED)):
        raise ValueError("R17_THREE_DISTINCT_INSTITUTIONS_REQUIRED")
    result = []
    for row in rows:
        institution, unit, limit, primary, secondary, mandatory, rights = ALLOWED[row["source_id"]]
        if ((row["institution"], row["documentary_unit"],
             row["procedural_stage_limit"],
             row["confidential_internal_all_received_registry_required"],
             row["terms_by_mere_access_status"])
                != (institution, unit, limit, mandatory, rights)):
            raise ValueError("R17_LEGAL_STAGE_OR_JURISDICTION_DRIFT")
        if (not _public_official_url(row["official_primary_url"], primary)
                or not _public_official_url(row["official_secondary_url"], secondary)):
            raise ValueError("R17_DOCUMENTARY_URL_NOT_WHITELISTED")
        if (row["public_preclassification_register_certified"] is not False
                or row["distribution_rights_certified"] is not False
                or type(row["case_originals_acquired"]) is not int
                or row["case_originals_acquired"] != 0
                or any(row[k] is not None for k in (
                    "independent_same_scope_denominator",
                    "positive_negative_pending_censoring_states",
                    "official_dual_id_crosswalk", "historical_case_first_public_at"))
                or any(type(row[k]) is not str or len(row[k]) > 400 for k in (
                    "legal_rights_scope", "legal_channel_or_regime_break"))):
            raise ValueError("R17_UNATTESTED_CASE_OR_RIGHTS_PROMOTION")
        result.append({
            "source_id": row["source_id"], "institution": institution,
            "documentary_unit": unit, "limitation": limit,
            "rights_scope": row["legal_rights_scope"],
            "terms_by_mere_access_status": rights,
            "legal_regime_break": row["legal_channel_or_regime_break"],
            "confidential_internal_register_mandated": mandatory,
            "public_registry_available": False,
            "source_originals_acquired": 0,
            "distribution_rights_certified": False,
            "independent_entry_denominator": None,
            "real_terminal_decisions": None,
            "real_pending_or_censored": None,
            "first_public_at": None,
            "official_dual_id_crosswalk": None,
            "source_role_is_not_a_homogeneous_risk_set": True,
        })
    return result


def status(*, as_of: str | None = None, path: Path | None = None) -> dict:
    cut = utc(as_of) if as_of is not None else datetime.now(timezone.utc)
    base = {
        "schema": "pfl.r17.confidential_documentary_source_status.v1",
        "as_of": as_of, "scientific_cycles": 0,
        "real_denominator": None, "real_pending_or_censoring": None,
        "real_case_outcomes": None, "historical_first_public_at": None,
        "source_groups_additive": False, "case_download_rights": False,
        "public_register_coverage_verified": False,
    }
    hidden = {"source_rows": [], "documentary_source_count": None,
              "manifest_sha256": None, "documentary_safe_by": None}
    if cut < SAFE_BY:
        return {**base, **hidden, "status": "R17_NOT_KNOWN_AT_CUT"}
    try:
        rows = _load(path or MANIFEST)
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return {**base, **hidden, "status": "R17_MANIFEST_QUARANTINED"}
    return {
        **base, "status": "R17_DOCUMENTARY_ONLY_CONFIDENTIAL_NO_CASE_COHORT",
        "source_rows": rows, "documentary_source_count": len(rows),
        "manifest_sha256": PIN, "documentary_safe_by": SAFE_BY.isoformat(),
    }
