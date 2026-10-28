"""Institutional source references; deliberately NOT a canonical person-ID system.
Source: AB20B C17 unmerged branch (identical behavior, imported for limited local use).
"""
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class InstitutionalRef:
    authority: str
    legislature: str
    record_family: str
    local_reference: str

    def __post_init__(self):
        if not all(isinstance(v, str) and v.strip() for v in (
            self.authority, self.legislature, self.record_family, self.local_reference
        )):
            raise ValueError("complete source namespace required")

    @property
    def key(self):
        return (self.authority, self.legislature, self.record_family, self.local_reference)


def same_institutional_record(a: InstitutionalRef, b: InstitutionalRef) -> bool:
    return a.key == b.key


def certify_same_person(a: InstitutionalRef, b: InstitutionalRef, *,
                        attested_crosswalk: Optional[object] = None) -> bool:
    # No audited server-owned person crosswalk exists.
    # Caller claims and name equality are NOT official proof.
    return False


def scoring_enabled(*refs: InstitutionalRef) -> bool:
    return False
