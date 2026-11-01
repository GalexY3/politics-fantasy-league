"""Synthetic contract checks for PP04 branches #11 and #12; no originals."""

import importlib

import pytest


PAN = (
    "9. PLAN ANUAL NORMATIVO\nREAL DECRETO ALFA\nObjetivo: alfa\nMinisterio: A\n"
    "LEY BETA\nObjetivo: beta\nMinisterio: A\n",
)
IAEN = (
    "4.1.- MINISTERIO A\n"
    "4.1.1.- INICIATIVAS NORMATIVAS INCLUIDAS EN EL PLAN ANUAL\n"
    "NORMATIVO 2024\nI. Aprobadas\n- Real Decreto alfa.\n"
    "II. Pendientes de aprobación\n- Ley beta.\n"
    "4.1.2.- NORMAS APROBADAS NO INCLUIDAS EN EL PLAN ANUAL\n"
    "- Real Decreto externo.\n"
    "4.22.- VIVIENDA\n"
    "4.22.1.- NORMAS APRO BADAS NO INCLUIDAS EN EL PLAN ANUAL\n"
    "- Real Decreto externo 2.\n"
    "5. REALES DECRETOS-LEYES\n",
)


def test_pr11_and_pr12_public_parser_contracts_coexist():
    frame = importlib.import_module("politics_fantasy.pan_iaen_original_frame")
    for name in (
        "parse_pan_objective_ministry_pairs",
        "parse_iaen_ministry_bullets",
        "summarise_local_frame",
        "parse_plan_candidate_blocks",
        "parse_report_ministry_listings",
        "reconcile_counts_without_crosswalk",
        "verify_exact_original_sha256",
        "require_private_output_directory",
    ):
        assert callable(getattr(frame, name, None)), name


def test_two_parsers_agree_on_synthetic_section_counts_without_claiming_crosswalk():
    bridge = importlib.import_module("politics_fantasy.pan_iaen_cross_parser_audit")
    report = bridge.audit_pp04_dual_parsers(
        PAN, IAEN, expected_plan_count=2, expected_planned_count=2,
        expected_approved_count=1,
        expected_planned_sections=(1,), expected_unplanned_count=2,
    )
    assert report["count_and_section_status_agreement"] is True
    assert report["planned_count"] == 2
    assert report["approved_count"] == 1
    assert report["pending_unsplit_count"] == 1
    assert report["not_included_4221_excluded"] is True
    assert report["expected_ministry_sections_matched"] is True
    assert report["expected_unplanned_count_matched"] is True
    assert report["item_crosswalk_verified"] is False
    assert report["first_public_at_verified"] is False
    assert report["source_rights_independently_verified"] is False
    assert report["R5"] == "STOP"


def test_parser_disagreement_cannot_be_silently_promoted_to_agreement():
    bridge = importlib.import_module("politics_fantasy.pan_iaen_cross_parser_audit")
    # The line-oriented parser admits a generic bullet; the block-oriented
    # one requires a supported legal title prefix. Neither can silently win.
    divergent = (IAEN[0].replace("- Ley beta.", "- Texto sin rango normativo."),)
    with pytest.raises(ValueError, match="DUAL_PARSER"):
        bridge.audit_pp04_dual_parsers(
            PAN, divergent, expected_plan_count=2, expected_planned_count=2,
            expected_approved_count=1,
            expected_planned_sections=(1,), expected_unplanned_count=2,
        )


def test_unrecognized_roman_status_cannot_inherit_previous_approved_heading():
    frame = importlib.import_module("politics_fantasy.pan_iaen_original_frame")
    source = (
        "4.1.- MINISTERIO A\n"
        "4.1.1.- INICIATIVAS NORMATIVAS INCLUIDAS EN EL PLAN\n"
        "I. Aprobadas\n- Ley A\n"
        "III. Desistidas\n- Ley B\n"
        "5. REALES DECRETOS-LEYES\n",
    )
    with pytest.raises(frame.FrameParseError, match="UNSUPPORTED_PLANNED_STATUS_HEADING"):
        frame.parse_iaen_ministry_bullets(source)


def test_equal_global_counts_do_not_hide_department_status_disagreement(monkeypatch):
    bridge = importlib.import_module("politics_fantasy.pan_iaen_cross_parser_audit")
    original = bridge.parse_report_ministry_listings

    def conflicting_section(*args, **kwargs):
        result = original(*args, **kwargs)
        # Artificially introduce a wrong department with the same totals.
        result["rows"][0]["source_ministry_section"] = 99
        return result

    monkeypatch.setattr(bridge, "parse_report_ministry_listings", conflicting_section)
    with pytest.raises(bridge.FrameParseError, match="SECTION_STATUS_MISMATCH"):
        bridge.audit_pp04_dual_parsers(
            PAN, IAEN, expected_plan_count=2, expected_planned_count=2,
            expected_approved_count=1,
            expected_planned_sections=(1,), expected_unplanned_count=2,
        )


def test_dual_audit_never_echoes_row_level_source_text():
    bridge = importlib.import_module("politics_fantasy.pan_iaen_cross_parser_audit")
    report = bridge.audit_pp04_dual_parsers(
        PAN, IAEN, expected_plan_count=2, expected_planned_count=2,
        expected_approved_count=1,
        expected_planned_sections=(1,), expected_unplanned_count=2,
    )
    assert not any("rows" in key or "text" in key or "title" in key for key in report)
    assert report["two_parsers_are_independent_sources"] is False
    assert report["independent_all_received_denominator_attested"] is False


def test_missing_misnumbered_unplanned_section_cannot_pass_pp04_structure():
    bridge = importlib.import_module("politics_fantasy.pan_iaen_cross_parser_audit")
    short = IAEN[0].replace(
        "4.22.- VIVIENDA\n"
        "4.22.1.- NORMAS APRO BADAS NO INCLUIDAS EN EL PLAN ANUAL\n"
        "- Real Decreto externo 2.\n",
        "",
    )
    with pytest.raises(bridge.FrameParseError, match="PP04_DUAL_PARSER_SECTION_4221_MISSING"):
        bridge.audit_pp04_dual_parsers(
            PAN, (short,), expected_plan_count=2, expected_planned_count=2,
            expected_approved_count=1,
            expected_planned_sections=(1,), expected_unplanned_count=2,
        )


def test_missing_expected_planned_ministry_cannot_pass_matching_aggregate_totals():
    bridge = importlib.import_module("politics_fantasy.pan_iaen_cross_parser_audit")
    with pytest.raises(bridge.FrameParseError, match="EXPECTED_MINISTRY_SECTIONS_MISSING"):
        bridge.audit_pp04_dual_parsers(
            PAN, IAEN, expected_plan_count=2, expected_planned_count=2,
            expected_approved_count=1,
            expected_planned_sections=(1, 2), expected_unplanned_count=2,
        )


def test_missing_expected_unplanned_entries_cannot_pass_matching_planned_totals():
    bridge = importlib.import_module("politics_fantasy.pan_iaen_cross_parser_audit")
    with pytest.raises(bridge.FrameParseError, match="UNPLANNED_COUNT_MISMATCH"):
        bridge.audit_pp04_dual_parsers(
            PAN, IAEN, expected_plan_count=2, expected_planned_count=2,
            expected_approved_count=1,
            expected_planned_sections=(1,), expected_unplanned_count=3,
        )
