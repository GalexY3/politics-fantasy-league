"""Read-only local raw/ledger integrity audit; returns aggregate statuses only.

Not an HTTP endpoint, issuer signature, license review or real-person scorer.
POSIX dirfd anchored; never follows source-authored object paths.
"""
from __future__ import annotations
from collections import Counter
from contextlib import contextmanager
import hashlib
import json
import os
import re
from pathlib import Path

from .secure_store import (_root_fd, _child_directory, _check_private_permissions,
                           _directory_flags)

@contextmanager
def _existing_dir(parentfd: int, name: str):
    if not name or name in (".", "..") or "/" in name or "\\" in name:
        raise ValueError("UNSAFE_AUDIT_DIRECTORY")
    try:
        fd = os.open(name, _directory_flags(), dir_fd=parentfd)
    except FileNotFoundError:
        yield None
        return
    except OSError as exc:
        raise ValueError("UNSAFE_AUDIT_DIRECTORY") from exc
    try:
        _check_private_permissions(fd, directory=True)
        yield fd
    finally:
        os.close(fd)


MAX_LEDGER_BYTES = 8 * 1024 * 1024
MAX_ROWS = 10000
MAX_OBJECT_BYTES = 20 * 1024 * 1024
OBJECT_RE = re.compile(r"\Aobjects/([0-9a-f]{2})/([0-9a-f]{64})\Z")


def _ledger(fd: int, filename: str) -> list[dict]:
    if filename not in ("manifest.jsonl", "quarantine_reviews.jsonl"):
        raise ValueError("UNAPPROVED_LEDGER")
    try:
        obj = os.open(filename, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                      dir_fd=fd)
    except FileNotFoundError:
        return []
    except OSError as exc:
        raise ValueError("UNSAFE_LEDGER") from exc
    try:
        _check_private_permissions(obj, directory=False)
        data = bytearray()
        while len(data) <= MAX_LEDGER_BYTES:
            chunk = os.read(obj, min(65536, MAX_LEDGER_BYTES + 1 - len(data)))
            if not chunk:
                break
            data.extend(chunk)
        if len(data) > MAX_LEDGER_BYTES:
            raise ValueError("LEDGER_TOO_LARGE")
        lines = data.splitlines()
        if len(lines) > MAX_ROWS:
            raise ValueError("TOO_MANY_LEDGER_ROWS")
        try:
            values = [json.loads(line) for line in lines]
        except (ValueError, UnicodeError) as exc:
            raise ValueError("BAD_LEDGER_JSON") from exc
        if any(not isinstance(x, dict) for x in values):
            raise ValueError("BAD_LEDGER_RECORD")
        return values
    finally:
        os.close(obj)


def _validate_object(objectsfd: int | None, rel: object, expected: object) -> str:
    if not isinstance(rel, str) or not isinstance(expected, str):
        return "BAD_OBJECT_REFERENCE"
    m = OBJECT_RE.fullmatch(rel)
    if m is None or m[1] != m[2][:2] or expected != m[2]:
        return "BAD_OBJECT_REFERENCE"
    if objectsfd is None:
        return "MISSING_OR_UNSAFE_OBJECT"
    try:
        with _existing_dir(objectsfd, m[1]) as shard:
            if shard is None:
                return "MISSING_OR_UNSAFE_OBJECT"
            fd = os.open(m[2], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                         dir_fd=shard)
            try:
                _check_private_permissions(fd, directory=False)
                digest = hashlib.sha256()
                total = 0
                while total <= MAX_OBJECT_BYTES:
                    block = os.read(fd, min(65536, MAX_OBJECT_BYTES + 1 - total))
                    if not block:
                        break
                    total += len(block)
                    digest.update(block)
                if total > MAX_OBJECT_BYTES:
                    return "OVERSIZED_OBJECT"
                if digest.hexdigest() != expected:
                    return "BAD_RAW_SHA"
                return "VALID_OBJECT"
            finally:
                os.close(fd)
    except (OSError, ValueError):
        return "MISSING_OR_UNSAFE_OBJECT"


def audit_private_root(root: Path) -> dict:
    """No URLs, raw content or person-level records are returned."""
    with _root_fd(root) as fd:
        manifest = _ledger(fd, "manifest.jsonl")
        reviews = _ledger(fd, "quarantine_reviews.jsonl")
        outcomes = Counter()
        with _existing_dir(fd, "objects") as objectsfd:
            for item in manifest:
                outcomes[_validate_object(objectsfd, item.get("raw_object"), item.get("sha256"))] += 1
        review_states = Counter()
        valid_manifest = {}
        manifest_duplicate_ids = set()
        legacy_captures = 0
        for item in manifest:
            cid = item.get("capture_id")
            if not isinstance(cid, str) or not re.fullmatch(r"[0-9a-f]{32}", cid):
                legacy_captures += 1
            elif cid in valid_manifest:
                manifest_duplicate_ids.add(cid)
            else:
                valid_manifest[cid] = item.get("sha256")
        seen_reviews = set()
        exactly_matched = set()
        for item in reviews:
            cid = item.get("capture_id")
            if not isinstance(cid, str) or not re.fullmatch(r"[0-9a-f]{32}", cid):
                review_states["LEGACY_REVIEW_WITHOUT_ID"] += 1
            elif cid in manifest_duplicate_ids:
                review_states["AMBIGUOUS_MANIFEST_CAPTURE_ID"] += 1
            elif cid in seen_reviews:
                review_states["DUPLICATE_REVIEW"] += 1
                exactly_matched.discard(cid)
            elif cid not in valid_manifest:
                review_states["ORPHAN_REVIEW"] += 1
            elif valid_manifest[cid] != item.get("sha256"):
                review_states["REVIEW_SHA_MISMATCH"] += 1
            else:
                state = item.get("quarantine_state")
                if state not in {"QUARANTINED_SCHEMA_PASSED", "QUARANTINED_SCHEMA_FAILED",
                                 "QUARANTINED_INTEGRITY_FAILED"}:
                    review_states["UNKNOWN_REVIEW_STATE"] += 1
                else:
                    review_states[state] += 1
                    exactly_matched.add(cid)
            if isinstance(cid, str):
                seen_reviews.add(cid)
        return {
            "manifest_rows": len(manifest), "review_rows": len(reviews),
            "object_integrity": dict(sorted(outcomes.items())),
            "quarantine_states": dict(sorted(review_states.items())),
            "unreviewed_captures": (len(valid_manifest) - len(exactly_matched)),
            "legacy_captures_unlinked": legacy_captures,
            "duplicate_manifest_capture_ids": len(manifest_duplicate_ids),
            "first_public_at_verified": False, "publisher_signature_verified": False,
            "real_person_scoring": False, "release_grade": False,
            "http_ingest_connected": False,
        }
