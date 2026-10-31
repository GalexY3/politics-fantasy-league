"""Local structural audit of public PAN/IAEN *text*, not a scientific join.

No network or PDF reader is imported by this module. The caller is responsible
for official-version byte authentication, page extraction, user rights and an
off-Git storage path. Every row represents a DOCUMENTARY TEXT ANCHOR, not an
authenticated independent initiative ID, process outcome or causal effect.

The 2024 PAN includes ministry counts in its statistical tables: only the
separately bounded main initiative section is eligible for item segmentation.
IAEN 2024 also has a numbered 4.22.1 section whose *heading* says NO INCLUIDAS.
Textual semantics must take precedence over the section-number suffix.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import re
from typing import Sequence


class FrameParseError(ValueError):
    """Evidence cannot support the required documentary segmentation."""


MAX_PAGES = 300
MAX_ROWS = 3000
_PAN_OBJECTIVE = re.compile(r"^\s*Objetivo:")
_PAN_MINISTRY = re.compile(r"^\s*Ministerio:")
_DEPARTMENT = re.compile(r"^\s*4\.(\d{1,2})\.-\s*(.*)")
_SUBSECTION = re.compile(r"^\s*4\.(\d{1,2})\.(\d+)\.-\s*(.*)")
_ROMAN_STATUS = re.compile(r"^\s*[IVX]+\.\s+(.+)", flags=re.I)
_BULLET = re.compile(r"^\s*-\s+\S")
_END_REPORT = re.compile(r"^\s*5\.\s*REALES\s+DECRETOS\s*[- ]\s*LEYES", re.I)


def _pages(pages: Sequence[str], start: int) -> None:
    if (type(pages) not in (tuple, list) or len(pages) > MAX_PAGES
            or type(start) is not int or start < 0 or start >= len(pages)
            or any(type(x) is not str or len(x) > 1_000_000 for x in pages)):
        raise FrameParseError("BOUNDED_PAGE_TEXT_REQUIRED")


def _text_digest(text: str) -> str:
    return sha256(text.encode("utf-8", errors="strict")).hexdigest()


def parse_pan_objective_ministry_pairs(
    pages: Sequence[str], *, start_page_index: int = 0,
) -> list[dict]:
    """Pair source-adjacent Objective:/Ministerio: anchors in a bounded part.

    Counting all `Ministerio:` occurrences across the PDF overcounts by 1 in
    PAN2024 because an earlier table is not a project entry. Coproponentes is
    a relationship attribute, never a second initiative. This returns no
    official individual identifier and performs no cross-document matching.
    """
    _pages(pages, start_page_index)
    objectives: list[tuple[tuple[int, int], str]] = []
    ministries: list[tuple[tuple[int, int], str]] = []
    for pno in range(start_page_index, len(pages)):
        for lineno, line in enumerate(pages[pno].splitlines(), start=1):
            if _PAN_OBJECTIVE.match(line):
                objectives.append(((pno, lineno), line.strip()))
            if _PAN_MINISTRY.match(line):
                ministries.append(((pno, lineno), line.strip()))
    if not objectives or len(objectives) != len(ministries) or len(objectives) > MAX_ROWS:
        raise FrameParseError("PAN_OBJECTIVE_MINISTRY_COUNT_MISMATCH")
    output = []
    for idx, ((o_at, objective), (m_at, ministry)) in enumerate(zip(objectives, ministries)):
        next_o_at = objectives[idx + 1][0] if idx + 1 < len(objectives) else None
        if not (o_at < m_at and (next_o_at is None or m_at < next_o_at)):
            raise FrameParseError("PAN_OBJECTIVE_MINISTRY_ORDER_VIOLATION")
        # Source-local ordinal (stable only for this exact PDF byte edition).
        # Never advertise it as an externally conferred ID or a join key.
        output.append({
            "ordinal": idx + 1,
            "source_local_key": f"PAN2024_TEXT_ANCHOR_{idx+1:04d}",
            "objective_pdf_page": o_at[0] + 1,
            "objective_line": o_at[1],
            "ministry_pdf_page": m_at[0] + 1,
            "ministry_line": m_at[1],
            "objective_line_text": objective,
            "ministry_line_text": ministry,
            "anchor_pair_sha256": _text_digest(objective + "\n" + ministry),
            "independent_official_item_id": None,
            "verified_plan_edition_first_public_at": None,
            "authenticated_iaen_reference": None,
            "item_level_status": "UNKNOWN_UNTIL_VERIFIED_CROSSWALK",
        })
    return output


def _heading_population(line: str) -> str:
    # PDF text extraction sometimes breaks individual letters into spaces.
    # Removing all whitespace before testing prevents NOT INCLUDED from being
    # falsely assigned to INCLUDED (substring bug).
    compact = re.sub(r"\s+", "", line).upper()
    if "NOINCLUIDAS" in compact and "NORMAS" in compact:
        return "UNPLANNED"
    if "INCLUIDAS" in compact and "INICIATIVAS" in compact and "NOINCLUIDAS" not in compact:
        return "PLANNED"
    raise FrameParseError("IAEN_UNRECOGNIZED_SECTION_HEADING")


def _heading_status(line: str) -> str | None:
    m = _ROMAN_STATUS.match(line)
    if not m:
        return None
    compact = re.sub(r"\s+", "", m.group(1)).upper()
    if "PENDIENTESDEAPROBACI" in compact:
        return "PENDING_UNSPECIFIED_AS_OF_REPORT"
    if "APROBADAS" in compact:
        return "APPROVED_AS_OF_REPORT"
    return None


def parse_iaen_ministry_bullets(
    pages: Sequence[str], *, start_page_index: int = 0,
) -> dict:
    """Parse section 4 ministry entry anchors without inferring outcomes.

    "Approved" and "pending" are IAEN documentary labels as of its later
    preparation/approval, NOT verified legal states at the start of 2024.
    The finer categories 'en tramitación' and 'desistida' from a global chart
    are never projected onto individual pending bullet rows.
    """
    _pages(pages, start_page_index)
    department: str | None = None
    population: str | None = None
    section_id: str | None = None
    status: str | None = None
    started = False
    ended = False
    rows = []
    planned_departments: set[str] = set()
    unplanned_number_anomalies: set[str] = set()
    section_count = 0
    for pno in range(start_page_index, len(pages)):
        for lineno, line in enumerate(pages[pno].splitlines(), start=1):
            if _END_REPORT.match(line):
                if started:
                    ended = True
                    break
                continue
            dep = _DEPARTMENT.match(line)
            if dep:
                department = dep.group(1)
                population = None
                section_id = None
                status = None
                started = True
                continue
            sub = _SUBSECTION.match(line)
            if sub:
                if department is None or sub.group(1) != department:
                    raise FrameParseError("IAEN_DEPARTMENT_SECTION_MISMATCH")
                section_id = f"4.{sub.group(1)}.{sub.group(2)}"
                population = _heading_population(sub.group(3))
                status = None
                section_count += 1
                if population == "PLANNED":
                    planned_departments.add(department)
                if population == "UNPLANNED" and sub.group(2) == "1":
                    unplanned_number_anomalies.add(section_id)
                continue
            header_status = _heading_status(line)
            if header_status is not None and population == "PLANNED":
                status = header_status
            if _BULLET.match(line) and population is not None:
                if len(rows) >= MAX_ROWS:
                    raise FrameParseError("IAEN_TOO_MANY_DOCUMENTARY_ENTRIES")
                if population == "PLANNED" and status is None:
                    raise FrameParseError("IAEN_PLANNED_BULLET_NO_STATUS")
                label = status if population == "PLANNED" else "UNPLANNED_ADOPTED"
                rows.append({
                    "source_local_key": f"IAEN2024_ANCHOR_{len(rows)+1:04d}",
                    "population": population,
                    "department_number": department,
                    "section_id": section_id,
                    "pdf_page": pno + 1,
                    "line": lineno,
                    "bullet_line_text": line.strip(),
                    "bullet_line_sha256": _text_digest(line.strip()),
                    "status_in_report": label,
                    "status_known_in_2024": None,
                    "first_public_at": None,
                    "verified_legal_instrument_id": None,
                    "authenticated_pan_item_link": None,
                })
        if ended:
            break
    if not started or not ended or not section_count:
        raise FrameParseError("IAEN_SECTION4_BOUNDS_NOT_ATTESTED")
    return {
        "rows": rows,
        "subsection_count": section_count,
        "departments_with_planned_section": sorted(planned_departments, key=int),
        "unplanned_misnumbered_sections": sorted(unplanned_number_anomalies),
        "section4_endpoint_found": ended,
    }


def summarise_local_frame(plan: list[dict], report: dict) -> dict:
    """Summarize documentary rows only; crosswalk is intentionally ZERO."""
    rows = report["rows"]
    pop = Counter(r["population"] for r in rows)
    status = Counter(r["status_in_report"] for r in rows)
    return {
        "schema": "pfl.pan_iaen2024.local_document_frame.v1",
        "evidence_class": "OFFICIAL_PDF_TEXT_ANCHORS_UNVERIFIED_ITEM_IDENTITY",
        "pan_item_candidates": len(plan),
        "report_planned_documentary_entries": pop["PLANNED"],
        "report_unplanned_documentary_entries": pop["UNPLANNED"],
        "report_approved_planned_entries": status["APPROVED_AS_OF_REPORT"],
        "report_pending_unspecified_planned_entries": status["PENDING_UNSPECIFIED_AS_OF_REPORT"],
        "unplanned_misnumbered_sections": report["unplanned_misnumbered_sections"],
        "report_planned_ministries_with_rows": len(report["departments_with_planned_section"]),
        "item_level_crosswalk_authenticated": False,
        "independent_registered_entry_population_attested": False,
        "individual_source_first_public_at": None,
        "report_status_not_historical_2024_predictor": True,
        "inferred_rejects_or_failures": 0,
        "statistical_estimand_admitted": False,
        "R5": "STOP",
        "scientific_AB_cycles": 0,
    }
