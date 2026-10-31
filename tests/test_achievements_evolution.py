"""Achievements evolve through audit events; never silently erase historical IDs."""
import copy
import json
from pathlib import Path

from ab_atlas.validate_achievements import validate


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "ab_atlas/ACHIEVEMENTS_REGISTRY.json").read_text(encoding="utf-8"))


def test_v7_new_context_relay_is_locked_not_empirically_promoted():
    assert validate(REGISTRY) == []
    relay = next(x for x in REGISTRY["achievements"] if x["id"] == "PFL-QA-11")
    assert relay["status"] == "locked"
    assert relay["prerequisites"] == ["PFL-QA-02"]
    assert not relay["evidence"]
    assert len(REGISTRY["achievements"]) == 91
    assert sum(x["status"] == "unlocked" for x in REGISTRY["achievements"]) == 5


def test_an_old_id_cannot_be_deleted_to_raise_completion_percent():
    bad = copy.deepcopy(REGISTRY)
    bad["achievements"] = [x for x in bad["achievements"] if x["id"] != "PFL-QA-10"]
    assert any("HISTORICAL_ACHIEVEMENT_DELETED" in e for e in validate(bad))


def test_an_added_id_needs_a_canonical_creation_event():
    bad = copy.deepcopy(REGISTRY)
    bad["change_log"][-1]["type"] = "achievement.edited"
    assert any("NEW_ACHIEVEMENT_WITHOUT_AUDIT_EVENT" in e for e in validate(bad))


def test_retirement_without_event_and_reason_fails():
    bad = copy.deepcopy(REGISTRY)
    item = next(x for x in bad["achievements"] if x["id"] == "PFL-QA-11")
    item["status"] = "retired"
    assert any("retired without" in e for e in validate(bad))


def test_unearned_unlock_without_event_fails():
    bad = copy.deepcopy(REGISTRY)
    item = next(x for x in bad["achievements"] if x["id"] == "PFL-UI-01")
    item["status"] = "unlocked"
    item["evidence"] = ["fake-evidence"]
    item["verified_by"] = "FAKE"
    item["verified_at"] = "2026-10-31"
    assert any("last audit event" in e for e in validate(bad))
