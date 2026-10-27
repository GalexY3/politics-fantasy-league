"""Fail-closed claim-type and as-of gate. AB-H RC07 experimental pure module.

This checks a *trusted registry entry*. It cannot authenticate that a caller actually
supplied a server-owned, independently attested registry; do not expose registry
or call it with untrusted client data. This is NOT live political identity scoring.
"""
from __future__ import annotations
from collections.abc import Mapping
from datetime import datetime, timezone

AUTHORIZED_CLAIMS = {
    'NOMINATED_AND_ACCEPTED_CANDIDATES': 'BOCCL_CANDIDATE_ACCEPTANCE',
    'DESIGNATED_SENATORS': 'BOCCL_PLENARY_DESIGNATION',
}
AUTHORITY = 'Cortes de Castilla y Leon'


def _aware_time(raw: str) -> datetime | None:
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        date = datetime.fromisoformat(raw.strip().replace('Z', '+00:00'))
    except ValueError:
        return None
    if date.tzinfo is None or date.utcoffset() is None:
        return None
    return date.astimezone(timezone.utc)


def evaluate_claim_as_of(*, authority: str, record_family: str,
                         evidence_ref: str, desired_claim: str, as_of: str,
                         trusted_registry: Mapping | None) -> dict:
    """Return auditable denial or local eligibility; not publisher signature validation.

    `trusted_registry` must be server-owned and independently verified. The
    application MUST NOT allow API callers to set its contents.
    `first_public_at` is required in the registry as timezone-aware ISO 8601.
    Signing, act, bulletin and effective dates cannot substitute for this field.
    """
    def deny(reason: str) -> dict:
        return {'eligible': False, 'reason': reason, 'release_grade': False}
    cutoff = _aware_time(as_of)
    if cutoff is None:
        return deny('INVALID_AS_OF')
    if not isinstance(authority, str) or authority != AUTHORITY:
        return deny('UNSUPPORTED_AUTHORITY')
    if desired_claim not in AUTHORIZED_CLAIMS:
        return deny('UNSUPPORTED_CLAIM')
    if record_family not in set(AUTHORIZED_CLAIMS.values()):
        return deny('UNSUPPORTED_RECORD_FAMILY')
    if record_family != AUTHORIZED_CLAIMS[desired_claim]:
        return deny('ASSERTION_TYPE_MISMATCH')
    if not isinstance(evidence_ref, str) or not evidence_ref.strip():
        return deny('MISSING_REFERENCE')
    if not isinstance(trusted_registry, Mapping):
        return deny('NO_TRUSTED_REGISTRY')
    entry = trusted_registry.get(evidence_ref)
    if not isinstance(entry, Mapping):
        return deny('NO_ATTESTED_ENTRY')
    if (entry.get('authority') != authority or
        entry.get('record_family') != record_family or
        entry.get('evidence_ref') != evidence_ref):
        return deny('RECORD_ATTESTATION_MISMATCH')
    first = _aware_time(entry.get('first_public_at'))
    if first is None:
        return deny('FIRST_PUBLIC_AT_UNVERIFIED')
    if first > cutoff:
        return deny('NOT_PUBLIC_BY_CUTOFF')
    return {'eligible': True,
            'reason': 'ELIGIBLE_ONLY_IF_REGISTRY_TRUSTED_AND_TIMESTAMP_INDEPENDENTLY_VERIFIED',
            'release_grade': False}
