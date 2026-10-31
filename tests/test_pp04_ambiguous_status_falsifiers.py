"""Contradictory IAEN section heading must never acquire a single status."""

import pytest

from politics_fantasy.pan_iaen_original_frame import (
    FrameParseError,
    parse_iaen_ministry_bullets,
    parse_report_ministry_listings,
)
from politics_fantasy.pan_iaen_cross_parser_audit import audit_pp04_dual_parsers
from politics_fantasy.procedural_index_contract import GateError


PAN = ("REAL DECRETO A\nObjetivo: prueba\nMinisterio: A\n",)
IAEN = (
    "4.1.- DEPARTAMENTO A\n"
    "4.1.1.- INICIATIVAS NORMATIVAS INCLUIDAS EN EL PLAN ANUAL\n"
    "II. Pendientes de aprobación y Aprobadas\n"
    "- Real Decreto A.\n"
    "4.1.2.- NORMAS NO INCLUIDAS EN EL PLAN ANUAL\n"
    "- Real Decreto externo.\n"
    "4.22.- VIVIENDA\n"
    "4.22.1.- NORMAS NO INCLUIDAS EN EL PLAN ANUAL\n"
    "- Real Decreto externo 2.\n"
    "5. REALES DECRETOS-LEYES\n",
)


def test_line_parser_rejects_two_status_labels_in_one_heading():
    with pytest.raises(FrameParseError, match="UNSUPPORTED_PLANNED_STATUS_HEADING"):
        parse_iaen_ministry_bullets(IAEN)


def test_block_parser_rejects_two_status_labels_in_one_heading():
    with pytest.raises(GateError, match="IAEN_UNKNOWN_HEADING_CLASS"):
        parse_report_ministry_listings(
            IAEN, expected_total=1, expected_approved=0,
        )


def test_dual_agreement_cannot_promote_a_shared_misclassification():
    with pytest.raises(FrameParseError, match="PP04_DUAL_PARSER_REJECTED"):
        audit_pp04_dual_parsers(
            PAN, IAEN, expected_plan_count=1, expected_planned_count=1,
            expected_approved_count=0,
            expected_planned_sections=(1,), expected_unplanned_count=2,
        )
