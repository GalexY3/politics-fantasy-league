"""Read only two user-authorized PAN/IAEN PDFs and write a *private* draft.

No HTTP, no data upload, no source redistribution, no automatic joins, no AB.
Usage (from the repository):
python scripts/pp04_extract_authorized_local_originals.py --private-dir ... --out-dir ...

The out-dir must NOT be within this repository and must not already exist.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from politics_fantasy.pan_iaen_original_frame import (
    PAN_SOURCE_SHA256, IAEN_SOURCE_SHA256,
    parse_plan_candidate_blocks, parse_report_ministry_listings,
    reconcile_counts_without_crosswalk, require_private_output_directory,
    verify_exact_original_sha256, rank_counts,
)


def _pdf_pages(path: Path, expected_pages: int) -> tuple[tuple[str, ...], dict]:
    from pypdf import PdfReader

    doc = PdfReader(path, strict=False)
    if doc.is_encrypted or len(doc.pages) != expected_pages:
        raise ValueError("PP04_SOURCE_EDITION_PAGE_COUNT_CHANGED")
    text = tuple(page.extract_text() or "" for page in doc.pages)
    if not text or not all(len(x) <= 200_000 for x in text):
        raise ValueError("PP04_PAGE_TEXT_LIMIT_OR_EMPTY")
    meta = doc.metadata or {}
    # PDF internal creation metadata is not proof of public availability.
    return text, {
        "pdf_page_count": len(text),
        "pdf_creation_date_claim": str(meta.get("/CreationDate")) if meta.get("/CreationDate") else None,
        "pdf_modification_date_claim": str(meta.get("/ModDate")) if meta.get("/ModDate") else None,
        "metadata_is_first_public_at": False,
    }


def _write_json(path: Path, payload: object) -> str:
    if path.exists():
        raise FileExistsError(f"PP04_CANNOT_OVERWRITE_PRIVATE_RESULT: {path.name}")
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Local-only PP04 original frame audit")
    parser.add_argument("--private-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    private = require_private_output_directory(args.private_dir, ROOT)
    output = require_private_output_directory(args.out_dir, ROOT)
    if output.exists():
        raise ValueError("PP04_PRIVATE_RESULT_DIRECTORY_MUST_NOT_EXIST")
    pan = private / "PAN_2024.pdf"
    iaen = private / "IAEN2024PT.pdf"
    pan_sha = verify_exact_original_sha256(pan, PAN_SOURCE_SHA256)
    iaen_sha = verify_exact_original_sha256(iaen, IAEN_SOURCE_SHA256)
    plan_pages, plan_meta = _pdf_pages(pan, 117)
    report_pages, report_meta = _pdf_pages(iaen, 126)
    if ("Plan Anual Normativo" not in plan_pages[0]
            or "INFORME ANUAL" not in report_pages[0]):
        raise ValueError("PP04_OFFICIAL_PDF_ROLE_UNSUPPORTED")
    # The plan's concrete list is in the 9th chapter, PDF pages 37..117.
    plan_rows = parse_plan_candidate_blocks(plan_pages[36:], expected_count=198,
                                            first_pdf_page=37)
    report = parse_report_ministry_listings(report_pages, expected_total=198,
                                            expected_approved=89)
    if (report["planned_ministry_sections"] != list(range(1, 22))
            or report["nonplanned_section_numbers"] != [22]
            or report["pending_approval_listing_count"] != 109
            or report["desisted_listing_count"] != 0):
        raise ValueError("PP04_UNEXPECTED_IAEN_2024_STRUCTURE")
    plan_ranks = rank_counts(plan_rows)
    approved_ranks = rank_counts(report["rows"], approved_only=True)
    if (plan_ranks != {"LEY": 43, "LEY_ORGANICA": 6, "REAL_DECRETO": 149}
            or approved_ranks != {"LEY": 17, "LEY_ORGANICA": 1,
                                  "REAL_DECRETO": 71}):
        raise ValueError("PP04_SOURCE_RANK_COUNTERS_DISAGREE")
    summary = reconcile_counts_without_crosswalk(plan_rows, report)
    summary.update({
        "pan_source_local_proposals_by_rank": plan_ranks,
        "iaen_source_local_approved_by_rank": approved_ranks,
        "source_pan_pdf_sha256": pan_sha,
        "source_iaen_pdf_sha256": iaen_sha,
        "source_pan_document_metadata": plan_meta,
        "source_iaen_document_metadata": report_meta,
        "source_originals_private_local_only": True,
        "source_originals_republished": False,
        "plan_source_marker_count": len(plan_rows),
        "plan_candidates_without_title_start": sum(
            row["title_requires_visual_review"] for row in plan_rows),
        "report_candidates_flagged_title_visual_review": sum(
            row["title_requires_visual_review"] for row in report["rows"]),
        "iaen_ministry_sections_with_planned_entries": 21,
        "iaen_ministry_section_22_is_not_included": True,
        "iaen_source_list_109_pending_heading_not_fine_states": True,
        "pan_intro_199_vs_tables_198": (
            "hasta 199" in "\n".join(plan_pages[:16])
            and "total de 198" in "\n".join(plan_pages[:16])),
        "approved_line_count_is_not_verified_item_crosswalk": True,
        "individual_candidate_timing_first_public_at": None,
        "condition_for_2024_asof_prediction": "NO_FIRST_PUBLIC_WITNESS_AND_POSTPERIOD_IAEN",
        "private_row_level_review_required": True,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    })
    output.mkdir(parents=True, exist_ok=False)
    plan_path = output / "PAN2024_ROWS_CANDIDATE_ONLY_PRIVATE.json"
    report_path = output / "IAEN2024_ROWS_CANDIDATE_ONLY_PRIVATE.json"
    summary_path = output / "PP04_COUNTS_AND_BLOCKERS_PRIVATE.json"
    hashes = {
        plan_path.name: _write_json(plan_path, {"role": "PAN2024", "rows": plan_rows}),
        report_path.name: _write_json(report_path, {"role": "IAEN2024", "rows": report["rows"]}),
        summary_path.name: _write_json(summary_path, summary),
    }
    _write_json(output / "PP04_PRIVATE_OUTPUT_HASHES.json", {
        "schema": "pfl.pp04.private_derived_row_hashes.v1",
        "files": hashes,
        "originals_sha256": [pan_sha, iaen_sha],
        "private_extraction_not_independent_sociological_validation": True,
        "R5": "STOP",
    })
    # Printing only aggregates and SHA values; never raw titles or row content.
    print(json.dumps({
        "plan_rows": len(plan_rows),
        "report_planned_rows": report["planned_listing_count"],
        "report_approved": report["approved_listing_count"],
        "report_pending_approval_unsplit": report["pending_approval_listing_count"],
        "nonplanned_section_22_excluded": True,
        "crosswalk_established": False,
        "first_public_at_verified": False,
        "private_output_sha256": hashes,
        "R5": "STOP", "AB_cycles": 0,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
