"""BR30J read-only local status adapter tests; fixtures contain no real people."""
import json

from politics_fantasy.evidence_warehouse_status import status


def test_missing_file_fails_closed(tmp_path):
    result = status(tmp_path / "no.json")
    assert result["ok"] is False
    assert result["real_people_verified"] == 0
    assert result["real_person_scoring"] is False


def test_reject_nonfiction_data(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"dataset_class": "OFFICIAL_VERIFIED", "sources": [], "entities": [],
                             "roles": [], "events": []}), encoding="utf8")
    assert status(p)["error"] == "NOT_FICTIONAL_BUNDLE"


def test_synthetic_summary_omits_names(tmp_path):
    p = tmp_path / "sample.json"
    p.write_text(json.dumps({
        "dataset_class": "FULLY_FICTIONAL_ENGINEERING_FIXTURE",
        "sources": [{"kind": "SYNTHETIC", "state": "TEST_FIXTURE", "id": "s"}],
        "entities": [{"id": "a", "type": "PARTY", "name": "Entidad Inventada", "source_id": "s"}],
        "roles": [], "events": []
    }), encoding="utf8")
    result = status(p)
    assert result["ok"] is True
    assert result["entities"] == 1
    assert result["entities_by_type"] == {"PARTY": 1}
    assert result["real_people_verified"] == 0
    assert "Entidad Inventada" not in json.dumps(result)
    assert "name" not in result


def test_bad_source_class_blocked(tmp_path):
    p = tmp_path / "sample.json"
    p.write_text(json.dumps({
        "dataset_class": "FULLY_FICTIONAL_ENGINEERING_FIXTURE",
        "sources": [{"kind": "OFFICIAL", "state": "RAW_CAPTURED"}],
        "entities": [], "roles": [], "events": []
    }), encoding="utf8")
    assert status(p)["error"] == "UNVERIFIED_SOURCE"
