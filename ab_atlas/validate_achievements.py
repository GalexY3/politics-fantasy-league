#!/usr/bin/env python3
"""Read-only verification of versioned symbolic achievement sidecar.

No changes to AB Atlas graph/delta replay, scientific indices, or launch gates.
Requires Python 3.10+ stdlib. Usage:
 python proyectos/politics-fantasy-league/ab_atlas/validate_achievements.py
 python proyectos/politics-fantasy-league/ab_atlas/validate_achievements.py --file path/to/ACHIEVEMENTS_REGISTRY.json
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

EXPECTED_TRACKS = {
    "sources": 18, "identity": 12, "events": 10, "science": 14, "game": 16,
    "ui": 10, "security": 8, "qa": 8, "launch": 4,
}
STATUS = {"locked", "unlocked", "retired"}


def validate(doc: dict, *, original: bool = False) -> list[str]:
    issues: list[str] = []
    if not isinstance(doc, dict):
        return ["Registry must be JSON object"]
    if doc.get("schema") != "pfl.achievements.v1":
        issues.append("Unexpected achievement schema")
    tracks = doc.get("tracks", [])
    items = doc.get("achievements", [])
    log = doc.get("change_log", [])
    if not isinstance(tracks, list) or not isinstance(items, list) or not isinstance(log, list):
        return issues + ["tracks/achievements/change_log must be arrays"]
    track_ids = [t.get("id") for t in tracks if isinstance(t, dict)]
    weights = {t.get("id"): t.get("weight") for t in tracks if isinstance(t, dict)}
    if set(track_ids) != set(EXPECTED_TRACKS) or len(track_ids) != 9 or weights != EXPECTED_TRACKS:
        issues.append("Nine V4 tracks and their frozen weights must be preserved")
    ids = [a.get("id") for a in items if isinstance(a, dict)]
    if len(ids) != len(items) or len(ids) != len(set(ids)):
        issues.append("Achievement IDs must be unique")
    by_id = {a["id"]: a for a in items if isinstance(a, dict) and isinstance(a.get("id"), str)}
    counts = Counter()
    for a in items:
        if not isinstance(a, dict):
            issues.append("Achievement is not an object")
            continue
        aid, track = a.get("id"), a.get("track_id")
        if not isinstance(aid, str) or not aid.startswith("PFL-"):
            issues.append("Invalid achievement ID")
        if track not in EXPECTED_TRACKS:
            issues.append(f"{aid}: unknown track")
        else:
            counts[track] += a.get("status") != "retired"
        if a.get("status") not in STATUS:
            issues.append(f"{aid}: invalid status")
        if not str(a.get("title", "")).strip() or not str(a.get("criteria", "")).strip():
            issues.append(f"{aid}: missing objective acceptance criterion")
        prereqs = a.get("prerequisites", [])
        if not isinstance(prereqs, list):
            issues.append(f"{aid}: prerequisites not array")
            continue
        for ref in prereqs:
            if ref not in by_id or ref == aid:
                issues.append(f"{aid}: unknown/self prerequisite {ref}")
            elif a.get("status") == "unlocked" and by_id[ref].get("status") != "unlocked":
                issues.append(f"{aid}: unlocked before prerequisite {ref}")
        if a.get("status") == "unlocked" and (not a.get("verified_by") or
                not a.get("verified_at") or not a.get("evidence")):
            issues.append(f"{aid}: unlocked without attributable evidence")
    visiting: set[str] = set()
    done: set[str] = set()
    def visit(aid: str) -> None:
        if aid in visiting:
            issues.append(f"{aid}: cyclic prerequisite relation")
            return
        if aid in done or aid not in by_id:
            return
        visiting.add(aid)
        for dep in by_id[aid].get("prerequisites", []):
            if dep in by_id:
                visit(dep)
        visiting.remove(aid)
        done.add(aid)
    for aid in ids:
        if aid in by_id:
            visit(aid)
    version = doc.get("version")
    if not isinstance(version, int) or version < 1:
        issues.append("Invalid registry version")
    if len(log) != version:
        issues.append("Every version requires exactly one recorded event")
    for n, event in enumerate(log, start=1):
        if not isinstance(event, dict) or event.get("seq") != n or event.get("registry_version") != n:
            issues.append(f"Audit event sequence {n} is incomplete")
        elif not str(event.get("type", "")).strip() or not str(event.get("reason", "")).strip():
            issues.append(f"Audit event sequence {n} lacks a type or reason")
    if log and isinstance(log[0], dict):
        founding = log[0].get("affected_ids", [])
        if log[0].get("type") != "registry.created" or not isinstance(founding, list) or len(founding) != 90:
            issues.append("Original 90-ID register origin missing")
        else:
            for aid in founding:
                if aid not in by_id:
                    issues.append(f"HISTORICAL_ACHIEVEMENT_DELETED: {aid}; soft-retire instead")
            newly_created = set(by_id).difference(founding)
            for aid in sorted(newly_created):
                if not any(isinstance(e, dict) and e.get("type") == "achievement.created"
                           and e.get("achievement_id") == aid for e in log[1:]):
                    issues.append(f"NEW_ACHIEVEMENT_WITHOUT_AUDIT_EVENT: {aid}")
    for aid, a in by_id.items():
        histories = [e for e in log[1:] if isinstance(e, dict) and e.get("achievement_id") == aid]
        latest = histories[-1].get("type") if histories else "registry.created"
        if a.get("status") == "unlocked" and latest != "achievement.unlocked":
            issues.append(f"{aid}: unlocked status contradicts last audit event")
        if a.get("status") == "retired" and latest != "achievement.retired":
            issues.append(f"{aid}: retired without final audit event")
        if a.get("status") == "retired" and not str(a.get("retirement_reason", "")).strip():
            issues.append(f"{aid}: retired without explicit reason")
        if a.get("status") == "locked" and latest in {"achievement.unlocked", "achievement.retired"}:
            issues.append(f"{aid}: locked status contradicts last audit event")
    if original and (len(items) != 90 or any(counts[t] != 10 for t in EXPECTED_TRACKS)):
        issues.append("Initial registry requires exactly 10 active achievements per branch, 90 total")
    if original and any(a.get("status") != "locked" for a in items):
        issues.append("Initial registry must not award achievements without review")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, default=Path(__file__).with_name("ACHIEVEMENTS_REGISTRY.json"))
    parser.add_argument("--initial", action="store_true", help="Require original 9x10 all-locked initialization")
    args = parser.parse_args()
    doc = json.loads(args.file.read_text(encoding="utf-8"))
    errors = validate(doc, original=args.initial)
    if errors:
        for issue in errors:
            print("INVALID:", issue)
        return 2
    active = [x for x in doc["achievements"] if x["status"] != "retired"]
    unlocked = sum(x["status"] == "unlocked" for x in active)
    print(f"OK achievements registry v{doc['version']}: {unlocked}/{len(active)} unlocked, 9 tracks, events={len(doc['change_log'])}")
    print("NOTICE: symbolic only; V4 progress, CT2, VSDS, official data rights and release gates NOT adjudicated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
