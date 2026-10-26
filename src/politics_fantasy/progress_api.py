"""Versioned, evidence-scoped Politics Fantasy completion metric.

Read-only local demo endpoint. Maturity levels are reviewed judgments backed by
repository evidence, not statistical probabilities, scientific grades or real
individual political assessments.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
DEFAULT_SCOPE = PROJECT / "product/progress_scope_v1.json"
MATURITY = (0.0, 0.1, 0.4, 0.6, 0.85, 1.0)
RELEASE_REQUIREMENTS = {
    "src.registry": (4, "Registro de partidos/candidaturas sin originales auditados"),
    "id.real": (4, "Identidades públicas reales sin reconciliar"),
    "ev.person": (4, "Eventos individuales reales sin atribución verificada"),
    "sec.auth": (4, "Autenticación y autorización multiusuario inexistentes"),
    "qa.endtoend": (4, "Pruebas end-to-end nativas aún no acreditadas"),
    "launch.hosted": (4, "No existe despliegue público seguro"),
}


class InvalidScope(ValueError):
    pass


def evaluate_scope(payload: dict) -> dict:
    """Mirror src/politics_fantasy/progress_model.mjs precisely."""
    if not isinstance(payload, dict):
        raise InvalidScope("SCOPE_NOT_OBJECT")
    if payload.get("scope_id") != "PFL-V1-20261026":
        raise InvalidScope("SCOPE_FAMILY_NOT_SUPPORTED")
    revision = payload.get("revision")
    if type(revision) is not int or revision < 1:
        raise InvalidScope("SCOPE_REVISION")
    tracks = payload.get("tracks")
    if not isinstance(tracks, list) or not tracks:
        raise InvalidScope("NO_TRACKS")
    seen_tracks, seen_milestones = set(), set()
    track_output = []
    levels = Counter()
    total_weights = 0.
    maturity_map = {}
    for track in tracks:
        if not isinstance(track, dict):
            raise InvalidScope("BAD_TRACK")
        tid, weight = track.get("id"), track.get("weight")
        if not isinstance(tid, str) or not tid or tid in seen_tracks:
            raise InvalidScope("DUPLICATE_TRACK")
        seen_tracks.add(tid)
        if type(weight) not in (int, float) or not 0 < weight <= 100:
            raise InvalidScope("BAD_WEIGHT")
        total_weights += weight
        milestones = track.get("milestones")
        if not isinstance(milestones, list) or not milestones:
            raise InvalidScope("NO_MILESTONES")
        value, units, out = 0., 0., []
        for milestone in milestones:
            if not isinstance(milestone, dict):
                raise InvalidScope("BAD_MILESTONE")
            mid, lvl, size = (milestone.get("id"), milestone.get("level"),
                               milestone.get("size"))
            if not isinstance(mid, str) or not mid or mid in seen_milestones:
                raise InvalidScope("DUPLICATE_MILESTONE")
            seen_milestones.add(mid)
            if type(lvl) is not int or lvl not in range(len(MATURITY)):
                raise InvalidScope("INVALID_MATURITY")
            if type(size) not in (int, float) or size <= 0 or size > 10000:
                raise InvalidScope("BAD_SIZE")
            if not isinstance(milestone.get("evidence_ref"), str) or not milestone["evidence_ref"]:
                raise InvalidScope("MISSING_EVIDENCE")
            earned = MATURITY[lvl]
            value += size * earned
            units += size
            levels[str(lvl)] += 1
            maturity_map[mid] = lvl
            out.append({"id": mid, "name": milestone["name"],
                        "maturity": lvl, "earned": earned,
                        "weight_within_track": size,
                        "evidence_ref": milestone["evidence_ref"],
                        "evidence_class": milestone["evidence_class"],
                        "reason": milestone["why"]})
        pct = 100. * value / units
        track_output.append({"id": tid, "name": track["name"], "weight": weight,
                             "progress_pct": pct,
                             "contribution_pp": weight * pct / 100.,
                             "achieved_units": value, "scope_units": units,
                             "milestones": out})
    if abs(total_weights-100) > 1e-8:
        raise InvalidScope("WEIGHTS_MUST_TOTAL_100")
    completed = sum(t["contribution_pp"] for t in track_output)
    blockers = [message for mid, (required, message) in RELEASE_REQUIREMENTS.items()
                if maturity_map.get(mid, 0) < required]
    return {
        "ok": True, "schema": "PFL_PROGRESS_1",
        "scope_id": payload["scope_id"], "revision": revision,
        "review_date": payload.get("review_date"),
        "objective": payload.get("target"),
        "progress_pct": completed, "progress_display_pct": round(completed, 1),
        "level_histogram": {str(i): levels[str(i)] for i in range(6)},
        "track_count": len(track_output), "milestone_count": len(seen_milestones),
        "tracks": track_output,
        "global_status": ("NOT_PUBLIC_RELEASE_READY" if blockers
                          else "RELEASE_GATES_CLEARED_FOR_FURTHER_VALIDATION"),
        "release_blockers": blockers, "real_people_scoring_ready": False,
        "scientific_grade_separate": True, "actor_influence_inferred": False,
        "scope_change_notice": "Wider requirements can reduce this score without loss of working software."
    }


def progress_status(path: Path | None = None) -> dict:
    p = Path(path) if path is not None else DEFAULT_SCOPE
    try:
        if not p.is_file() or p.stat().st_size > 160_000:
            return {"ok": False, "error": "SCOPE_UNAVAILABLE"}
        return evaluate_scope(json.loads(p.read_text(encoding="utf8")))
    except (OSError, ValueError, KeyError, TypeError):
        return {"ok": False, "error": "SCOPE_INVALID_OR_UNVERIFIED"}
