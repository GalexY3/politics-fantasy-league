"""Fail-closed comparison of two PP04 documentary parsers on identical text.

These parser implementations originate in sibling PR #11 and PR #12. Their
agreement on *aggregates* is not independent evidence about the source or an
item-level PAN/IAEN match. The caller supplies already bounded page text;
there is no network, PDF reader, output writer, or access-rights evaluation.
"""
from __future__ import annotations

from collections import Counter

from .pan_iaen_original_frame import (
    FrameParseError,
    parse_iaen_ministry_bullets,
    parse_pan_objective_ministry_pairs,
    parse_plan_candidate_blocks,
    parse_report_ministry_listings,
)
from .procedural_index_contract import GateError


_MODERN_STATUS_TO_BLOCK = {
    "APPROVED_AS_OF_REPORT": "APPROVED_AS_REPORTED",
    "PENDING_UNSPECIFIED_AS_OF_REPORT": "PENDING_APPROVAL_UNSPLIT",
}


def audit_pp04_dual_parsers(
    pan_section_pages: tuple[str, ...],
    iaen_section_pages: tuple[str, ...],
    *,
    expected_plan_count: int,
    expected_planned_count: int,
    expected_approved_count: int,
    expected_planned_sections: tuple[int, ...],
    expected_unplanned_count: int,
) -> dict:
    """Audit bounded, source-local count/status agreement, never item identity.

    PAN inputs must already be restricted to its initiative section. Both
    implementations receive *exactly the same* text. Agreement is therefore
    an internal robustness check, not two independent documentary witnesses.
    """
    if (type(pan_section_pages) is not tuple
            or type(iaen_section_pages) is not tuple
            or type(expected_plan_count) is not int
            or type(expected_planned_count) is not int
            or type(expected_approved_count) is not int
            or type(expected_unplanned_count) is not int
            or type(expected_planned_sections) is not tuple
            or not expected_planned_sections
            or any(type(n) is not int or not 1 <= n <= 99
                   for n in expected_planned_sections)
            or tuple(sorted(set(expected_planned_sections)))
               != expected_planned_sections
            or not 0 <= expected_approved_count <= expected_planned_count <= 700
            or not 0 <= expected_unplanned_count <= 3000
            or not 1 <= expected_plan_count <= 500):
        raise FrameParseError("PP04_DUAL_PARSER_BAD_INPUT")

    try:
        block_plan = parse_plan_candidate_blocks(
            pan_section_pages, expected_count=expected_plan_count,
        )
        line_plan = parse_pan_objective_ministry_pairs(pan_section_pages)
        block_report = parse_report_ministry_listings(
            iaen_section_pages, expected_total=expected_planned_count,
            expected_approved=expected_approved_count,
        )
        line_report = parse_iaen_ministry_bullets(iaen_section_pages)
    except (GateError, FrameParseError) as exc:
        # Do not interpolate snippets of confidential PDF text into errors.
        raise FrameParseError("PP04_DUAL_PARSER_REJECTED") from exc

    line_planned = [r for r in line_report["rows"]
                    if r["population"] == "PLANNED"]
    line_status = Counter(r["status_in_report"] for r in line_planned)
    block_status = Counter(r["source_listing_heading"]
                           for r in block_report["rows"])

    if (len(line_plan) != len(block_plan)
            or len(line_planned) != block_report["planned_listing_count"]
            or line_status["APPROVED_AS_OF_REPORT"]
               != block_status["APPROVED_AS_REPORTED"]
            or line_status["PENDING_UNSPECIFIED_AS_OF_REPORT"]
               != block_status["PENDING_APPROVAL_UNSPLIT"]
            or block_status["DESISTED_AS_REPORTED"] != 0):
        raise FrameParseError("PP04_DUAL_PARSER_AGGREGATE_MISMATCH")

    # Count by department and *documentary* heading, not by title/ordinal.
    # Two incorrect parsers could still agree; a false positive here cannot
    # authenticate an actual item crosswalk or historical first publication.
    block_sections = Counter((str(r["source_ministry_section"]),
                              r["source_listing_heading"])
                             for r in block_report["rows"])
    try:
        line_sections = Counter((r["department_number"],
                                 _MODERN_STATUS_TO_BLOCK[r["status_in_report"]])
                                for r in line_planned)
    except KeyError as exc:
        raise FrameParseError("PP04_DUAL_PARSER_UNKNOWN_STATUS") from exc
    if block_sections != line_sections:
        raise FrameParseError("PP04_DUAL_PARSER_SECTION_STATUS_MISMATCH")

    misnumbered_line = "4.22.1" in line_report["unplanned_misnumbered_sections"]
    nonplanned_block = 22 in block_report["nonplanned_section_numbers"]
    if misnumbered_line != nonplanned_block:
        raise FrameParseError("PP04_DUAL_PARSER_NONPLANNED_HEADING_MISMATCH")
    if not misnumbered_line:
        raise FrameParseError("PP04_DUAL_PARSER_SECTION_4221_MISSING")
    if any(row["department_number"] == "22" for row in line_planned):
        raise FrameParseError("PP04_DUAL_PARSER_NONPLANNED_ENTERED_PLAN")

    if (block_report["planned_ministry_sections"]
            != list(expected_planned_sections)
            or tuple(int(n) for n in line_report["departments_with_planned_section"])
               != expected_planned_sections):
        raise FrameParseError("PP04_DUAL_PARSER_EXPECTED_MINISTRY_SECTIONS_MISSING")
    unplanned_count = sum(r["population"] == "UNPLANNED"
                          for r in line_report["rows"])
    if unplanned_count != expected_unplanned_count:
        raise FrameParseError("PP04_DUAL_PARSER_UNPLANNED_COUNT_MISMATCH")

    return {
        "schema": "pfl.pp04.dual_parser_documentary_consistency.v1",
        "count_and_section_status_agreement": True,
        "plan_candidate_count": len(line_plan),
        "planned_count": len(line_planned),
        "approved_count": line_status["APPROVED_AS_OF_REPORT"],
        "pending_unsplit_count": line_status["PENDING_UNSPECIFIED_AS_OF_REPORT"],
        "not_included_4221_excluded": True,
        "expected_planned_sections_source_internal": list(expected_planned_sections),
        "expected_ministry_sections_matched": True,
        "expected_unplanned_count_matched": True,
        "line_parser_unplanned_entries_source_local": unplanned_count,
        "count_is_source_internal_only": True,
        "two_parsers_are_independent_sources": False,
        "item_crosswalk_verified": False,
        "first_public_at_verified": False,
        "source_rights_independently_verified": False,
        "independent_all_received_denominator_attested": False,
        "statistical_estimand_admitted": False,
        "R5": "STOP",
        "scientific_AB_cycles": 0,
    }
