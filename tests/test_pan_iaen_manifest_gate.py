"""Regression controls: a proposed source manifest cannot authorize ingestion."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from politics_fantasy.procedural_index_contract import GateError
from politics_fantasy.pan_iaen_preaccess_gate import validate_preaccess_source_manifest


PATH = Path(__file__).resolve().parents[1] / "research" / "PFL_POLICY_PUBLICAS_20261031" / "SOURCE_DECISION_GATE.json"


def fixture():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_manifest_is_blocked_even_when_calendar_pair_is_consistent():
    result = validate_preaccess_source_manifest(fixture())
    assert result["year_mapping_documented"] is True
    assert result["real_ingestion_admitted"] is False
    assert result["AB_scientific_cycles"] == 0
    assert result["outcome_2024_2025_blind_holdout"] is False


def test_previously_incorrect_pair_pan2024_iaen2025_is_rejected():
    altered = fixture()
    altered["primary_candidate"]["possible_pair"]["report_label_year"] = 2025
    with pytest.raises(GateError, match="MANIFEST_YEAR_RELATION_FALSE"):
        validate_preaccess_source_manifest(altered)


def test_approval_year_is_not_report_label_year():
    altered = fixture()
    altered["primary_candidate"]["possible_pair"]["report_approval_year"] = 2024
    with pytest.raises(GateError, match="MANIFEST_REPORT_APPROVAL_MISMATCH"):
        validate_preaccess_source_manifest(altered)


def test_approval_date_and_catalog_update_cannot_be_blended():
    altered = fixture()
    altered["primary_candidate"]["possible_pair"]["report_approval_on"] = "2024-04-15"
    with pytest.raises(GateError, match="MANIFEST_REPORT_APPROVAL_MISMATCH"):
        validate_preaccess_source_manifest(altered)


def test_asset_rights_and_terms_cannot_be_promoted_via_metadata():
    for path in ("rights_by_exact_asset_verified", "rights_acceptance_user_approved"):
        altered = fixture()
        altered["primary_candidate"][path] = True
        with pytest.raises(GateError, match="MANIFEST_UNAUTHORIZED_RIGHTS_PROMOTION"):
            validate_preaccess_source_manifest(altered)


def test_both_2024_and_2025_outcome_exposure_are_recorded():
    for year in ("2024", "2025"):
        altered = fixture()
        altered["primary_candidate"]["exposure_notice"][year]["confirmatory_holdout_unexposed"] = True
        with pytest.raises(GateError, match="MANIFEST_OUTCOME_EXPOSURE_CONTRADICTION"):
            validate_preaccess_source_manifest(altered)


def test_rights_on_regional_data_catalog_do_not_authorize_originals():
    data = fixture()
    data["regional_documentary_alternatives"][0]["original_opened"] = True
    with pytest.raises(GateError, match="MANIFEST_UNAUTHORIZED_RIGHTS_PROMOTION"):
        validate_preaccess_source_manifest(data)


def test_r5_or_cycle_counter_can_not_be_changed_by_source_metadata():
    for key, value in (("R5", "PASS"), ("AB_scientific_cycles", 1)):
        data = fixture()
        data[key] = value
        with pytest.raises(GateError, match="MANIFEST_SCIENTIFIC_GATE_CANNOT_PROMOTE"):
            validate_preaccess_source_manifest(data)


def test_asset_crosswalk_cannot_be_proclaimed_by_catalog_labels():
    data = fixture()
    data["primary_candidate"]["crosswalk_verified"] = True
    with pytest.raises(GateError, match="MANIFEST_FAKE_CROSSWALK_OR_DENOMINATOR"):
        validate_preaccess_source_manifest(data)


@pytest.mark.parametrize("mutation", [
    ("candidate", "rights_verified"),
    ("candidate", "eligible_for_real_ingestion"),
    ("exposure", "2026"),
])
def test_unknown_manifest_claims_cannot_be_smuggled_into_approved_metadata(mutation):
    data = fixture()
    scope, key = mutation
    if scope == "candidate":
        data["primary_candidate"][key] = True
    else:
        data["primary_candidate"]["exposure_notice"][key] = {
            "aggregate_outcome_snippet_seen": True,
            "confirmatory_holdout_unexposed": True,
        }
    with pytest.raises(GateError, match="MANIFEST_UNEXPECTED_FIELD"):
        validate_preaccess_source_manifest(data)
