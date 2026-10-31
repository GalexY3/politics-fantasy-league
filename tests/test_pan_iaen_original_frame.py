"""Synthetic page-text fixtures for a strictly local PAN/IAEN frame audit.

No Spanish original is bundled with this test suite. Runtime originals live
outside Git, and these tests cannot authenticate a real-world source.
"""
import pytest

from politics_fantasy.pan_iaen_original_frame import (
    FrameParseError, parse_pan_objective_ministry_pairs,
    parse_iaen_ministry_bullets, summarise_local_frame,
)


def mini_plan():
    return (
        "Intro title and total 999 (not data)",
        "PLAN ANUAL NORMATIVO\nLEY A\nObjetivo: Actuación a\nMinisterio: MINISTERIO A\n"
        "Coproponentes: MINISTERIO B\nREAL DECRETO B\nObjetivo: Actuación b\n",
        "Ministerio: MINISTERIO B\nREAL DECRETO C\nObjetivo: Actuación c\nMinisterio: MINISTERIO C\n",
    )


def mini_report():
    return (
        "1. INTRODUCCION\n- una lista fuera del seguimiento\n",
        "4.1.- MINISTERIO A\n4.1.1.- INICIATIVAS NORMATIVAS INCLUIDAS EN EL PLAN ANUAL\n"
        "I. Aprobadas\n- Ley A\nPublicado como: Ley 1/2025\n",
        "II. Pendientes de aprobación\n- Real Decreto B\n"
        "4.1.2.- NORMAS APROB ADAS NO I NCLUIDAS EN EL PLAN ANUAL\n- RD no previsto\n",
        # This actual-style numbering anomaly MUST use the descriptor, not .1.
        "4.22.- VIVIENDA\n4.22.1.- NORMAS APRO BADAS NO INCLUIDAS EN EL PLAN ANUAL\n"
        "- RD no previsto de Vivienda\n5. REALES DECRETOS-LEYES\n- no contar\n",
    )


def test_pan_pairs_cross_page_without_multiplying_coproponents():
    items = parse_pan_objective_ministry_pairs(mini_plan(), start_page_index=1)
    assert len(items) == 3
    assert [row["ordinal"] for row in items] == [1, 2, 3]
    assert [row["objective_pdf_page"] for row in items] == [2, 2, 3]
    assert [row["ministry_pdf_page"] for row in items] == [2, 3, 3]
    assert len(set(row["source_local_key"] for row in items)) == 3
    assert all(row["independent_official_item_id"] is None for row in items)


def test_missing_ministry_or_backward_pair_is_rejected():
    broken = ("Objetivo: A\nObjetivo: B\nMinisterio: M1\n",)
    with pytest.raises(FrameParseError, match="COUNT_MISMATCH"):
        parse_pan_objective_ministry_pairs(broken)
    broken = ("Ministerio: M1\nObjetivo: A\n",)
    with pytest.raises(FrameParseError, match="ORDER_VIOLATION"):
        parse_pan_objective_ministry_pairs(broken)


def test_report_heading_semantics_precede_section_number():
    result = parse_iaen_ministry_bullets(mini_report(), start_page_index=1)
    rows = result["rows"]
    assert len(rows) == 4
    assert [r["population"] for r in rows] == [
        "PLANNED", "PLANNED", "UNPLANNED", "UNPLANNED",
    ]
    assert [r["status_in_report"] for r in rows] == [
        "APPROVED_AS_OF_REPORT", "PENDING_UNSPECIFIED_AS_OF_REPORT",
        "UNPLANNED_ADOPTED", "UNPLANNED_ADOPTED",
    ]
    assert result["unplanned_misnumbered_sections"] == ["4.22.1"]
    assert result["departments_with_planned_section"] == ["1"]


def test_ambiguous_heading_fails_closed_not_by_section_number():
    text = (
        "4.1.- DEPT\n4.1.1.- ACTIVIDAD NORMATIVA\n- Real Decreto\n",
    )
    with pytest.raises(FrameParseError, match="UNRECOGNIZED_SECTION_HEADING"):
        parse_iaen_ministry_bullets(text)


def test_no_crosswalk_inferred_from_identical_titles():
    plan = parse_pan_objective_ministry_pairs(mini_plan(), start_page_index=1)
    report = parse_iaen_ministry_bullets(mini_report(), start_page_index=1)
    summary = summarise_local_frame(plan, report)
    assert summary["pan_item_candidates"] == 3
    assert summary["report_planned_documentary_entries"] == 2
    assert summary["report_unplanned_documentary_entries"] == 2
    assert summary["report_approved_planned_entries"] == 1
    assert summary["item_level_crosswalk_authenticated"] is False
    assert summary["individual_source_first_public_at"] is None
    assert summary["statistical_estimand_admitted"] is False
    assert summary["scientific_AB_cycles"] == 0


def test_report_approval_status_not_retrojected_to_plan_start():
    result = parse_iaen_ministry_bullets(mini_report(), start_page_index=1)
    assert result["rows"][0]["status_in_report"] == "APPROVED_AS_OF_REPORT"
    assert result["rows"][0]["status_known_in_2024"] is None
    assert all(r["first_public_at"] is None for r in result["rows"])


def test_report_section_number_must_match_department():
    text = ("4.1.- DEPT\n4.2.1.- INICIATIVAS NORMATIVAS INCLUIDAS EN EL PLAN\n- Ley\n",)
    with pytest.raises(FrameParseError, match="DEPARTMENT_SECTION_MISMATCH"):
        parse_iaen_ministry_bullets(text)


def test_unknown_report_entry_status_is_not_fabricated():
    text = ("4.1.- DEPT\n4.1.1.- INICIATIVAS NORMATIVAS INCLUIDAS EN EL PLAN\n- Ley\n",)
    with pytest.raises(FrameParseError, match="PLANNED_BULLET_NO_STATUS"):
        parse_iaen_ministry_bullets(text)
