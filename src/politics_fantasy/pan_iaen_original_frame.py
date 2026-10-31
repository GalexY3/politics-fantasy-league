"""Local-only documentary census *candidates* from the two authorized PDFs.

Forensic/source-engineering utility; NOT an empirical scientific data admission.
The source PDFs and the resulting row-level extracts remain outside Git. The
extractor does not match PAN to IAEN by title or ministry and does not assert
an item-level outcome, a historical first-public timestamp, or R5 clearance.
"""
from __future__ import annotations

from bisect import bisect_right
from collections import Counter
from hashlib import sha256
from pathlib import Path
import re

from .procedural_index_contract import GateError


PAN_SOURCE_SHA256 = "49de70b656da1b9ed9c68f552eafe743bede253e5b7a725d5eb615db1b61b4c5"
IAEN_SOURCE_SHA256 = "7c77a73480f3f039d8ba069e12301b7a4c7ad0eeec85934ec84721526cb88aa2"

_OBJECTIVE = re.compile(r"(?m)^[ \t]*Objetivo\s*:")
_MINISTRY = re.compile(r"(?m)^[ \t]*Ministerio\s*:")
_TITLE_START = re.compile(
    r"(?mi)^[ \t]*(?:LEY(?:[ \t]+ORG[ÁA]NICA)?|REAL[ \t]+DECRETO|"
    r"PROYECTO(?:[ \t]+DE[ \t]+LEY)?|ANTEPROYECTO)[ \t]+"
)
_REPORT_SECTION = re.compile(r"(?m)^[ \t]*4\.(\d{1,2})\.1\.[ \t]*-[ \t]*")
_BULLET = re.compile(r"(?mi)^[ \t]*-[ \t]+(?=(?:Real[ \t]+Decreto|Ley|Proyecto|Anteproyecto))")
_STAGE = re.compile(
    r"(?mi)^[ \t]*(?:I|II|III)\.[ \t]*(Aprobadas|Pendientes[ \t]+de[ \t]+aprobaci[oó]n|Desistidas)"
)
_SOURCE_PAGE = re.compile(r"^\s*\d{1,3}\s*$")
MAX_PAGE_CHARS = 200_000
MAX_PAGES = 300


def _text_and_pages(page_texts: tuple[str, ...]) -> tuple[str, list[int]]:
    if (type(page_texts) is not tuple or not 1 <= len(page_texts) <= MAX_PAGES
            or any(type(x) is not str or len(x) > MAX_PAGE_CHARS for x in page_texts)):
        raise GateError("PP04_BOUNDED_PAGE_TEXT_REQUIRED")
    offsets = []
    total = 0
    for page in page_texts:
        offsets.append(total)
        total += len(page) + 1
    return "\n".join(page_texts), offsets


def _page(offset: int, starts: list[int]) -> int:
    return bisect_right(starts, offset)  # one-based PDF page number


def _clean(raw: str) -> str:
    return " ".join(raw.split())


def _rank_from_title(title: str) -> str:
    normalized = title.upper()
    if normalized.startswith("LEY ORG"):
        return "LEY_ORGANICA"
    if normalized.startswith("LEY "):
        return "LEY"
    if normalized.startswith("REAL DECRETO"):
        return "REAL_DECRETO"
    return "UNKNOWN_RANK"


def rank_counts(rows: list[dict], *, approved_only: bool = False) -> dict[str, int]:
    relevant = (x for x in rows if not approved_only or
                x.get("source_listing_heading") == "APPROVED_AS_REPORTED")
    return dict(sorted(Counter(_rank_from_title(x["title_candidate"])
                               for x in relevant).items()))


def parse_plan_candidate_blocks(page_texts: tuple[str, ...],
                                *, expected_count: int,
                                first_pdf_page: int = 1) -> list[dict]:
    """Bound 1 marker-pair per candidate, without promoting publisher IDs.

    The caller is responsible for passing the Section 9 PAN pages only. A
    successful cardinality test is an *internal source witness*, not proof of
    population coverage outside this particular plan edition.
    """
    if (type(expected_count) is not int or not 0 <= expected_count <= 500
            or type(first_pdf_page) is not int or not 1 <= first_pdf_page <= MAX_PAGES):
        raise GateError("PP04_EXPECTED_COUNT_INVALID")
    text, starts = _text_and_pages(page_texts)
    objectives = list(_OBJECTIVE.finditer(text))
    ministries = list(_MINISTRY.finditer(text))
    if len(objectives) != expected_count or len(ministries) != expected_count:
        raise GateError("PAN_MARKER_DENOMINATOR_MISMATCH")
    rows = []
    prior_ministry_end = 0
    for ix, (objective, ministry) in enumerate(zip(objectives, ministries), start=1):
        next_obj = objectives[ix].start() if ix < len(objectives) else len(text)
        if (not prior_ministry_end <= objective.start() < ministry.start()
                or not ministry.end() <= next_obj):
            raise GateError("PAN_OBJECTIVE_MINISTRY_PAIRING_UNSUPPORTED")
        title_region = text[prior_ministry_end:objective.start()]
        title_starts = list(_TITLE_START.finditer(title_region))
        title_raw = (title_region[title_starts[-1].start():] if title_starts
                     else title_region[-300:])
        title = _clean(title_raw)
        ministry_line = text[ministry.end():].split("\n", 1)[0].strip()
        rows.append({
            "source_local_ordinal": ix,
            "source_pdf_page": first_pdf_page - 1 + _page(objective.start(), starts),
            "ministry_line_candidate": ministry_line,
            "title_candidate": title,
            "objective_text_source_only": _clean(text[objective.end():ministry.start()]),
            "title_requires_visual_review": (not bool(title_starts) or len(title) > 400),
            "identity_authentication": False,
            "publisher_stable_id_verified": False,
            "outcome": None,
            "first_public_at": None,
        })
        prior_ministry_end = ministry.end()
    return rows


def _heading_class(text: str) -> str:
    compact = re.sub(r"[^A-Z0-9]", "", text[:230].upper())
    if "NOINCLUIDAS" in compact:
        return "NONPLANNED"
    if "INICIATIVASNORMATIVASINCLUIDAS" in compact:
        return "PLANNED"
    raise GateError("IAEN_UNRECOGNIZED_MINISTRY_SECTION_ROLE")


def _section_end(text: str, start: int, section_no: int) -> int:
    # The source's section 4.22.1 is nonplanned and has no 4.22.2 header.
    patterns = [
        rf"(?m)^[ \t]*4\.{section_no}\.2\.[ \t]*-[ \t]*",
        rf"(?m)^[ \t]*4\.{section_no + 1}\.[ \t]*-[ \t]*",
        r"(?m)^[ \t]*5\.[ \t]+REALES[ \t]+DECRETOS[ \t]*-[ \t]*LEYES",
    ]
    ends = [m.start() + start for p in patterns
            if (m := re.search(p, text[start:], flags=re.I))]
    return min(ends) if ends else len(text)


def parse_report_ministry_listings(page_texts: tuple[str, ...],
                                   *, expected_total: int,
                                   expected_approved: int) -> dict:
    """Extract only planned ministerial listings in IAEN section 4.n.1.

    A row under "Pendientes de aprobación" cannot be further classified as
    "in process", "not started", or "desisted" from this heading alone.
    Neither an IAEN list entry nor equal counts proves item PAN↔IAEN identity.
    """
    if (type(expected_total) is not int or type(expected_approved) is not int
            or not 0 <= expected_approved <= expected_total <= 700):
        raise GateError("PP04_EXPECTED_COUNT_INVALID")
    text, pages = _text_and_pages(page_texts)
    section_starts = list(_REPORT_SECTION.finditer(text))
    planned = []
    nonplanned = []
    rows = []
    for start in section_starts:
        section_no = int(start.group(1))
        end = _section_end(text, start.end(), section_no)
        if end <= start.end():
            raise GateError("IAEN_MINISTRY_SECTION_BOUNDS_INVALID")
        segment = text[start.start():end]
        cls = _heading_class(segment)
        if cls == "NONPLANNED":
            nonplanned.append(section_no)
            continue
        planned.append(section_no)
        heads = list(_STAGE.finditer(segment))
        bullets = list(_BULLET.finditer(segment))
        for j, bullet in enumerate(bullets):
            earlier = [h for h in heads if h.start() < bullet.start()]
            if not earlier:
                raise GateError("IAEN_UNCLASSIFIED_PLANNED_LISTING")
            status_label = earlier[-1].group(1).lower()
            if "aprobadas" in status_label:
                status = "APPROVED_AS_REPORTED"
            elif "pendientes" in status_label:
                status = "PENDING_APPROVAL_UNSPLIT"
            elif "desistidas" in status_label:
                status = "DESISTED_AS_REPORTED"
            else:
                raise GateError("IAEN_UNKNOWN_HEADING_CLASS")
            next_bullet = bullets[j + 1].start() if j + 1 < len(bullets) else len(segment)
            block = segment[bullet.start():next_bullet]
            heading = re.split(r"(?mi)^[ \t]*(?:Publicado[ \t]+como|Observaciones)[ \t]*:", block, maxsplit=1)[0]
            title = _clean(heading.lstrip(" \t\n-"))
            rows.append({
                "source_local_ordinal": len(rows) + 1,
                "source_ministry_section": section_no,
                "source_pdf_page": _page(start.start() + bullet.start(), pages),
                "title_candidate": title,
                "title_requires_visual_review": len(title) > 400,
                "source_listing_heading": status,
                "source_block_private": _clean(block),
                "publisher_stable_id_verified": False,
                "policy_outcome_causally_attributed": False,
                "first_public_at": None,
            })
    statuses = Counter(row["source_listing_heading"] for row in rows)
    if (len(rows) != expected_total
            or statuses["APPROVED_AS_REPORTED"] != expected_approved):
        raise GateError("IAEN_LISTING_DENOMINATOR_MISMATCH")
    return {
        "planned_listing_count": len(rows),
        "approved_listing_count": statuses["APPROVED_AS_REPORTED"],
        "pending_approval_listing_count": statuses["PENDING_APPROVAL_UNSPLIT"],
        "desisted_listing_count": statuses["DESISTED_AS_REPORTED"],
        "planned_ministry_sections": sorted(planned),
        "not_included_ministry_sections": len(nonplanned),
        "nonplanned_section_numbers": sorted(nonplanned),
        "status_granularity": "APPROVED_VS_PENDING_APPROVAL_ONLY",
        "first_public_at_verified": False,
        "rows": rows,
    }


def reconcile_counts_without_crosswalk(plan_rows: list[dict],
                                       report: dict) -> dict:
    if type(plan_rows) is not list or type(report) is not dict:
        raise GateError("PP04_UNTRUSTED_CENSUS_INPUT")
    return {
        "schema": "pfl.pp04.source_internal_count_audit.v1",
        "plan_candidate_count": len(plan_rows),
        "report_planned_listing_count": report["planned_listing_count"],
        "report_approved_listing_count": report["approved_listing_count"],
        "report_pending_approval_listing_count": report["pending_approval_listing_count"],
        "internal_count_concordance": len(plan_rows) == report["planned_listing_count"],
        "item_crosswalk_verified": False,
        "item_level_success_rate_admissible": False,
        "join_cardinality": "UNKNOWN",
        "plan_year": 2024,
        "report_evaluated_year": 2024,
        "report_approved_year": 2025,
        "as_of_first_public_at": None,
        "source_rights_allow_redistribution": False,
        "source_unit_is_all_policies_in_spain": False,
        "R5": "STOP",
        "scientific_AB_cycles": 0,
    }


def verify_exact_original_sha256(path: Path, expected_sha256: str) -> str:
    if type(expected_sha256) is not str or not re.fullmatch("[0-9a-f]{64}", expected_sha256):
        raise GateError("PP04_BAD_SHA256_EXPECTATION")
    source = Path(path)
    if not source.is_file() or source.stat().st_size > 20_000_000:
        raise GateError("PP04_ORIGINAL_MISSING_OR_TOO_LARGE")
    digest = sha256()
    with source.open("rb") as f:
        while chunk := f.read(1 << 20):
            digest.update(chunk)
    if digest.hexdigest() != expected_sha256:
        raise GateError("PP04_SOURCE_ASSET_SHA256_MISMATCH")
    return digest.hexdigest()


def require_private_output_directory(path: Path, repository_root: Path) -> Path:
    out = Path(path).resolve()
    root = Path(repository_root).resolve()
    if out == root or root in out.parents:
        raise GateError("PP04_PRIVATE_OUTPUT_MUST_BE_OUTSIDE_REPO")
    return out
