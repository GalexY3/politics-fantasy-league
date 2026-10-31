"""R15 adversarial *synthetic* knowledge-bound model for documentary facts.

Four clocks must not collapse:
event / document / publisher edition / local discovery and capture.
An independent historical public witness is a separate fifth question.  No
timestamp in this synthetic module, even a third-party hostname or an
editorial restore label, can authenticate first_public_at or R5.

This module accepts only SYNTHETIC IDs and no source or case data. It is
intended for regression, threat-modeling and preregistered future parsers.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re

from .procedural_index_contract import GateError, utc

SYN = re.compile(r"SYNTHETIC:[A-Z0-9_:-]{1,110}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
MAX_CLAIMS = 200
TYPES = {"CATALOGUE_RESTORE_METADATA", "CATALOGUE_ENTRY",
         "REGISTRATION_FRAME_ASSERTION", "EXTERNAL_COUNT_ASSERTION",
         "INDEPENDENT_ARCHIVE_INDEX_CANDIDATE"}


def _syn(x: str) -> bool:
    return isinstance(x, str) and bool(SYN.fullmatch(x))


@dataclass(frozen=True)
class KnowledgeInterval:
    """An observation was first *detected* sometime in this interval.

    If the upper bound is unknown, no historical replay can show it.  An
    imprecise day observed_on should use [day 00:00, next day 00:00] UTC.
    """
    observed_not_before: str | None
    observed_no_later_than: str | None

    def __post_init__(self) -> None:
        if (self.observed_not_before is None) != (self.observed_no_later_than is None):
            raise GateError("UNBOUNDED_DISCOVERY_INTERVAL")
        if self.observed_no_later_than is not None and (
                utc(self.observed_not_before) > utc(self.observed_no_later_than)):
            raise GateError("REVERSED_DISCOVERY_INTERVAL")

    def upper(self) -> datetime | None:
        return utc(self.observed_no_later_than) if self.observed_no_later_than else None


@dataclass(frozen=True)
class DocumentaryClaim:
    claim_id: str
    source_id: str
    dataset_id: str
    claim_type: str
    discovered: KnowledgeInterval
    captured_at: str | None
    event_at: str | None = None
    document_dated_at: str | None = None
    publisher_edition_at: str | None = None
    publisher_backend: str | None = None
    claimed_original_sha256: str | None = None
    original_verified: bool = False
    first_public_at: None = None

    def __post_init__(self) -> None:
        if (not all(_syn(s) for s in (
                self.claim_id, self.source_id, self.dataset_id))
                or self.claim_type not in TYPES
                or not isinstance(self.discovered, KnowledgeInterval)
                or self.publisher_backend is not None and not _syn(self.publisher_backend)
                or self.claimed_original_sha256 is not None
                and (not isinstance(self.claimed_original_sha256,str)
                     or not SHA.fullmatch(self.claimed_original_sha256))
                or self.original_verified is not False
                or self.first_public_at is not None):
            raise GateError("SYNTHETIC_DOCUMENTARY_CLAIM_ONLY")
        for x in (self.captured_at, self.event_at, self.document_dated_at,
                  self.publisher_edition_at):
            if x is not None:
                utc(x)
        # A day-precision discovery interval may legitimately contain an
        # exact capture (e.g. captured 23:15 but conservatively discoverable
        # only after that day's midnight). Reject capture *before the lower*
        # bound; do not reject a capture within the interval.
        if (self.captured_at is not None
                and self.discovered.observed_not_before is not None
                and utc(self.captured_at) < utc(self.discovered.observed_not_before)):
            raise GateError("CAPTURE_PRECEDES_START_OF_DISCOVERY_WINDOW")

    def visible_on(self, as_of: datetime) -> bool:
        high=self.discovered.upper()
        return (high is not None and self.captured_at is not None
                and as_of >= high and as_of >= utc(self.captured_at))


def audit_documentary_knowledge(*, claims: tuple[DocumentaryClaim,...],
                                as_of: str) -> dict:
    """No identity, SHA, count, diagnostic or exclusion before observation.

    Conflicts of *visible* claims quarantine a source; future contradictory
    metadata cannot contaminate an earlier cut. Repeated claims with the same
    ID are never taken as independent archival witnesses.
    """
    cut=utc(as_of)
    if (type(claims) is not tuple or len(claims)>MAX_CLAIMS
            or any(not isinstance(c, DocumentaryClaim) for c in claims)):
        raise GateError("BAD_DOCUMENTARY_WITNESS_COLLECTION")
    visible=[c for c in claims if c.visible_on(cut)]
    base={
        "schema": "pfl.synthetic_documentary_knowledge_v1",
        "synthetic_only": True,
        "scientific_cycles": 0,
        "R5_passed": False,
        "all_received_denominator": None,
        "real_pending": None,
        "real_terminal": None,
        "right_censoring": None,
        "first_public_at": None,
        "originals_verified": False,
        "comparable_historical_original_pairs": None,
        "independent_archive_certified": False,
        "official_cross_links_admitted": False,
        "source_count_additive": False,
    }
    hidden={
        "visible_claim_count": None, "visible_sources_count": None,
        "visible_restore_labels_count": None,
        "same_dataset_restore_labels": None,
        "duplicate_or_conflicting_claims": None,
        "claim_original_sha256": None,
    }
    if not visible:
        return {**base, **hidden, "status":"NO_DOCUMENTARY_KNOWLEDGE_AT_CUT"}
    by_id={}
    for c in visible:
        # One identical claim is a replay, not another independent witness.
        if c.claim_id in by_id:
            if c != by_id[c.claim_id]:
                return {**base,**hidden,"status":"VISIBLE_DOCUMENTARY_CLAIMS_QUARANTINED"}
            continue
        by_id[c.claim_id]=c
    unique=list(by_id.values())
    # Same published claim ID should never point to two sources or datasets
    # at once. If the more recent conflicting observation is unseen, it
    # must not change the old snapshot (checked above).
    restores=[c for c in unique if c.claim_type=="CATALOGUE_RESTORE_METADATA"]
    # Two alleged source versions are not two source-original SHA-vintages.
    return {
        **base, "status":"DOCUMENTARY_ASSERTIONS_VISIBLE_NOT_EMPIRICAL",
        "visible_claim_count":len(unique),
        "visible_sources_count":len({c.source_id for c in unique}),
        "visible_restore_labels_count":len(restores),
        "same_dataset_restore_labels": (
            len({(c.source_id,c.dataset_id) for c in restores})==1 if restores
            else None),
        "duplicate_or_conflicting_claims":False,
        "claim_original_sha256":None,
    }
