"""R14 documentary rights, frame and vintage gates; no case-data ingestion.

Pure, synthetic-only quality-assurance contract. It makes *negative*
identification claims, never certifies an actual Spanish all-received census.
Even a completed local checklist cannot override R5 or substitute frozen
remote A/J and authenticated rights for the exact original distribution.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
import re

ID = re.compile(r"^SYNTHETIC:[A-Z0-9_:-]{1,110}$")
SHA = re.compile(r"^[a-f0-9]{64}$")
ROLES = {"INITIAL_INTAKE", "CASE_FILE", "TERMINAL_DECISION", "PUBLISHED_INDEX", "PROCEDURE_TYPE"}
RIGHTS = {"UNKNOWN", "GENERAL_TERMS_BIND_ON_ACCESS", "PORTAL_ATTRIBUTION_NOTICE_ONLY", "ASSET_LICENSE_REVIEWED_NO_ACCEPTANCE"}


class ProbeError(ValueError):
    """Refuse incoherent synthetic-only input rather than silently join it."""


def _time(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ProbeError("NEED_EXPLICIT_UTC_INSTANT")
    try:
        d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProbeError("INVALID_UTC_INSTANT") from exc
    return d.astimezone(timezone.utc)


def _local_safe_by(observed_on: str) -> datetime:
    """DATE-precision audit: evidence is visible only after that UTC day ends.

    An editorial restore-point date is NOT the date our audit learned of it.
    A historical cut cannot see a later documentary discovery, even when the
    publisher's edition label is older than the cut.
    """
    if not isinstance(observed_on, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", observed_on):
        raise ProbeError("LOCAL_AUDIT_DAY_REQUIRED")
    try:
        parsed = date.fromisoformat(observed_on)
    except ValueError as exc:
        raise ProbeError("INVALID_LOCAL_AUDIT_DAY") from exc
    return datetime(parsed.year, parsed.month, parsed.day, tzinfo=timezone.utc) + timedelta(days=1)


@dataclass(frozen=True)
class Frame:
    institution: str
    family: str
    regime: str
    entry_stage: str
    unit: str
    first_day: str
    last_day: str

    def __post_init__(self):
        if (not all(isinstance(v, str) and v.startswith("SYNTHETIC_")
                    for v in (self.institution, self.family, self.regime, self.unit))
                or self.entry_stage not in {"ALL_RECEIVED", "ADMITTED_FIRST"}
                or _time(self.first_day) >= _time(self.last_day)):
            raise ProbeError("FRAMES_NOT_IDENTICAL_OR_NOT_SYNTHETIC")


@dataclass(frozen=True)
class Asset:
    source_id: str
    publisher_id: str
    backend_id: str
    frame: Frame
    role: str
    rights: str
    locally_known_on: str
    original_sha256: str | None = None
    total_claim: int | None = None
    verified_original: bool = False
    independently_audited_population: bool = False

    def __post_init__(self):
        _local_safe_by(self.locally_known_on)
        if (not all(isinstance(v, str) and ID.fullmatch(v)
                    for v in (self.source_id, self.publisher_id, self.backend_id))
                or not isinstance(self.frame, Frame)
                or self.role not in ROLES or self.rights not in RIGHTS
                or (self.original_sha256 is not None and
                    (not isinstance(self.original_sha256, str) or not SHA.fullmatch(self.original_sha256)))
                or (self.total_claim is not None and
                    (type(self.total_claim) is not int or self.total_claim < 0))
                or self.verified_original is not False
                or self.independently_audited_population is not False):
            raise ProbeError("REAL_ASSET_OR_UNVERIFIED_RIGHTS_PROMOTION")


@dataclass(frozen=True)
class ArchiveHint:
    source_id: str
    dataset_id: str
    described_at: str
    locally_known_on: str
    original_sha256: str | None = None
    original_bytes_authenticated: bool = False
    first_public_at: None = None

    def __post_init__(self):
        safe = _local_safe_by(self.locally_known_on)
        if (not all(isinstance(v, str) and ID.fullmatch(v)
                    for v in (self.source_id, self.dataset_id))
                or (self.original_sha256 is not None and
                    not SHA.fullmatch(self.original_sha256))
                or self.original_bytes_authenticated is not False
                or self.first_public_at is not None):
            raise ProbeError("RESTORE_HINT_NOT_ORIGINAL_OR_PUBLIC_WITNESS")
        if _time(self.described_at) >= safe:
            raise ProbeError("EDITORIAL_EDITION_AFTER_LOCAL_AUDIT")


def audit(*, entry: Asset, comparator: Asset | None,
          hints: tuple[ArchiveHint, ...], as_of: str) -> dict:
    """Return blocked, explicitly non-empirical, non-additive audit fields.

    Time filters *all* documentary information, including flags and counts.
    Claims of independence, legal permission or historical versions from a
    shared publisher, metadata restore buttons or SHA labels are insufficient.
    """
    t = _time(as_of)
    if (not isinstance(entry, Asset) or entry.role != "INITIAL_INTAKE"
            or (comparator is not None and not isinstance(comparator, Asset))
            or type(hints) is not tuple or len(hints) > 120
            or any(not isinstance(h, ArchiveHint) for h in hints)):
        raise ProbeError("INVALID_DOCUMENTARY_FRAME_INPUT")
    base = {
        "schema": "pfl.synthetic_documentary_frame_gate.v1",
        "synthetic_only": True,
        "R5_passed": False,
        "independent_denominator": None,
        "rights_for_real_original_granted": False,
        "real_terminal_outcomes": None,
        "real_pending_or_censored": None,
        "first_public_at": None,
        "two_real_original_vintages_compared": False,
        "AB_cycles": 0,
    }
    # The publisher's edition label is not a historical-publication witness.
    # Filter by documented *local knowledge*, not by advertised edition dates.
    # Comparator metadata also has its own independently bounded discovery.
    if t < _local_safe_by(entry.locally_known_on):
        return {**base, "status": "NO_DOCUMENTARY_ASSET_KNOWN_AS_OF",
                "listed_restore_hints": None,
                "same_dataset_restore_hints": None,
                "comparator_same_frame": None,
                "comparator_independent_backend": None,
                "asset_license_sufficient": None}
    visible = tuple(h for h in hints if _local_safe_by(h.locally_known_on) <= t)
    if not visible:
        return {**base, "status": "NO_DOCUMENTARY_VERSION_HINT_KNOWN_AS_OF",
                "listed_restore_hints": None,
                "same_dataset_restore_hints": None,
                "comparator_same_frame": None,
                "comparator_independent_backend": None,
                "asset_license_sufficient": None}
    if any(h.source_id != entry.source_id for h in visible):
        raise ProbeError("MIXED_SOURCE_ARCHIVE_HINTS")
    same_dataset = len({h.dataset_id for h in visible}) == 1
    seen_comparator = (comparator if comparator is not None
                       and _local_safe_by(comparator.locally_known_on) <= t else None)
    return {**base,
        "status": "DOCUMENTARY_VERSION_HINTS_NOT_REAL_SNAPSHOTS",
        "listed_restore_hints": len(visible),
        "same_dataset_restore_hints": same_dataset,
        "comparator_same_frame": (seen_comparator.frame == entry.frame
                                  if seen_comparator is not None else None),
        "comparator_independent_backend": (
            seen_comparator.publisher_id != entry.publisher_id
            and seen_comparator.backend_id != entry.backend_id
            if seen_comparator is not None else None),
        "asset_license_sufficient": False,
        "originals_present": False,
        "publisher_claim_not_independent_total": True,
        "catalogue_count_not_received_denominator": True,
        "restore_button_not_first_public_at": True,
        "no_fuzzy_case_joins": True}
