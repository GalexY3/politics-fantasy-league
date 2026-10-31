"""PP04 source-only, noncycle parity of two authorized IAEN-derived extracts.

No direct PDF read, web, title publication, cross-document link, scientific
outcome or real-person classification. The two parsers see the SAME original,
so their agreement does not establish an independent source population.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import unicodedata


P11_NAME = "IAEN2024_ROWS_CANDIDATE_ONLY_PRIVATE.json"
P12_NAME = "PRIVATE_IAEN2024_SECTION_ANCHORS.jsonl"
P11_SHA = "0a46761441426183f08c86a1ba334640b8c402c059b777eb34cf2de8f571696b"
P12_SHA = "db21a56f8ad69f3466f5a08799dd6b903d1c6de3afa2a1384cbca364e9e55131"
PLANNED_N = 198
UNPLANNED_N = 259


class ParityError(ValueError):
    pass


def tokens(text: str) -> tuple[str, ...]:
    if type(text) is not str or len(text) > 12000:
        raise ParityError("PRIVATE_TITLE_TEXT_NOT_BOUNDED")
    folded = unicodedata.normalize("NFKD", text.upper())
    plain = "".join(c for c in folded if not unicodedata.combining(c))
    return tuple(re.findall(r"[A-Z0-9]+", plain))


def compare(p11: list[dict], p12: list[dict], *, n: int = PLANNED_N) -> dict:
    if (type(n) is not int or n < 1 or type(p11) is not list or type(p12) is not list
            or len(p11) != n or len(p12) != n
            or any(type(x) is not dict for x in p11 + p12)):
        raise ParityError("SOURCE_LOCAL_PLANNED_CENSUS_INVALID")
    statistics = Counter()
    positions = []
    for i, (x, y) in enumerate(zip(p11, p12), 1):
        if y.get("population") != "PLANNED":
            raise ParityError("NONPLANNED_IN_PLANNED_FRAME")
        if (x.get("first_public_at") is not None or y.get("first_public_at") is not None
                or x.get("publisher_stable_id_verified") is not False
                or x.get("policy_outcome_causally_attributed") is not False
                or y.get("authenticated_pan_item_link") is not None):
            raise ParityError("REAL_CAUSAL_OR_HISTORICAL_CROSSWALK_CLAIM")
        checks = {
            "ordinal": x.get("source_local_ordinal") == i,
            "page": (type(x.get("source_pdf_page")) is int
                     and x["source_pdf_page"] == y.get("pdf_page")),
            "section": (type(x.get("source_ministry_section")) is int
                        and str(x["source_ministry_section"]) == y.get("department_number")),
            "status": (
                {"APPROVED_AS_REPORTED": "APPROVED_AS_OF_REPORT",
                 "PENDING_APPROVAL_UNSPLIT": "PENDING_UNSPECIFIED_AS_OF_REPORT"}
                .get(x.get("source_listing_heading")) == y.get("status_in_report")
            ),
            "title_initial_four_tokens": (
                tokens(x.get("title_candidate"))[:4]
                == tokens(y.get("bullet_line_text", "").lstrip("- "))[:4]
            ),
        }
        for name, matches in checks.items():
            if matches:
                statistics[f"{name}_matches"] += 1
            else:
                statistics[f"{name}_disagrees"] += 1
                positions.append({"ordinal": i, "field": name,
                                  "p11_page": x.get("source_pdf_page"),
                                  "p12_page": y.get("pdf_page")})
    if sum(statistics[f"{k}_matches"] + statistics[f"{k}_disagrees"]
           for k in checks) != n * len(checks):
        raise ParityError("PARITY_DENOMINATOR_INCOMPLETE")
    return {
        "source_scope": "TWO_DIFFERENT_PARSERS_SAME_OFFICIAL_IAEN2024_PDF",
        "source_local_planned_n": n,
        "structural_comparisons": dict(sorted(statistics.items())),
        "review_locations_without_original_text": positions,
        "verified_independent_population": False,
        "authenticated_pan_iaen_links": 0,
        "R5": "STOP",
        "AB_cycles_charged": 0,
    }


def offgit(path: Path) -> Path:
    p = path.resolve()
    if not p.is_dir() or any((q / ".git").exists() for q in (p, *p.parents)):
        raise ParityError("PRIVATE_OUTPUT_DIRECTORY_MUST_EXIST_OUTSIDE_GIT")
    return p


def read_pinned(path: Path, name: str, digest: str) -> bytes:
    if path.name != name or not path.is_file() or path.stat().st_size > 2_000_000:
        raise ParityError("PRIVATE_SOURCE_NAME_OR_SIZE_WRONG")
    data = path.read_bytes()
    if sha256(data).hexdigest() != digest:
        raise ParityError("PRIVATE_SOURCE_SHA256_MISMATCH")
    return data


def run(p11_path: Path, p12_path: Path, output_dir: Path) -> dict:
    out = offgit(output_dir) / "PP04_IAEN_PARSER_PARITY_PRIVATE.json"
    if out.exists():
        raise ParityError("NO_OVERWRITE_PRIVATE_PARITY_RECEIPT")
    first = json.loads(read_pinned(p11_path, P11_NAME, P11_SHA))
    second = [json.loads(line) for line in
              read_pinned(p12_path, P12_NAME, P12_SHA).decode("utf-8-sig").splitlines()]
    if (type(first) is not dict or first.get("role") != "IAEN2024"
            or type(first.get("rows")) is not list
            or len(second) != PLANNED_N + UNPLANNED_N):
        raise ParityError("PRIVATE_IAEN_SOURCE_STRUCTURE_WRONG")
    planned = [row for row in second if row.get("population") == "PLANNED"]
    unplanned = [row for row in second if row.get("population") == "UNPLANNED"]
    if len(planned) != PLANNED_N or len(unplanned) != UNPLANNED_N:
        raise ParityError("IAEN_PLANNED_UNPLANNED_FRAME_CHANGED")
    audit = compare(first["rows"], planned)
    audit.update({
        "schema": "pfl.pp04.iaen_dual_parser_private_noncycle.v1",
        "pr11_derived_sha256": P11_SHA,
        "pr12_derived_sha256": P12_SHA,
        "unplanned_entries_separate": len(unplanned),
    })
    with out.open("x", encoding="utf-8") as f:
        json.dump(audit, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write("\n")
    return audit


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr11-derived", type=Path, required=True)
    parser.add_argument("--pr12-derived", type=Path, required=True)
    parser.add_argument("--private-output", type=Path, required=True)
    args = parser.parse_args()
    audit = run(args.pr11_derived, args.pr12_derived, args.private_output)
    print(json.dumps({
        "planned": audit["source_local_planned_n"],
        "unplanned": audit["unplanned_entries_separate"],
        "comparisons": audit["structural_comparisons"],
        "mismatch_count": len(audit["review_locations_without_original_text"]),
        "R5": audit["R5"], "AB_cycles_charged": audit["AB_cycles_charged"],
    }, ensure_ascii=False, sort_keys=True))
