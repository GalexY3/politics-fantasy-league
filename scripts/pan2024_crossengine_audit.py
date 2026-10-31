"""Offline PP04 cross-engine audit of all source-local PAN2024 title anchors.

Only an authorized PAN original pinned by SHA is read. Never opens IAEN,
publishes row text, decides outcome/coverage, or equates two extraction engines
with two independently sourced historical registers. Output directory must be
private and outside the project checkout.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import unicodedata


HERE = Path(__file__).resolve().parent
SOURCE_SCRIPT = HERE / "pan2024_local_cohort.py"
spec = importlib.util.spec_from_file_location("pan2024_source_cohort", SOURCE_SCRIPT)
cohort = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(cohort)

PUBLIC_KEYS = (
    "normative_class", "title_pdf_page", "objective_pdf_page", "ministry_pdf_page",
)
TEXT_KEYS = ("title_first_line_unverified", "first_ministry_line_unverified")


def normalize(text: str) -> str:
    if type(text) is not str:
        raise cohort.CohortGateError("CROSSENGINE_TEXT_NOT_STRING")
    decomp = unicodedata.normalize("NFKD", text.upper())
    plain = "".join(ch for ch in decomp if not unicodedata.combining(ch))
    return " ".join(re.findall(r"[A-Z0-9]+", plain))


def compare_rows(left: tuple[dict, ...], right: tuple[dict, ...]) -> dict:
    if (type(left) is not tuple or type(right) is not tuple
            or len(left) != len(right) or not left):
        raise cohort.CohortGateError("CROSSENGINE_INCOMPATIBLE_ROW_GRAIN")
    wrong = {field: [] for field in (*PUBLIC_KEYS, *TEXT_KEYS)}
    for n, (a, b) in enumerate(zip(left, right), 1):
        if a.get("source_local_ordinal_not_official_id") != n or b.get("source_local_ordinal_not_official_id") != n:
            raise cohort.CohortGateError("CROSSENGINE_ORDINAL_GRAIN_DRIFT")
        for name in PUBLIC_KEYS:
            if a.get(name) != b.get(name):
                wrong[name].append(n)
        for name in TEXT_KEYS:
            if normalize(a.get(name, "")) != normalize(b.get(name, "")):
                wrong[name].append(n)
    return {
        "row_count": len(left),
        "comparison_fields": len(wrong),
        "disagreements_by_field": {k: len(v) for k, v in wrong.items()},
        "disagreement_ordinals_private": wrong,
        "all_rows_agree_on_six_fields": not any(wrong.values()),
        "source_independent_denominator": False,
    }


def run(*, pdf: Path, out_dir: Path, repo_root: Path) -> dict:
    from pypdf import PdfReader

    pdf, out_dir, repo_root = (x.resolve() for x in (pdf, out_dir, repo_root))
    if (not pdf.is_file() or pdf.name != cohort.SOURCE_FILENAME
            or not out_dir.is_dir() or repo_root in pdf.parents
            or repo_root == pdf or repo_root in out_dir.parents
            or repo_root == out_dir):
        raise cohort.CohortGateError("CROSSENGINE_SOURCE_OR_TARGET_INVALID")
    if sha256(pdf.read_bytes()).hexdigest() != cohort.SOURCE_SHA256:
        raise cohort.CohortGateError("CROSSENGINE_SHA256_SOURCE_CHANGED")
    command = shutil.which("pdftotext")
    if command is None:
        raise cohort.CohortGateError("CROSSENGINE_POPPLER_NOT_INSTALLED")
    reader = PdfReader(str(pdf), strict=True)
    if len(reader.pages) != cohort.EXPECTED_PDF_PAGES or reader.is_encrypted:
        raise cohort.CohortGateError("CROSSENGINE_SOURCE_PAGE_COUNT_CHANGED")
    pypdf_pages = tuple((i + 1, reader.pages[i].extract_text() or "")
                        for i in range(cohort.FIRST_PLAN_BODY_PAGE-1, len(reader.pages)))
    first = cohort.identify_plan_items(pypdf_pages)
    poppler = subprocess.run([command, "-f", "37", "-l", "117", "-raw",
                              str(pdf), "-"], capture_output=True, timeout=40, check=True)
    text = poppler.stdout.decode("utf-8", "replace")
    pages = text.split("\f")
    if len(pages) < 81:
        raise cohort.CohortGateError("CROSSENGINE_POPPLER_PAGE_BOUNDARY_MISMATCH")
    other = cohort.identify_plan_items(tuple((37+i, p) for i, p in enumerate(pages[:81])))
    cohort.audit_source_local_counts(first, expected=cohort.EXPECTED_ITEM_COUNTS)
    cohort.audit_source_local_counts(other, expected=cohort.EXPECTED_ITEM_COUNTS)
    result = compare_rows(first, other)
    if not result["all_rows_agree_on_six_fields"]:
        raise cohort.CohortGateError("CROSSENGINE_SOURCE_LOCAL_FIELDS_DIVERGE")
    report = {
        "schema": "pfl.pp04.pan2024.crossengine_qa.v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_sha256": cohort.SOURCE_SHA256,
        "source_pdf_pages": len(reader.pages),
        "method_a": "pypdf extract_text plain",
        "method_b": "Poppler pdftotext -raw",
        "method_b_version_recorded": subprocess.run([command, "-v"], capture_output=True,
                                                   text=True, timeout=10).stderr.strip()[:180],
        "normative_class_counts": dict(sorted(Counter(row["normative_class"] for row in first).items())),
        **result,
        "IAEN_individual_outcomes_read": False,
        "source_local_not_independent_denominator": True,
        "visual_review_of_198_records_completed": False,
        "intro_199_main_body_198_disagreement_unresolved": True,
        "first_public_at_attested": False,
        "rights_to_redistribute_originals_or_full_rows": False,
        "R5": "STOP",
        "AB_scientific_cycles": 0,
    }
    dst = out_dir / "PAN2024_CROSSENGINE_FULL_ANCHOR_AUDIT_PRIVATE.json"
    with dst.open("x", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, sort_keys=True, indent=2)
    return report


def main() -> None:
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--pdf", type=Path, required=True)
    a.add_argument("--out-dir", type=Path, required=True)
    args = a.parse_args()
    result = run(pdf=args.pdf, out_dir=args.out_dir, repo_root=HERE.parent)
    # No original titles, ministry names or item texts are emitted.
    public = {k: v for k, v in result.items() if k in (
        "row_count", "comparison_fields", "all_rows_agree_on_six_fields",
        "disagreements_by_field", "source_local_not_independent_denominator",
        "intro_199_main_body_198_disagreement_unresolved", "R5", "AB_scientific_cycles",
    )}
    print(json.dumps(public, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
