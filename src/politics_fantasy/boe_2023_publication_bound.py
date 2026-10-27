"""2023 ordinary BOE documentary-availability *conditional* bound; no person scoring.

Publisher 2023 annual report says all 312 ordinary issues were published before
08:00 issue-day. RD 181/2008 art. 11 requires same-day accessibility absent
extraordinary technical problems. This registry covers only two signed PDF
originals independently inspected locally, not arbitrary client material.
Neither a PDF signing date nor this policy yields exact first_public_at.
"""
from datetime import datetime, timedelta, time
from types import MappingProxyType
from zoneinfo import ZoneInfo

_DOCS = MappingProxyType({
    'BOE-A-2023-15066': ('2023-06-27', 'd1c179fcfab9889df272753ad3d44513f86cec703805219834b7d048ef0eda20'),
    'BOE-A-2023-18907': ('2023-09-01', 'f2146cfbf00d2b6eb6f8dd0dcdebc1e10298019589b2254e244e0ebc513d2f8a'),
})


def assess_boe_2023_document(*, document_id: str, as_of: str) -> dict:
    """Return documentary-only eligibility under a specified publication assumption.

    This method does not authenticate request data; document hash/type must be
    verified against the original by a separate server-side ingestion process.
    """
    def deny(reason):
        return {'available_under_assumption': False, 'reason': reason,
                'first_public_at': None, 'real_person_scoring': False, 'release_grade': False}
    if not isinstance(document_id, str) or document_id not in _DOCS:
        return deny('UNKNOWN_OR_UNVERIFIED_DOCUMENT')
    try:
        dt = datetime.fromisoformat(as_of.replace('Z', '+00:00')) if isinstance(as_of, str) else None
    except ValueError:
        dt = None
    if dt is None or dt.tzinfo is None or dt.utcoffset() is None:
        return deny('INVALID_AS_OF_TIMESTAMP')
    issue_day, source_sha = _DOCS[document_id]
    bound = datetime.combine(datetime.fromisoformat(issue_day).date() + timedelta(days=1),
                             time.min, tzinfo=ZoneInfo('Europe/Madrid'))
    if dt < bound:
        return deny('BEFORE_CONSERVATIVE_ISSUE_DAY_BOUND')
    return {'available_under_assumption': True,
            'reason': 'PUBLISHER_2023_ORDINARY_ISSUE_SELF_REPORT_AND_RD181_ART11',
            'issuer_issue_day': issue_day, 'available_by_policy': bound.isoformat(),
            'pdf_sha256_reference': source_sha,
            'first_public_at': None, 'per_file_archive_capture_at': None,
            'publisher_signature_integrity_checked_locally': True,
            'publisher_certificate_trust_long_term_proven': False,
            'original_historical_web_timestamp_witnessed': False,
            'scope': 'BOE_2023_ORDINARY_DOCUMENTARY_ONLY',
            'real_person_scoring': False, 'release_grade': False}
