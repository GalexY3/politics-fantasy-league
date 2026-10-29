"""Source-publication chronology gate for two specific original public ForecastBench snapshots.

This is documentary metadata from GitHub, NOT an independent certificate of
origin, a live API client, a participant dataset, or proof of per-record
first_public_at. Restrict evidence to two frozen, verified historical cutoffs
to prevent using a future resolution snapshot for a prequential claim.

Original data: Forecasting Research Institute / Karger et al., ICLR 2025,
forecastingresearch/forecastbench-datasets, CC BY-SA 4.0.
"""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha1
import json
from types import MappingProxyType

UPSTREAM = "forecastingresearch/forecastbench-datasets"
COHORT = "2026-09-27"
QUESTION_SHA1 = "d4c7e1286d76fbaa1c9911ffb0b97cbcc16440c0"
FIRST_PUBLIC_RESOLUTION_COMMIT = "4eafa5cdda4d9fbf3542ea9f5f71050b9dd89110"
FIRST_PUBLIC_RESOLUTION_AT = "2026-10-07T07:19:29Z"
FIRST_PUBLIC_RESOLUTION_SHA1 = "0b67cfec67fad4b23899e8e48c6ca3a034344edc"
LATER_RESOLUTION_COMMIT = "027ba0b3017a60e0e64602d724284ac6b2d91134"
LATER_RESOLUTION_AT = "2026-10-29T07:30:17Z"
LATER_RESOLUTION_SHA1 = "b2ee53f09407e2b555668f66e286073ace6d5fce"
_CHECKPOINTS = MappingProxyType({
    "2026-10-08T00:00:00Z": (
        FIRST_PUBLIC_RESOLUTION_COMMIT, FIRST_PUBLIC_RESOLUTION_AT, FIRST_PUBLIC_RESOLUTION_SHA1
    ),
    "2026-10-29T16:00:00Z": (
        LATER_RESOLUTION_COMMIT, LATER_RESOLUTION_AT, LATER_RESOLUTION_SHA1
    ),
})
_MARKETS = frozenset(("kalshi", "manifold", "metaculus", "polymarket"))


def _date_time(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("CANONICAL_UTC_REQUIRED")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("CANONICAL_UTC_REQUIRED") from exc
    if dt.utcoffset().total_seconds() != 0 or dt.isoformat().replace("+00:00", "Z") != value:
        raise ValueError("CANONICAL_UTC_REQUIRED")
    return dt


def git_blob_sha1(raw: bytes) -> str:
    if type(raw) is not bytes or not 0 < len(raw) <= 5_000_000:
        raise ValueError("BOUNDED_ORIGINAL_BYTES_REQUIRED")
    return sha1(b"blob " + str(len(raw)).encode("ascii") + b"\\0" + raw).hexdigest()


def select_verified_checkpoint(as_of_instant: str) -> dict:
    """Only two pre-checked immutable external commit snapshots are supported.

    The dated repo search found NO public Sep27 resolution-set file by
    2026-10-06 23:59:59Z; first documented commit is Oct07 07:19:29Z.
    Absence from this Git history does NOT establish absence from every
    possible third-party website or private original system.
    """
    cutoff = _date_time(as_of_instant)
    if cutoff < _date_time(FIRST_PUBLIC_RESOLUTION_AT):
        return {"status": "NO_ORIGINAL_PUBLIC_RESOLUTION_SET_AT_CUTOFF",
                "as_of_instant": as_of_instant,
                "known_first_repo_commit_at": FIRST_PUBLIC_RESOLUTION_AT,
                "historical_outcomes_scored": 0,
                "not_a_zero_outcome_claim": True,
                "scope": "PUBLIC_GITHUB_REPOSITORY_ONLY"}
    selected = _CHECKPOINTS.get(as_of_instant)
    if selected is None:
        return {"status": "NO_VERIFIED_EXACT_CHECKPOINT",
                "as_of_instant": as_of_instant,
                "historical_outcomes_scored": 0,
                "not_a_zero_outcome_claim": True,
                "scope": "PUBLIC_GITHUB_REPOSITORY_ONLY"}
    commit, committed_at, resolution_sha1 = selected
    if _date_time(committed_at) > cutoff:
        raise AssertionError("FUTURE_SOURCE_SNAPSHOT")
    return {"status": "PINNED_PUBLIC_SNAPSHOT_METADATA",
            "as_of_instant": as_of_instant, "source_commit": commit,
            "source_commit_at": committed_at, "resolution_blob_sha1": resolution_sha1,
            "question_blob_sha1": QUESTION_SHA1,
            "person_rows": 0, "publisher_authentication": False,
            "per_record_first_public_at": False,
            "scope": "PUBLIC_GITHUB_REPOSITORY_ONLY"}


def audit_verified_public_snapshot(question_raw: bytes, resolution_raw: bytes,
                                   *, as_of_instant: str) -> dict:
    """Fail closed on original Git blob mismatch before parsing or calculating.

    This requires ORIGINAL raw bytes; ordinary JSON serialization is not
    byte-identical. No override of precommitted expected blob SHA is accepted.
    """
    checkpoint = select_verified_checkpoint(as_of_instant)
    if checkpoint["status"] != "PINNED_PUBLIC_SNAPSHOT_METADATA":
        raise ValueError(checkpoint["status"])
    if (git_blob_sha1(question_raw) != QUESTION_SHA1 or
            git_blob_sha1(resolution_raw) != checkpoint["resolution_blob_sha1"]):
        raise ValueError("SOURCE_SNAPSHOT_GIT_BLOB_MISMATCH")
    try:
        q, r = json.loads(question_raw), json.loads(resolution_raw)
    except (UnicodeError, ValueError) as exc:
        raise ValueError("INVALID_ORIGINAL_JSON") from exc
    if (q.get("forecast_due_date") != COHORT or r.get("forecast_due_date") != COHORT or
            q.get("question_set") != COHORT + "-llm.json" or
            r.get("question_set") != COHORT + "-llm.json" or
            not isinstance(q.get("questions"), list) or not isinstance(r.get("resolutions"), list)):
        raise ValueError("SOURCE_COHORT_MISMATCH")
    resolutions = {}
    for row in r["resolutions"]:
        if isinstance(row, dict) and isinstance(row.get("source"), str) and isinstance(row.get("id"), str):
            resolutions.setdefault((row["source"], row["id"]), []).append(row)
    total, accepted, by_source, first_seen_ids = len(q["questions"]), 0, {}, set()
    rejected = {}
    def reject(k):
        rejected[k] = rejected.get(k, 0) + 1
    for row in q["questions"]:
        if not isinstance(row, dict) or not isinstance(row.get("source"), str) or not isinstance(row.get("id"), str):
            reject("MALFORMED_KEY"); continue
        k = (row["source"], row["id"])
        if k in first_seen_ids:
            raise ValueError("DUPLICATE_QUESTION_KEY")
        first_seen_ids.add(k)
        if row["source"] not in _MARKETS:
            reject("NONPROBABILITY_SOURCE");continue
        try:
            if type(row.get("freeze_datetime_value")) is not str or not row["freeze_datetime_value"].strip():
                raise ValueError()
            p=float(row["freeze_datetime_value"])
        except (ValueError, TypeError, OverflowError):
            reject("INVALID_PROBABILITY");continue
        if not 0 <= p <= 1:
            reject("INVALID_PROBABILITY");continue
        rs=resolutions.get(k, [])
        if len(rs) != 1:
            reject("NO_UNIQUE_RESOLUTION");continue
        y=rs[0]
        if y.get("resolved") is not True or type(y.get("resolved_to")) is not int or y["resolved_to"] not in (0,1):
            reject("NO_BINARY_RESOLUTION");continue
        try:
            resolved_on=datetime.fromisoformat(y["resolution_date"]).date()
            due=datetime.fromisoformat(COHORT).date()
        except (ValueError, TypeError, KeyError):
            reject("INVALID_RESOLUTION_DATE");continue
        if not due < resolved_on < _date_time(as_of_instant).date():
            reject("CUTOFF_OR_ORDER");continue
        accepted+=1;by_source[row["source"]]=by_source.get(row["source"],0)+1
    if accepted+sum(rejected.values()) != total:
        raise AssertionError("ACCOUNTING_MISMATCH")
    return {
        "schema": "pfl.public.snapshot.publication.gate.v1",
        "as_of_instant": as_of_instant,
        "source_commit": checkpoint["source_commit"],
        "source_commit_at": checkpoint["source_commit_at"],
        "question_blob_sha1": QUESTION_SHA1,
        "resolution_blob_sha1": checkpoint["resolution_blob_sha1"],
        "original_questions": total, "accepted": accepted, "rejected": rejected,
        "accepted_by_source": by_source,
        "interpretation": "PUBLIC_GIT_SNAPSHOT_AT_CUTOFF_NOT_PER_RECORD_FIRST_PUBLIC_AT",
        "not_independent_publisher_authentication": True,
        "not_human_causes": True, "person_rows": 0, "release_ready": False
    }
