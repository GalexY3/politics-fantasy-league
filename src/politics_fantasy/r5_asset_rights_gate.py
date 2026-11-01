"""Conservative R5 documentary gate for source/distribution rights.

Research instrumentation ONLY. All input is untrusted, including claims of
legal review. The output cannot grant ingestion, empirical research, scoring,
publication or reproduction rights. No network access or original data.
"""
from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import datetime, timezone
from urllib.parse import urlsplit


SHA = re.compile(r"[a-f0-9]{64}\Z")
PURPOSES = frozenset({
    "LOCAL_ACADEMIC_READ",
    "INTERNAL_DERIVATION",
    "PUBLIC_AGGREGATE_DISPLAY",
    "PUBLIC_ORIGINAL_REDISTRIBUTION",
})
RIGHTS_KINDS = frozenset({
    "PUBLISHER_ASSET_SPECIFIC",
    "PUBLISHER_CATALOGUE_GENERAL",
    "THIRD_PARTY_SUMMARY",
    "UNKNOWN",
})
TERMS = frozenset({"NOT_ESTABLISHED", "BIND_ON_ACCESS", "REQUIRE_CLICK", "PUBLISHER_OPEN_NOTICE"})
ALLOWED = frozenset({
    "distribution_id", "asset_url", "asset_sha256", "requested_purpose",
    "historical_as_of", "first_public_at", "rights",
})
RIGHTS_FIELDS = frozenset({
    "kind", "distribution_id", "asset_sha256", "covered_purposes",
    "notice_published_at", "terms_mode", "terms_reviewed_by_human",
    "rights_reviewed_by_human",
})


def _utc(value: object) -> datetime | None:
    if not isinstance(value, str) or "T" not in value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.astimezone(timezone.utc) if dt.tzinfo is not None and dt.utcoffset() is not None else None
    except ValueError:
        return None


def _https(url: object) -> bool:
    if not isinstance(url, str):
        return False
    try:
        parsed = urlsplit(url)
        return (parsed.scheme == "https" and bool(parsed.hostname)
                and parsed.username is None and parsed.password is None
                and parsed.port in (None, 443) and not parsed.fragment
                and parsed.path not in ("", "/"))
    except ValueError:
        return False


def assess_distribution_rights(record: object) -> dict:
    """Explain what remains unproven for a proposed exact asset and use.

    A syntactically complete and apparently permissive record still ends in
    BLOCKED: publisher authenticity and independent adjudication are absent.
    No caller-supplied token, signature or flag can override that.
    """
    reasons: list[str] = []
    if not isinstance(record, Mapping):
        return {"schema": "pfl.r5.asset_rights.v1", "status": "QUARANTINED",
                "reasons": ["BAD_SCHEMA"], "reuse_admitted": False,
                "empirical_r5_open": False, "independent_attestation": False}
    if set(record) - ALLOWED:
        reasons.append("UNKNOWN_ASSET_FIELDS")
    distribution_id = record.get("distribution_id")
    if not isinstance(distribution_id, str) or not distribution_id.strip() or len(distribution_id)>180:
        reasons.append("DISTRIBUTION_ID_UNKNOWN")
    if not _https(record.get("asset_url")):
        reasons.append("ASSET_URL_NOT_STRUCTURALLY_VALID")
    sha = record.get("asset_sha256")
    if not isinstance(sha, str) or not SHA.fullmatch(sha):
        reasons.append("ASSET_DIGEST_UNKNOWN")
    purpose = record.get("requested_purpose")
    if not isinstance(purpose, str) or purpose not in PURPOSES:
        reasons.append("PURPOSE_UNKNOWN")
    cut = _utc(record.get("historical_as_of"))
    if cut is None:
        reasons.append("KNOWLEDGE_CUT_INVALID")
    first_public = _utc(record.get("first_public_at"))
    if first_public is None:
        reasons.append("FIRST_PUBLIC_UNVERIFIED")
    elif cut is not None and first_public > cut:
        reasons.append("SOURCE_NOT_YET_PUBLIC_AT_CUT")

    rights = record.get("rights")
    if not isinstance(rights, Mapping):
        reasons.append("NO_DISTRIBUTION_RIGHTS_RECORD")
    else:
        if set(rights) - RIGHTS_FIELDS:
            reasons.append("UNKNOWN_RIGHTS_FIELDS")
        kind = rights.get("kind")
        if not isinstance(kind, str) or kind not in RIGHTS_KINDS:
            reasons.append("RIGHTS_NOTICE_KIND_INVALID")
        elif kind != "PUBLISHER_ASSET_SPECIFIC":
            reasons.append("GENERAL_OR_THIRD_PARTY_NOTICE_NOT_ASSET_PERMISSION")
        if rights.get("distribution_id") != distribution_id or not isinstance(distribution_id, str):
            reasons.append("RIGHTS_DISTRIBUTION_BINDING_MISMATCH")
        if rights.get("asset_sha256") != sha or not isinstance(sha, str):
            reasons.append("RIGHTS_VINTAGE_SHA_BINDING_MISMATCH")
        uses = rights.get("covered_purposes")
        if (not isinstance(uses, list) or not uses or
                any(not isinstance(u, str) or u not in PURPOSES for u in uses) or
                len(set(uses)) != len(uses)):
            reasons.append("COVERED_PURPOSES_INVALID")
        elif purpose not in uses:
            reasons.append("REQUESTED_USE_NOT_COVERED")
        rights_date = _utc(rights.get("notice_published_at"))
        if rights_date is None:
            reasons.append("RIGHTS_NOTICE_DATE_INVALID")
        elif cut is not None and rights_date > cut:
            reasons.append("RIGHTS_NOTICE_POSTDATES_KNOWLEDGE_CUT")
        terms_mode = rights.get("terms_mode")
        if not isinstance(terms_mode, str) or terms_mode not in TERMS:
            reasons.append("TERMS_MODE_UNKNOWN")
        elif terms_mode in {"BIND_ON_ACCESS", "REQUIRE_CLICK"}:
            reasons.append("TERMS_REQUIRE_SEPARATE_PRIOR_ACCESS_REVIEW")
        elif terms_mode == "NOT_ESTABLISHED":
            reasons.append("TERMS_NOT_ESTABLISHED")
        if rights.get("terms_reviewed_by_human") is not True:
            reasons.append("TERMS_REVIEW_NOT_ATTESTED")
        if rights.get("rights_reviewed_by_human") is not True:
            reasons.append("ASSET_REUSE_REVIEW_NOT_ATTESTED")
    # Crucially, source-supplied or analyst-supplied assertions are not a
    # witnessed publisher licence or permission to process protected data.
    reasons.append("INDEPENDENT_LEGAL_AND_PROVENANCE_ATTESTATION_ABSENT")
    return {"schema": "pfl.r5.asset_rights.v1",
            "status": "BLOCKED_R5" if reasons == ["INDEPENDENT_LEGAL_AND_PROVENANCE_ATTESTATION_ABSENT"] else "QUARANTINED",
            "reasons": reasons, "reuse_admitted": False,
            "empirical_r5_open": False, "independent_attestation": False}
