"""Private PP04-C reviewer queue: proposal candidates, NEVER authenticated links.

Uses precisely pinned, already-derived PAN2024/IAEN2024 local candidate files
from previously authorized originals. Does not fetch PDFs, scrape URLs,
read IAEN approval outcomes, join cases automatically, or emit row text in Git.
Candidate similarity is a work-queue ordering device, not linkage evidence.
"""
from __future__ import annotations

import argparse
from collections import Counter
from difflib import SequenceMatcher
from hashlib import sha256
import json
from pathlib import Path
import re
import unicodedata


PAN_ORIGINAL_SHA = "49de70b656da1b9ed9c68f552eafe743bede253e5b7a725d5eb615db1b61b4c5"
IAEN_ORIGINAL_SHA = "7c77a73480f3f039d8ba069e12301b7a4c7ad0eeec85934ec84721526cb88aa2"
PAN_DERIVED_SHA = "c5bb5feba316c77c827bf60e912074ebc2ab56fd2be0489122116c30a78d86bf"
IAEN_DERIVED_SHA = "0a46761441426183f08c86a1ba334640b8c402c059b777eb34cf2de8f571696b"
PAN_DERIVED_FILE = "PAN2024_SOURCE_LOCAL_ITEMS_PRIVATE.jsonl"
IAEN_DERIVED_FILE = "IAEN2024_ROWS_CANDIDATE_ONLY_PRIVATE.json"
NUMBER = 198


class ReviewGateError(ValueError):
    pass


def keytext(text: str) -> str:
    if type(text) is not str or not text or len(text) > 7000:
        raise ReviewGateError("REVIEW_TITLE_UNTRUSTED")
    folded = unicodedata.normalize("NFKD", text.upper())
    letters = "".join(c for c in folded if not unicodedata.combining(c))
    result = " ".join(re.findall(r"[A-Z0-9]+", letters))
    if not result:
        raise ReviewGateError("REVIEW_TITLE_EMPTY_AFTER_NORMALIZATION")
    return result


def project_pan(rows: list[dict]) -> tuple[dict, ...]:
    if type(rows) is not list or len(rows) != NUMBER:
        raise ReviewGateError("PAN_PROVISIONAL_DENOMINATOR_WRONG")
    selected = []
    for i, row in enumerate(rows, 1):
        if (type(row) is not dict or row.get("source_local_ordinal_not_official_id") != i
                or row.get("first_public_at") is not None
                or row.get("actual_approval_outcome") is not None
                or row.get("IAEN_link") is not None
                or row.get("official_crosswalk_id") is not None):
            raise ReviewGateError("PAN_HISTORICAL_LINK_OR_ORDINAL_NOT_ADMISSIBLE")
        title = row.get("title_first_line_unverified")
        page = row.get("title_pdf_page")
        if type(page) is not int or not 37 <= page <= 117:
            raise ReviewGateError("PAN_PAGE_OUTSIDE_PROVISIONAL_BODY")
        selected.append({"ordinal": i, "page": page, "text": title, "key": keytext(title)})
    return tuple(selected)


def project_iaen(rows: list[dict]) -> tuple[dict, ...]:
    if type(rows) is not list or len(rows) != NUMBER:
        raise ReviewGateError("IAEN_PLANNED_REVIEW_FRAME_WRONG")
    selected = []
    for i, row in enumerate(rows, 1):
        if (type(row) is not dict or row.get("source_local_ordinal") != i
                or row.get("first_public_at") is not None
                or row.get("publisher_stable_id_verified") is not False
                or row.get("policy_outcome_causally_attributed") is not False
                or row.get("source_listing_heading") not in (
                    "APPROVED_AS_REPORTED", "PENDING_APPROVAL_UNSPLIT")):
            raise ReviewGateError("IAEN_ROW_GRANULARITY_OR_SOURCE_CLAIMS")
        page = row.get("source_pdf_page")
        if type(page) is not int or not 1 <= page <= 126:
            raise ReviewGateError("IAEN_PAGE_UNTRUSTED")
        title = row.get("title_candidate")
        # Deliberately do NOT copy/use source_listing_heading or the body
        # (which may contain post-2024 'Publicado como' outcomes).
        selected.append({"ordinal": i, "page": page, "text": title, "key": keytext(title)})
    return tuple(selected)


def candidates(plan: tuple[dict, ...], report: tuple[dict, ...], topk: int = 3) -> tuple[dict, ...]:
    if (type(plan) is not tuple or type(report) is not tuple
            or len(plan) != NUMBER or len(report) != NUMBER
            or type(topk) is not int or not 1 <= topk <= 5):
        raise ReviewGateError("REVIEW_CANDIDATE_GRAIN_OR_TOPK")
    queue = []
    for item in plan:
        scoring = sorted((
            (SequenceMatcher(None, item["key"], candidate["key"], autojunk=False).ratio(),
             candidate["ordinal"], candidate["page"], candidate["text"])
            for candidate in report
        ), key=lambda x: (-x[0], x[1]))[:topk]
        queue.append({
            "pan_local_ordinal": item["ordinal"],
            "pan_pdf_page": item["page"],
            "pan_title_private_excerpt": item["text"],
            "options_unverified": [
                {"iaen_local_ordinal": rank[1], "iaen_pdf_page": rank[2],
                 "iaen_title_private_excerpt": rank[3],
                 "string_similarity_not_probability": round(rank[0], 6),
                 "status": "REVIEW_SUGGESTION_ONLY", "authenticated": False}
                for rank in scoring
            ],
            "source_confirmed_crosswalk": None,
            "decision": "UNKNOWN",
            "requires_independent_documentary_adjudication": True,
        })
    return tuple(queue)


def independent_review_gate(reviews: tuple[dict, ...]) -> dict:
    """Review consensus merely queues external verification; it proves no ID."""
    if type(reviews) is not tuple or len(reviews) != 2:
        raise ReviewGateError("TWO_INDEPENDENT_REVIEWERS_REQUIRED")
    for r in reviews:
        if type(r) is not dict or set(r) != {
            "reviewer_pseudonym", "pan_ordinal", "iaen_ordinal", "decision",
            "evidence_kind", "pan_page", "iaen_page", "evidence_ref_hash"
        }:
            raise ReviewGateError("REVIEW_EVIDENCE_SCHEMA_INVALID")
        if (type(r["reviewer_pseudonym"]) is not str
                or not re.fullmatch(r"R[0-9]{1,3}", r["reviewer_pseudonym"])
                or any(type(r[k]) is not int or not 1 <= r[k] <= 198
                       for k in ("pan_ordinal", "iaen_ordinal"))
                or any(type(r[k]) is not int or r[k] < 1
                       for k in ("pan_page", "iaen_page"))
                or r["decision"] not in {"SAME_DOCUMENTARY_INITIATIVE", "NOT_SAME", "UNKNOWN"}
                or r["evidence_kind"] not in {
                    "OFFICIAL_EXPLICIT_ITEM_ID", "OFFICIAL_EXPLICIT_CROSS_REFERENCE",
                    "TITLE_SIMILARITY_ONLY", "NOT_AVAILABLE"
                }
                or type(r["evidence_ref_hash"]) is not str
                or not re.fullmatch(r"[0-9a-f]{64}", r["evidence_ref_hash"])):
            raise ReviewGateError("REVIEW_UNTRUSTED_FIELDS")
    if reviews[0]["reviewer_pseudonym"] == reviews[1]["reviewer_pseudonym"]:
        raise ReviewGateError("INDEPENDENT_REVIEWERS_MUST_DIFFER")
    if ((reviews[0]["pan_ordinal"], reviews[0]["iaen_ordinal"])
            != (reviews[1]["pan_ordinal"], reviews[1]["iaen_ordinal"])):
        raise ReviewGateError("REVIEWERS_NOT_REVIEWING_SAME_PAIR")
    concurrence = (
        reviews[0]["decision"] == reviews[1]["decision"] == "SAME_DOCUMENTARY_INITIATIVE"
        and all(r["evidence_kind"] in {
            "OFFICIAL_EXPLICIT_ITEM_ID", "OFFICIAL_EXPLICIT_CROSS_REFERENCE"
        } for r in reviews)
        and reviews[0]["evidence_ref_hash"] == reviews[1]["evidence_ref_hash"]
        and reviews[0]["pan_page"] == reviews[1]["pan_page"]
        and reviews[0]["iaen_page"] == reviews[1]["iaen_page"]
    )
    return {
        "pan_ordinal": reviews[0]["pan_ordinal"],
        "iaen_ordinal": reviews[0]["iaen_ordinal"],
        "status": ("CONCURRING_REVIEW_READY_FOR_EXTERNAL_ORIGINAL_CHECK"
                   if concurrence else "UNKNOWN_OR_REVIEW_DISAGREEMENT"),
        "authenticated_source_link": False,
        "rights_or_independent_population_attested": False,
        "R5": "STOP",
        "AB_scientific_cycles": 0,
    }


def ensure_outside_git(path: Path) -> None:
    p = path.resolve()
    if not p.is_dir():
        raise ReviewGateError("REVIEW_OUTPUT_DIR_MUST_ALREADY_EXIST")
    if any((parent / ".git").exists() for parent in (p, *p.parents)):
        raise ReviewGateError("REVIEW_PRIVATE_OUTPUT_INSIDE_GIT_TREE")


def load_pinned(path: Path, expected_name: str, expected_sha: str) -> bytes:
    if path.name != expected_name or not path.is_file() or path.stat().st_size > 2_000_000:
        raise ReviewGateError("REVIEW_SOURCE_NAME_OR_SIZE_NOT_ALLOWED")
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != expected_sha:
        raise ReviewGateError("REVIEW_DERIVED_SOURCE_SHA_CHANGED")
    return raw


def run(pan_path: Path, iaen_path: Path, out_dir: Path) -> dict:
    ensure_outside_git(out_dir)
    pan_bytes = load_pinned(pan_path, PAN_DERIVED_FILE, PAN_DERIVED_SHA)
    iaen_bytes = load_pinned(iaen_path, IAEN_DERIVED_FILE, IAEN_DERIVED_SHA)
    iaen_data = json.loads(iaen_bytes.decode("utf-8-sig"))
    if type(iaen_data) is not dict or iaen_data.get("role") != "IAEN2024":
        # Exact role checked; a nonplanned report must never enter candidates.
        raise ReviewGateError("IAEN_PRIVATE_PLANNED_ROLE_REQUIRED")
    pan_rows = tuple(json.loads(line) for line in pan_bytes.decode("utf-8-sig").splitlines())
    source_pan = project_pan(list(pan_rows))
    source_report = project_iaen(iaen_data["rows"])
    queue = candidates(source_pan, source_report)
    out = out_dir / "PP04_PRIVATE_REVIEW_QUEUE.json"
    receipt = out_dir / "PP04_PRIVATE_REVIEW_QUEUE_RECEIPT.json"
    if out.exists() or receipt.exists():
        raise ReviewGateError("REVIEW_QUEUE_ALREADY_EXISTS_NO_OVERWRITE")
    with out.open("x", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)
    summary = {
        "schema": "pfl.pp04.private_review_queue.v1",
        "plan_pdf_sha256": PAN_ORIGINAL_SHA,
        "report_pdf_sha256": IAEN_ORIGINAL_SHA,
        "plan_private_source_sha256": PAN_DERIVED_SHA,
        "report_private_source_sha256": IAEN_DERIVED_SHA,
        "private_queue_sha256": sha256(out.read_bytes()).hexdigest(),
        "plan_entries": len(queue),
        "report_planned_entries": len(source_report),
        "max_unverified_suggestions_per_plan": 3,
        "review_queue_is_not_a_verified_crosswalk": True,
        "authenticated_matches": 0,
        "unresolved_plan_entries": len(queue),
        "status_from_iaen_used_to_rank": False,
        "original_IAEN_outcomes_as_2024_predictors": False,
        "all_results_private_outside_git": True,
        "R5": "STOP", "AB_scientific_cycles": 0,
    }
    with receipt.open("x", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pan-derived", type=Path, required=True)
    parser.add_argument("--iaen-derived", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    opts = parser.parse_args()
    result = run(opts.pan_derived, opts.iaen_derived, opts.out_dir)
    # Return aggregate, provenance and limitation only: no private titles.
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
