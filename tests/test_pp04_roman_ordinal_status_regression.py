"""PP04C: editorial stage number must match its documentary category.

All page strings are invented fixtures, not extracts from the PAN/IAEN PDFs.
The assertion is specific to the IAEN2024 I/II heading contract.
"""

import pytest

from politics_fantasy.pan_iaen_original_frame import (
    FrameParseError, parse_iaen_ministry_bullets,
    parse_report_ministry_listings,
)
from politics_fantasy.pan_iaen_cross_parser_audit import audit_pp04_dual_parsers
from politics_fantasy.procedural_index_contract import GateError


PAN = (
    "REAL DECRETO A\nObjetivo: alfa\nMinisterio: A\n"
    "LEY B\nObjetivo: beta\nMinisterio: B\n",
)


def iaen(first: str, second: str) -> tuple[str, ...]:
    return (
        "4.1.- DEPARTAMENTO A\n"
        "4.1.1.- INICIATIVAS NORMATIVAS INCLUIDAS EN EL PLAN ANUAL\n"
        + first + "\n- Real Decreto alfa.\n"
        + second + "\n- Ley beta.\n"
        "4.1.2.- NORMAS NO INCLUIDAS EN EL PLAN ANUAL\n"
        "- Real Decreto externo.\n"
        "4.22.- VIVIENDA\n"
        "4.22.1.- NORMAS NO INCLUIDAS EN EL PLAN ANUAL\n"
        "- Real Decreto externo 2.\n"
        "5. REALES DECRETOS-LEYES\n",
    )


@pytest.mark.parametrize("bad_first,bad_second", [
    ("I. Pendientes de aprobación", "II. Aprobadas"),
    ("I. Pendientes de aprobación", "II. Pendientes de aprobación"),
    ("I. Aprobadas", "II. Aprobadas"),
])
def test_both_parsers_reject_ordinal_label_mismatch(bad_first, bad_second):
    fixture = iaen(bad_first, bad_second)
    with pytest.raises(FrameParseError, match="IAEN_STAGE_ORDINAL_LABEL_MISMATCH"):
        parse_iaen_ministry_bullets(fixture)
    with pytest.raises(GateError, match="IAEN_STAGE_ORDINAL_LABEL_MISMATCH"):
        parse_report_ministry_listings(fixture, expected_total=2, expected_approved=1)
    with pytest.raises(FrameParseError, match="PP04_DUAL_PARSER_REJECTED"):
        audit_pp04_dual_parsers(
            PAN, fixture, expected_plan_count=2, expected_planned_count=2,
            expected_approved_count=1, expected_planned_sections=(1,),
            expected_unplanned_count=2,
        )


def test_valid_roman_categories_preserve_planned_unplanned_separation():
    fixture = iaen("I. Aprobadas", "II. Pendientes de aprobación")
    report = audit_pp04_dual_parsers(
        PAN, fixture, expected_plan_count=2, expected_planned_count=2,
        expected_approved_count=1, expected_planned_sections=(1,),
        expected_unplanned_count=2,
    )
    assert report["planned_count"] == 2
    assert report["approved_count"] == 1
    assert report["pending_unsplit_count"] == 1
    assert report["line_parser_unplanned_entries_source_local"] == 2
    assert report["item_crosswalk_verified"] is False
    assert report["R5"] == "STOP"


def test_valid_labels_but_reversed_section_order_are_not_a_clean_frame():
    # Both ordinals have the correct labels individually; the order is wrong.
    fixture = iaen("II. Pendientes de aprobación", "I. Aprobadas")
    with pytest.raises(FrameParseError, match="IAEN_STAGE_ORDER_MISMATCH"):
        parse_iaen_ministry_bullets(fixture)
    with pytest.raises(GateError, match="IAEN_STAGE_ORDER_MISMATCH"):
        parse_report_ministry_listings(fixture, expected_total=2, expected_approved=1)
