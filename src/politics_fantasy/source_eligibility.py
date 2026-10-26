"""Fail-closed explanations for evidence eligibility in the local PFL demonstrator.

This is a documentary gate, not a source-authentication service or a score
engine. It deliberately never awards points to real-world people.
"""
from __future__ import annotations

import re
from collections.abc import Mapping

HTTPS_OFFICIAL = ("www.congreso.es", "www.boe.es")
HEX_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
ALLOWED_SCOPES = {"AGGREGATE", "CANDIDACY_LABEL", "PERSON_EVENT"}

def assess_evidence(record: object) -> dict:
    """Evaluate an *untrusted* proposed source record, without accepting it.

    Caller-supplied booleans and digests cannot certify an official source.
    Real-person scoring is always disallowed, even with all flags asserted.
    """
    reasons: list[str] = []
    if not isinstance(record, Mapping):
        return {"status": "QUARANTINED", "reasons": ["BAD_SCHEMA"],
                "real_person_scoring": False, "release_ready": False}
    if set(record) - {"scope", "official_url", "raw_sha256", "sha_replayed",
                      "stable_person_id", "as_of_documented", "first_public_at",
                      "reuse_adjudicated"}:
        reasons.append("UNKNOWN_FIELDS")
    scope = record.get("scope")
    if not isinstance(scope, str) or scope not in ALLOWED_SCOPES:
        reasons.append("UNKNOWN_SCOPE")
    url = record.get("official_url")
    if not isinstance(url, str):
        reasons.append("UNVERIFIED_SOURCE_URL")
    else:
        from urllib.parse import urlsplit
        try:
            parsed = urlsplit(url)
            if (parsed.scheme != "https" or parsed.hostname not in HTTPS_OFFICIAL
                    or parsed.username is not None or parsed.password is not None
                    or parsed.port not in (None, 443)):
                reasons.append("UNVERIFIED_SOURCE_URL")
        except ValueError:
            reasons.append("UNVERIFIED_SOURCE_URL")
    raw_sha = record.get("raw_sha256")
    if not isinstance(raw_sha, str) or HEX_SHA256.fullmatch(raw_sha) is None:
        reasons.append("NO_REPLAYABLE_DIGEST")
    if record.get("sha_replayed") is not True:
        reasons.append("ORIGINAL_NOT_REPLAYED")
    if scope == "PERSON_EVENT":
        if record.get("stable_person_id") is not True:
            reasons.append("PERSON_ID_UNRESOLVED")
        if record.get("as_of_documented") is not True:
            reasons.append("TEMPORAL_PROVENANCE_INCOMPLETE")
        if record.get("first_public_at") is None:
            reasons.append("FIRST_PUBLIC_AT_UNKNOWN")
    if record.get("reuse_adjudicated") is not True:
        reasons.append("REUSE_RIGHTS_UNADJUDICATED")
    # No caller-controlled field can establish authenticity, legal rights, or a
    # scoring licence: these are *claims*, not independent attestation.
    if not reasons:
        reasons.append("CLAIMS_NOT_INDEPENDENTLY_ATTESTED")
    return {"status": "QUARANTINED", "reasons": reasons,
            "real_person_scoring": False, "release_ready": False}

def policy_status() -> dict:
    """Local display summary; no individual data and no writable receipts."""
    return {"mode": "LOCAL_DOCUMENTARY_DEMO", "policy_version": "PFL-ELIG-1",
            "real_person_scoring": False, "release_ready": False,
            "message": "Sources and political people are not score-eligible.",
            "requires": ["official original and provenance", "stable person identity",
                         "reproducible as-of date", "source-specific reuse review",
                         "server-owned trusted review", "all public launch gates"]}
