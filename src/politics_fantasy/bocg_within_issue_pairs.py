"""Match two mentions *within one BOCG issue*; never assert global identity.

The returned pairs are document mention alignments only. This module does not
validate publisher signatures, independently verify person identity or permit
person scoring. Duplicate/missing names fail closed.
"""
from collections import Counter
import unicodedata

ISSUES = {"BOCG-15-D-51", "BOCG-15-D-390"}
ISSUER = "Congreso de los Diputados"


def _key(name):
    if not isinstance(name, str) or not name.strip():
        raise ValueError("INVALID_SOURCE_NAME")
    norm = unicodedata.normalize("NFKD", name.casefold())
    return " ".join("".join(c for c in norm if c.isalnum() or c.isspace()).split())


def pair_within_bocg(*, issuer, bulletin_id, condition_names, credential_names):
    if issuer != ISSUER or bulletin_id not in ISSUES:
        raise ValueError("UNSUPPORTED_SOURCE_SCOPE")
    if not isinstance(condition_names, list) or not isinstance(credential_names, list):
        raise ValueError("INVALID_SOURCE_LISTS")
    if not condition_names or not credential_names:
        return _deny("EMPTY_SOURCE_MENTIONS")
    ca = [_key(x) for x in condition_names]
    cb = [_key(x) for x in credential_names]
    if len(ca) != len(set(ca)) or len(cb) != len(set(cb)):
        return _deny("AMBIGUOUS_REPEATED_NAME")
    if set(ca) != set(cb):
        return _deny("MISSING_OR_EXTRA_SOURCE_MENTION")
    index = {key: i for i, key in enumerate(ca)}
    return {
        "status": "SAME_DOCUMENT_MENTIONS_MATCHED",
        "paired_ordinals_condition_to_credential": [
            [index[k] + 1, j + 1] for j, k in enumerate(cb)
        ],
        "count": len(ca),
        "same_person_across_documents_certified": False,
        "real_person_scoring": False,
        "first_public_at": None,
        "release_grade": False,
    }


def _deny(reason):
    return {"status": reason, "paired_ordinals_condition_to_credential": [],
            "count": 0, "same_person_across_documents_certified": False,
            "real_person_scoring": False, "first_public_at": None,
            "release_grade": False}
