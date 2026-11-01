"""A hyphenated editorial note is not an observed legal instrument."""

import pytest

from politics_fantasy.pan_iaen_original_frame import (
    FrameParseError,
    parse_iaen_ministry_bullets,
)
from politics_fantasy.pan_iaen_cross_parser_audit import audit_pp04_dual_parsers


PAN = ("REAL DECRETO A\nObjetivo: prueba\nMinisterio: A\n",)
IAEN = (
    "4.1.- DEPARTAMENTO A\n"
    "4.1.1.- INICIATIVAS NORMATIVAS INCLUIDAS EN EL PLAN ANUAL\n"
    "I. Aprobadas\n- Real Decreto A.\n"
    "4.1.2.- NORMAS NO INCLUIDAS EN EL PLAN ANUAL\n"
    "4.22.- VIVIENDA\n"
    "4.22.1.- NORMAS NO INCLUIDAS EN EL PLAN ANUAL\n"
    "- Real Decreto externo.\n"
    "- Nota editorial que no es una norma.\n"
    "5. REALES DECRETOS-LEYES\n",
)


def test_iaen_unplanned_note_is_not_counted_as_normative_entry():
    with pytest.raises(FrameParseError, match="IAEN_UNSUPPORTED_ENTRY_TYPE"):
        parse_iaen_ministry_bullets(IAEN)


def test_unplanned_note_does_not_make_two_parsers_appear_consistent():
    with pytest.raises(FrameParseError, match="PP04_DUAL_PARSER_REJECTED"):
        audit_pp04_dual_parsers(
            PAN, IAEN, expected_plan_count=1, expected_planned_count=1,
            expected_approved_count=1,
            expected_planned_sections=(1,), expected_unplanned_count=2,
        )
