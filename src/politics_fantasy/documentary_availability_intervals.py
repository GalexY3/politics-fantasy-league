"""Evidence-bounded publication timing for PFL, without invented first-public-at.

This *contract* is exercised on synthetic witnesses. Only a separately reviewed
server-owned registry may designate a real source as an archival witness.
Historical event and bulletin dates, HTTP Last-Modified and current retrieval
are NEVER acceptable witness bases of historical public availability.

Three clocks stay separate: valid event time, availability of a specific source
revision to the public, and local acquisition of that revision. Exact first
publication is seldom knowable; a bounded interval is not an exact date.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

from .procedural_index_contract import GateError, utc, day, SHA, ID

@dataclass(frozen=True)
class RevisionWitness:
    revision_id: str
    original_sha256: str
    captured_at: str
    captured_clock_precision: Literal["EXACT", "SECOND", "DATE"]
    claimed_event_on: str | None = None
    documentary_date: str | None = None
    witnessed_public_by: str | None = None
    positive_basis: str = "LOCAL_VERIFIED_CAPTURE"
    witnessed_not_public_before: str | None = None
    negative_basis: str | None = None
    independently_reviewed: bool = False
    exact_first_public_at: str | None = None
    source_evidence_class: Literal["SYNTHETIC_LAB", "REAL_LOCAL_CAPTURE_ONLY"] = "SYNTHETIC_LAB"

    def __post_init__(self):
        if not isinstance(self.revision_id, str) or not ID.fullmatch(self.revision_id):
            raise GateError("INVALID_REVISION_ID")
        if self.source_evidence_class not in {"SYNTHETIC_LAB", "REAL_LOCAL_CAPTURE_ONLY"}:
            raise GateError("UNSUPPORTED_REAL_EVIDENCE_CLASS")
        if (self.source_evidence_class=="SYNTHETIC_LAB"
                and not self.revision_id.startswith("SYNTHETIC:")):
            raise GateError("SYNTHETIC_WITNESS_NEEDS_LAB_NAMESPACE")
        if (self.source_evidence_class=="REAL_LOCAL_CAPTURE_ONLY"
                and (self.positive_basis != "LOCAL_VERIFIED_CAPTURE"
                     or self.witnessed_not_public_before is not None
                     or self.witnessed_public_by is not None
                     or self.independently_reviewed)):
            raise GateError("REAL_ARCHIVAL_EVIDENCE_REQUIRES_SEPARATE_TRUSTED_REGISTRY")
        if not isinstance(self.original_sha256, str) or not SHA.fullmatch(self.original_sha256):
            raise GateError("UNVERIFIED_ORIGINAL_SHA")
        cutoff=utc(self.captured_at)
        if self.captured_clock_precision not in {"EXACT", "SECOND", "DATE"}:
            raise GateError("BAD_CAPTURE_PRECISION")
        if self.claimed_event_on is not None:
            day(self.claimed_event_on)
        if self.documentary_date is not None:
            day(self.documentary_date)
        if self.positive_basis not in {
            "TRUSTED_ARCHIVE_REVISION_WITNESS", "LOCAL_VERIFIED_CAPTURE"
        }:
            raise GateError("UNSAFE_POSITIVE_WITNESS_BASIS")
        if (self.positive_basis == "TRUSTED_ARCHIVE_REVISION_WITNESS"
                and not self.independently_reviewed):
            raise GateError("ARCHIVAL_WITNESS_NOT_REVIEWED")
        if self.positive_basis == "LOCAL_VERIFIED_CAPTURE" and self.witnessed_public_by is not None:
            # Local retrieval by itself attests only successful local
            # observation, not when a revision first became public.
            raise GateError("CAPTURE_CANNOT_ATTEST_HISTORICAL_PUBLICATION")
        if self.positive_basis == "TRUSTED_ARCHIVE_REVISION_WITNESS":
            if self.witnessed_public_by is None:
                raise GateError("ARCHIVAL_WITNESS_MISSING_DATE")
            if utc(self.witnessed_public_by) > cutoff:
                raise GateError("WITNESS_POSTDATES_ITS_CAPTURE")
        if self.witnessed_not_public_before is not None:
            if (self.negative_basis != "TRUSTED_PREVIOUS_COMPLETE_INDEX_NEGATIVE_WITNESS"
                    or not self.independently_reviewed):
                raise GateError("NEGATIVE_WITNESS_NOT_COMPLETE_OR_REVIEWED")
            if utc(self.witnessed_not_public_before)>cutoff:
                raise GateError("NEGATIVE_OBSERVATION_AFTER_CAPTURE")
        elif self.negative_basis is not None:
            raise GateError("ORPHAN_NEGATIVE_WITNESS_BASIS")
        if self.exact_first_public_at is not None:
            # No current source type in this module supports a trusted
            # *exact first* moment. Exact publication belongs to a different
            # independently adjudicated source version registry.
            raise GateError("EXACT_FIRST_PUBLICATION_NOT_ESTABLISHED")
        low=self.lower_bound()
        high=self.public_upper_bound()
        if low is not None and high is not None and low>=high:
            raise GateError("INCONSISTENT_PUBLICATION_INTERVAL")

    def capture_known_safe_by(self) -> datetime:
        stamp=utc(self.captured_at)
        if self.captured_clock_precision == "DATE":
            return (stamp.replace(hour=0,minute=0,second=0,microsecond=0)
                    + timedelta(days=1))
        if self.captured_clock_precision == "SECOND":
            return stamp.replace(microsecond=0) + timedelta(seconds=1)
        return stamp

    def public_upper_bound(self) -> datetime | None:
        if self.positive_basis == "TRUSTED_ARCHIVE_REVISION_WITNESS":
            return utc(self.witnessed_public_by)
        return None

    def lower_bound(self) -> datetime | None:
        return (utc(self.witnessed_not_public_before)
                if self.witnessed_not_public_before is not None else None)

    def temporal_report(self, *, as_of: str, purpose: Literal["LOCAL_OBSERVATORY", "HISTORICAL_PUBLIC_PREDICTOR"]) -> dict:
        """NO evidence that a document was new at an observed event date."""
        t=utc(as_of)
        if purpose not in {"LOCAL_OBSERVATORY", "HISTORICAL_PUBLIC_PREDICTOR"}:
            raise GateError("INVALID_TEMPORAL_PURPOSE")
        safe_capture=self.capture_known_safe_by()
        if purpose == "LOCAL_OBSERVATORY":
            ready=t>=safe_capture
            reason="CAPTURE_KNOWN_BY_CUT" if ready else "NOT_YET_IN_LOCAL_ARCHIVE"
        else:
            upper=self.public_upper_bound()
            ready=upper is not None and upper<=t
            reason=("HISTORICAL_BOUNDED_AVAILABLE_BY_REVIEWED_WITNESS" if ready
                    else "HISTORICAL_AVAILABILITY_UNKNOWN_OR_AFTER_CUT")
        # A reviewed negative witness means the exact *revision* was not
        # publicly available at or before the negative cut. This is not
        # evidence a political case did not exist or was unsuccessful.
        below=self.lower_bound()
        if below is not None and t<=below and purpose == "HISTORICAL_PUBLIC_PREDICTOR":
            ready=False
            reason="REVISION_NOT_PUBLIC_YET_PER_COMPLETE_NEGATIVE_WITNESS"
        if not ready:
            return {
                "status":"NOT_ADMITTED_AT_CUT", "purpose":purpose,
                "public_revision_usable":False, "reason":reason,
                "revision_id":None,"original_sha256":None,
                "event_on":None,"documentary_date":None,
                "first_public_at":None,
            }
        return {
            "status":"BOUNDED_AVAILABILITY" if purpose=="HISTORICAL_PUBLIC_PREDICTOR"
                     else "LOCAL_OBSERVATION_ONLY",
            "purpose":purpose,
            "public_revision_usable":purpose=="HISTORICAL_PUBLIC_PREDICTOR",
            "local_revision_usable":True if purpose=="LOCAL_OBSERVATORY" else None,
            "reason":reason,
            "revision_id":self.revision_id, "original_sha256":self.original_sha256,
            # Historical reconstruction from a trusted archival witness does
            # not permit using the *future research capture clock* as a model
            # feature at an earlier cut.
            "observed_local_safe_by":(safe_capture.isoformat()
                                      if safe_capture<=t else None),
            "public_available_by":(self.public_upper_bound().isoformat()
                                   if self.public_upper_bound() is not None else None),
            "not_public_before":(below.isoformat() if below else None),
            "claimed_event_on":self.claimed_event_on,
            "documentary_date":self.documentary_date,
            "first_public_at":None,
            "exact_first_public_at_verified":False,
            "not_observed_is_not_failure":True,
        }
