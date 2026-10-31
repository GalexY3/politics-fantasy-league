"""Extract a LOCAL, PROVISIONAL PAN 2024 plan-item frame, not IAEN outcomes.

This bounded offline script ONLY reads an explicitly supplied PAN PDF with a
pinned SHA-256. It never opens the corresponding IAEN, contacts a website,
assigns official IDs, infers compliance or publishes a row. Use --out-dir only
outside the Git checkout. It deliberately stops on source drift or mismatches.

The synthetic parser is exposed for fixture tests; pypdf is used only by CLI.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re


SOURCE_SHA256 = "49de70b656da1b9ed9c68f552eafe743bede253e5b7a725d5eb615db1b61b4c5"
SOURCE_FILENAME = "PAN_2024.pdf"
EXPECTED_PDF_PAGES = 117
FIRST_PLAN_BODY_PAGE = 37  # 1-based, as observed in the PDF outline
EXPECTED_ITEM_COUNTS = {"ORGANIC_LAW": 6, "LAW": 43, "ROYAL_DECREE": 149}
SOURCE_PAGE = "https://transparencia.gob.es/publicidad-activa/por-materias/normativa-otras-disposiciones/plan-anual/plan-anual-2024"

OBJECTIVE = re.compile(r"(?m)^[ \t]*Objetivo[ \t]*:")
MINISTRY = re.compile(r"(?m)^[ \t]*Ministerio[ \t]*:")
TITLE_START = re.compile(r"(?m)^[ \t]*(LEY ORG.NICA|LEY[ \t]+|REAL DECRETO(?:[ \t]|$))[^\n]*")


class CohortGateError(ValueError):
    pass


def identify_plan_items(page_texts: tuple[tuple[int, str], ...]) -> tuple[dict, ...]:
    """Find source-local entries by objective/ministry anchors; no fake outcomes.

    A title's first line is only an unverified text-extraction fragment. This
    method cannot establish identity across editions or against IAEN/BOE.
    """
    if (type(page_texts) is not tuple or not page_texts or len(page_texts) > 250
            or any(type(p) is not tuple or len(p) != 2
                   or type(p[0]) is not int or p[0] < 1
                   or type(p[1]) is not str for p in page_texts)
            or any(page_texts[k][0] >= page_texts[k+1][0]
                   for k in range(len(page_texts)-1))):
        raise CohortGateError("PAN_INVALID_PAGE_ORDER_OR_INPUT")
    starts = []
    buffer = []
    offset = 0
    for page, content in page_texts:
        starts.append(offset)
        fragment = content + "\n"
        buffer.append(fragment)
        offset += len(fragment)
    text = "".join(buffer)
    objectives = list(OBJECTIVE.finditer(text))
    ministries = list(MINISTRY.finditer(text))
    titles = list(TITLE_START.finditer(text))
    if not objectives or len(objectives) != len(ministries):
        raise CohortGateError("PAN_MISSING_OBJECTIVE_OR_MINISTRY")

    def page_at(position: int) -> int:
        return page_texts[bisect_right(starts, position) - 1][0]

    rows: list[dict] = []
    preceding_ministry_end = 0
    for i, (objective, ministry) in enumerate(zip(objectives, ministries), 1):
        next_objective = objectives[i].start() if i < len(objectives) else len(text)
        if not (objective.start() < ministry.start() < next_objective):
            raise CohortGateError("PAN_OBJECTIVE_MINISTRY_ORDER_AMBIGUOUS")
        candidate_titles = [t for t in titles
                            if preceding_ministry_end <= t.start() < objective.start()]
        if not candidate_titles:
            raise CohortGateError("PAN_ENTRY_WITHOUT_TITLE_ANCHOR")
        # The heading may itself span several lines containing references to
        # other laws ("LEY 17/2001 ..."). Such a continuation is NOT a new
        # planned item. Choose the first title anchor after the preceding
        # item's Ministry witness; the order guard below still controls each
        # Objective -> Ministry pairing.
        anchor = candidate_titles[0]
        line = anchor.group().strip()
        kind = ("ORGANIC_LAW" if line.startswith("LEY ORG") else
                "ROYAL_DECREE" if line.startswith("REAL DECRETO") else "LAW")
        ministry_line = text[ministry.end():].split("\n", 1)[0].strip()
        rows.append({
            "source_local_ordinal_not_official_id": i,
            "source_local_id": f"UNVERIFIED_PAN2024_ORDER_{i:04d}",
            "normative_class": kind,
            "title_first_line_unverified": line[:500],
            "first_ministry_line_unverified": ministry_line[:200],
            "title_pdf_page": page_at(anchor.start()),
            "objective_pdf_page": page_at(objective.start()),
            "ministry_pdf_page": page_at(ministry.start()),
            "text_extraction_is_not_manual_transcription": True,
            "status": "PLANNED_IN_THIS_EDITION_ONLY",
            "official_crosswalk_id": None,
            "first_public_at": None,
            "IAEN_link": None,
            "actual_approval_outcome": None,
        })
        preceding_ministry_end = ministry.end()
    return tuple(rows)


def audit_source_local_counts(rows: tuple[dict, ...], *, expected: dict[str, int]) -> dict:
    counts = Counter(row["normative_class"] for row in rows)
    if dict(counts) != expected or len(rows) != sum(expected.values()):
        raise CohortGateError("PAN_SOURCE_LOCAL_198_AND_CLASS_DISTRIBUTION_NOT_MET")
    if len({row["source_local_id"] for row in rows}) != len(rows):
        raise CohortGateError("PAN_DUPLICATED_LOCAL_ITEM_ID")
    return {
        "provisional_source_local_items": len(rows),
        "counts_by_normative_class": dict(sorted(counts.items())),
        "independent_register_denominator_certified": False,
        "source_edition_vintages_verified": False,
        "first_public_at_verified": False,
        "individual_IAEN_outcomes_inspected": False,
        "plan_edition_to_IAEN_crosswalk_verified": False,
        "status": "SOURCE_LOCAL_PLAN_ONLY_REVIEW_REQUIRED",
        "AB_scientific_cycles": 0,
        "R5": "STOP",
    }


def run(*, pdf_path: Path, out_dir: Path, repo_root: Path) -> dict:
    """Write original-derived rows only in explicit private path outside Git."""
    import pypdf

    pdf_path, out_dir, repo_root = (p.resolve() for p in (pdf_path, out_dir, repo_root))
    if (pdf_path.name != SOURCE_FILENAME or not pdf_path.is_file()
            or repo_root == pdf_path or repo_root in pdf_path.parents
            or repo_root == out_dir or repo_root in out_dir.parents):
        raise CohortGateError("PAN_SOURCE_OR_OUTPUT_NOT_OUTSIDE_REPO")
    if not out_dir.is_dir():
        raise CohortGateError("PAN_PRIVATE_OUTPUT_DIR_MUST_ALREADY_EXIST")
    if pdf_path.stat().st_size > 10_000_000:
        raise CohortGateError("PAN_UNEXPECTED_SOURCE_SIZE")
    actual_sha = sha256(pdf_path.read_bytes()).hexdigest()
    if actual_sha != SOURCE_SHA256:
        raise CohortGateError("PAN_ORIGINAL_SHA256_CHANGED_REQUIRE_REVIEW")
    pdf = pypdf.PdfReader(str(pdf_path), strict=True)
    if pdf.is_encrypted or len(pdf.pages) != EXPECTED_PDF_PAGES:
        raise CohortGateError("PAN_UNEXPECTED_PDF_PAGE_COUNT_OR_ENCRYPTION")
    page_texts = tuple((index+1, pdf.pages[index].extract_text() or "")
                       for index in range(FIRST_PLAN_BODY_PAGE-1, len(pdf.pages)))
    rows = identify_plan_items(page_texts)
    audit = audit_source_local_counts(rows, expected=EXPECTED_ITEM_COUNTS)
    report = {
        "schema": "pfl.pan2024.source_local_inventory.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_page": SOURCE_PAGE,
        "original_pdf_filename": SOURCE_FILENAME,
        "original_pdf_sha256": actual_sha,
        "original_pdf_page_count": len(pdf.pages),
        "source_page_update_date": "2025-04-16",
        "source_page_update_date_is_not_first_public_at": True,
        "introduction_says_projected_norms": 199,
        "main_statistics_and_body_count": 198,
        "unresolved_within_original_claim_discrepancy": True,
        "lossy_extraction_warning": "Title and ministry first-line excerpts require visual checking; U+FFFD exists in parsed source text",
        "no_IAEN_pages_read_by_this_script": True,
        "original_redistributed": False,
        **audit,
    }
    inventory = out_dir / "PAN2024_SOURCE_LOCAL_ITEMS_PRIVATE.jsonl"
    receipt = out_dir / "PAN2024_SOURCE_LOCAL_AUDIT_PRIVATE.json"
    # Both paths are reserved atomically, never overwrite another session's
    # observations, and neither may be inside the Git tree.
    if inventory.exists() or receipt.exists():
        raise CohortGateError("PAN_PRIVATE_OUTPUT_ALREADY_EXISTS")
    with inventory.open("x", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    report["private_items_jsonl_sha256"] = sha256(inventory.read_bytes()).hexdigest()
    with receipt.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, sort_keys=True)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    opts = parser.parse_args()
    result = run(pdf_path=opts.pdf, out_dir=opts.out_dir,
                 repo_root=Path(__file__).resolve().parents[1])
    # Never print the item rows or excerpts, only a safe public aggregate.
    public = {key: result[key] for key in (
        "provisional_source_local_items", "counts_by_normative_class",
        "independent_register_denominator_certified", "source_edition_vintages_verified",
        "first_public_at_verified", "individual_IAEN_outcomes_inspected",
        "plan_edition_to_IAEN_crosswalk_verified", "R5", "AB_scientific_cycles",
        "unresolved_within_original_claim_discrepancy",
    )}
    print(json.dumps(public, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
