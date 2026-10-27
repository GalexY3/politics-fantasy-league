"""Audit competing official date-of-birth assertions without deciding personal identity.

Source-family grouping is editorial lineage, NOT statistical independence. This
function does not authenticate the source, validate a civil registry record,
or infer same/different persons. No person scoring or public release.
"""
from datetime import date
from collections import defaultdict


def audit_birth_assertions(assertions):
    if not isinstance(assertions, (tuple, list)) or not assertions:
        raise ValueError('ASSERTIONS_REQUIRED')
    refs = set()
    families = defaultdict(set)
    for row in assertions:
        if not isinstance(row, dict) or set(row) != {'source_ref','publisher_lineage','birth_day'}:
            raise ValueError('INVALID_ASSERTION_SCHEMA')
        ref, family, value = row['source_ref'], row['publisher_lineage'], row['birth_day']
        if not isinstance(ref, str) or not ref or ref in refs:
            raise ValueError('INVALID_OR_DUPLICATE_SOURCE_REF')
        if not isinstance(family, str) or not family.strip():
            raise ValueError('UNKNOWN_PUBLISHER_LINEAGE')
        if not isinstance(value, str) or len(value) != 10 or value[4] != '-' or value[7] != '-':
            raise ValueError('INVALID_BIRTH_DAY')
        try:
            if date.fromisoformat(value).isoformat() != value:
                raise ValueError('INVALID_BIRTH_DAY')
        except ValueError as exc:
            raise ValueError('INVALID_BIRTH_DAY') from exc
        refs.add(ref)
        families[family].add(value)
    all_values = sorted(set.union(*families.values()))
    return {
        'has_conflict': len(all_values) > 1,
        'observed_values': all_values,
        'documents_recorded': len(assertions),
        'publisher_lineages': len(families),
        'publisher_lineage_assertions': {f: sorted(v) for f, v in sorted(families.items())},
        'requires_source_review': len(all_values) > 1,
        'same_person_certified': False,
        'different_person_certified': False,
        'person_link_automatically_resolved': False,
        'first_public_at': None,
        'real_person_scoring': False,
        'release_grade': False,
    }
