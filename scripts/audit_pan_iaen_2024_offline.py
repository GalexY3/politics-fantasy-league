"""Audit exactly two official 2024 PDF bytes in an OFF-GIT local directory.

No network requests, PDF distribution, scientific AB cycles, title matching,
person scoring, first_public_at inference or source-license promotion.

Usage:
  python scripts/audit_pan_iaen_2024_offline.py \
    --raw-root ../PFL-raw-primary/pan_iaen_2024_20261031 \
    --output-dir ../PFL-raw-primary/pan_iaen_2024_20261031/_pp04_frame_audit
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from politics_fantasy.pan_iaen_original_frame import (
    FrameParseError, parse_pan_objective_ministry_pairs,
    parse_iaen_ministry_bullets, summarise_local_frame,
)

OFFICIAL = {
    "PAN_2024.pdf": {
        "sha256": "49de70b656da1b9ed9c68f552eafe743bede253e5b7a725d5eb615db1b61b4c5",
        "pages": 117,
        "url": "https://transparencia.gob.es/content/dam/transparencia_home/publicidadactiva/normativa/pan2024/PAN_2024.pdf",
    },
    "IAEN2024PT.pdf": {
        "sha256": "7c77a73480f3f039d8ba069e12301b7a4c7ad0eeec85934ec84721526cb88aa2",
        "pages": 126,
        "url": "https://transparencia.gob.es/content/dam/transparencia_home/publicidadactiva/normativa/pan2024/IAEN2024PT.pdf",
    },
}


def _must_be_off_git(path: Path, *, allow_nongit_ancestor: bool = False) -> Path:
    path = path.resolve()
    if path == ROOT or ROOT in path.parents:
        raise FrameParseError("ORIGINALS_OR_DERIVATIVES_INSIDE_GIT_PROHIBITED")
    for ancestor in (path, *path.parents):
        if (ancestor / ".git").exists():
            raise FrameParseError("ORIGINALS_OR_DERIVATIVES_INSIDE_GIT_PROHIBITED")
    return path


def _read_verified(name: str, root: Path):
    # Dependency isolated from pure fixture tests.
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise FrameParseError("LOCAL_PYPDF_DEPENDENCY_REQUIRED") from exc
    f = root / name
    if f.is_symlink() or not f.is_file() or f.stat().st_size > 12_000_000:
        raise FrameParseError("UNEXPECTED_OR_MISSING_PRIVATE_ORIGINAL")
    data = f.read_bytes()
    digest = sha256(data).hexdigest()
    if digest != OFFICIAL[name]["sha256"] or not data.startswith(b"%PDF-"):
        raise FrameParseError("OFFICIAL_EXACT_ASSET_SHA_MISMATCH")
    reader = PdfReader(str(f))
    if reader.is_encrypted or len(reader.pages) != OFFICIAL[name]["pages"]:
        raise FrameParseError("PDF_VERSION_OR_PAGE_NUMBER_MISMATCH")
    texts = tuple(page.extract_text() or "" for page in reader.pages)
    if not all(texts):
        raise FrameParseError("UNREADABLE_OFFICIAL_TEXT_PAGE")
    metadata = reader.metadata or {}
    return texts, {
        "official_url": OFFICIAL[name]["url"],
        "sha256": digest,
        "bytes": len(data),
        "pdf_pages": len(texts),
        "pdf_embedded_creation_date_claim": str(metadata.get("/CreationDate", "")),
        "pdf_embedded_mod_date_claim": str(metadata.get("/ModDate", "")),
        "original_historical_first_public_at": None,
        "same_bytes_at_start_of_2024_proven": False,
    }


def _write_jsonl(path: Path, rows: list[dict]):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    raw = _must_be_off_git(args.raw_root)
    output = _must_be_off_git(args.output_dir)
    if not raw.is_dir() or raw not in output.parents or output.exists():
        raise FrameParseError("OUTPUT_MUST_BE_NEW_SUBDIRECTORY_OF_PRIVATE_RAW_ROOT")

    plan_text, plan_meta = _read_verified("PAN_2024.pdf", raw)
    report_text, report_meta = _read_verified("IAEN2024PT.pdf", raw)
    plan = parse_pan_objective_ministry_pairs(plan_text, start_page_index=35)
    report = parse_iaen_ministry_bullets(report_text, start_page_index=20)
    summary = summarise_local_frame(plan, report)
    expected = {
        "pan_item_candidates": 198,
        "report_planned_documentary_entries": 198,
        "report_unplanned_documentary_entries": 259,
        "report_approved_planned_entries": 89,
        "report_pending_unspecified_planned_entries": 109,
        "unplanned_misnumbered_sections": ["4.22.1"],
        "report_planned_ministries_with_rows": 21,
    }
    for key, value in expected.items():
        if summary[key] != value:
            raise FrameParseError(f"UNRECONCILED_OFFICIAL_AGGREGATE_{key}")
    if len(report["departments_with_planned_section"]) != 21:
        raise FrameParseError("IAEN_UNEXPECTED_DEPARTMENT_SECTION_COVERAGE")
    # The document itself has ONE inconsistent introductory assertion (199)
    # despite several 198 tables and exactly 198 objective/minister pairs.
    if "199" not in plan_text[8] or "198" not in plan_text[11] or "198" not in plan_text[13]:
        raise FrameParseError("PAN_INTERNAL_DENOMINATOR_ANOMALY_NOT_WITNESSED")
    if "259" not in report_text[13] or "198" not in report_text[10]:
        raise FrameParseError("IAEN_AGGREGATES_NOT_WITNESSED")

    # Exclude document bytes, full text and source-local item identities from Git.
    # Output of this script is deliberately confined to the private raw folder.
    metadata = {
        **summary,
        "audited_at_utc": datetime.now(timezone.utc).isoformat(),
        "year_of_plan": 2024,
        "year_of_iaen_label": 2024,
        "iaen_editorial_approval_on": "2025-04-15",
        "plan_introduction_says_199": True,
        "pan_other_sections_and_tables_say_198": True,
        "internal_denominator_conflict_resolved_explanation": None,
        "pan_pdf_main_section_start_page": 36,
        "iaen_pdf_ministry_section_start_page": 21,
        "source_documents": {
            "PAN_2024.pdf": plan_meta,
            "IAEN2024PT.pdf": report_meta,
        },
        "terms_url": "https://transparencia.gob.es/utilidades/aviso-legal/reutilizacion",
        "user_authorized_local_academic_use": True,
        "source_attribution": "Origen de los datos: Portal de la Transparencia de la Administración General del Estado",
        "local_originals_or_full_rows_distributed": False,
        "cross_document_names_or_titles_joined": False,
        "crosswalk_item_id_missing_from_documents": True,
        "IAEN_pending_detailed_75_31_3_at_record_level_verified": False,
        "data_quality_manual_visual_review_completed": False,
        "full_version_history_verified": False,
        "R5": "STOP",
        "scientific_AB_cycles": 0,
    }
    output.mkdir(parents=False)
    _write_jsonl(output / "PRIVATE_PAN2024_OBJECTIVE_ANCHORS.jsonl", plan)
    _write_jsonl(output / "PRIVATE_IAEN2024_SECTION_ANCHORS.jsonl", report["rows"])
    (output / "PRIVATE_FRAME_AUDIT.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    public_summary = {
        key: value for key, value in metadata.items()
        if key in ("schema", "evidence_class", "pan_item_candidates",
                   "report_planned_documentary_entries", "report_unplanned_documentary_entries",
                   "report_approved_planned_entries", "report_pending_unspecified_planned_entries",
                   "unplanned_misnumbered_sections", "report_planned_ministries_with_rows",
                   "item_level_crosswalk_authenticated", "independent_registered_entry_population_attested",
                   "R5", "scientific_AB_cycles")
    }
    print(json.dumps(public_summary, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
