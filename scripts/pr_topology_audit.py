"""Read-only, fail-closed PR dependency and path-overlap auditor.

Only GitHub PR metadata, never original sources, case data, account secrets,
code contents, merge attempts or claims of compatibility. No Git writes.
Default input is an explicit JSON snapshot; --live calls gh pr list read-only.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

SHA = re.compile(r"[0-9a-f]{40}\Z")
BRANCH = re.compile(r"[A-Za-z0-9._/-]{1,200}\Z")
REPO = re.compile(r"[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}\Z")
FIELDS = {"number", "headRefName", "baseRefName", "headRefOid", "files"}
FILE_FIELDS = {"path", "changeType", "additions", "deletions"}
COORDINATION = {
    "HANDOFF.md", "START_HERE.md", "PROJECT_INDEX.json",
    "PROJECT_MAP.md", "research/INDEX.md",
    "research/PFL_SYSTEM20_20261031/AUTHORIZATION.json",
}
MAX_PRS = 250
MAX_FILES = 6000


class TopologyError(ValueError):
    pass


def _safe_branch(value: object) -> bool:
    return (type(value) is str and BRANCH.fullmatch(value) is not None
            and not value.startswith("/") and not value.endswith("/")
            and ".." not in value.split("/"))


def _safe_path(value: object) -> bool:
    return (type(value) is str and 0 < len(value) <= 512
            and not value.startswith(("/", "\\"))
            and not any(seg in ("", ".", "..") for seg in value.split("/"))
            and "\\" not in value and "\x00" not in value
            and not value.startswith(".git/"))


def analyze(prs: object) -> dict:
    if type(prs) is not list or len(prs) > MAX_PRS:
        raise TopologyError("BAD_PR_SNAPSHOT")
    by_number: dict[int, dict] = {}
    by_head: dict[str, int] = {}
    paths: dict[int, set[str]] = {}
    for item in prs:
        if type(item) is not dict or set(item) != FIELDS:
            raise TopologyError("INVALID_PR_FIELDS")
        number, head, base, sha, files = (
            item["number"], item["headRefName"], item["baseRefName"],
            item["headRefOid"], item["files"])
        if type(number) is not int or not 1 <= number <= 10_000_000:
            raise TopologyError("INVALID_PR_NUMBER")
        if not _safe_branch(head) or not _safe_branch(base):
            raise TopologyError("INVALID_PR_BRANCH")
        if type(sha) is not str or SHA.fullmatch(sha) is None:
            raise TopologyError("INVALID_PR_SHA")
        if type(files) is not list or len(files) > MAX_FILES:
            raise TopologyError("INVALID_PR_FILES")
        if number in by_number or head in by_head:
            raise TopologyError("DUPLICATE_PR_OR_BRANCH")
        file_set: set[str] = set()
        for f in files:
            if (type(f) is not dict or not set(f).issubset(FILE_FIELDS)
                    or "path" not in f):
                raise TopologyError("INVALID_FILE_FIELDS")
            p = f["path"]
            if not _safe_path(p):
                raise TopologyError("INVALID_PR_PATH")
            if p in file_set:
                raise TopologyError("DUPLICATE_CHANGED_PATH")
            file_set.add(p)
        by_number[number] = item
        by_head[head] = number
        paths[number] = file_set

    bases: dict[int, int] = {}
    unknown = set()
    for number, item in by_number.items():
        base = item["baseRefName"]
        if base in by_head:
            bases[number] = by_head[base]
        elif base != "main":
            unknown.add(base)
    visited, visiting, order = set(), set(), []

    def visit(number: int):
        if number in visiting:
            raise TopologyError("PR_DEPENDENCY_CYCLE")
        if number in visited:
            return
        visiting.add(number)
        if number in bases:
            visit(bases[number])
        visiting.remove(number)
        visited.add(number)
        order.append(number)

    for number in sorted(by_number):
        visit(number)

    def ancestors(number: int) -> set[int]:
        result: set[int] = set()
        while number in bases:
            number = bases[number]
            result.add(number)
        return result

    overlap = []
    numbers = sorted(by_number)
    for i, a in enumerate(numbers):
        for b in numbers[i + 1:]:
            if a in ancestors(b) or b in ancestors(a):
                continue  # expected stacked dependency; review after base changes
            same = sorted(paths[a] & paths[b])
            if not same:
                continue
            overlap.append({
                "left_pr": a, "right_pr": b,
                "relationship": ("SAME_BASE" if
                                 by_number[a]["baseRefName"] ==
                                 by_number[b]["baseRefName"]
                                 else "DIVERGENT_BASES"),
                "substantive_paths": [p for p in same if p not in COORDINATION],
                "coordination_paths": [p for p in same if p in COORDINATION],
                "merge_conflict_proven": False,
            })

    return {
        "schema": "pfl.pr_topology_readonly.v1",
        "open_prs_inspected": len(prs),
        "dependency_edges": [
            {"pr": n, "base_pr": bases[n]} for n in sorted(bases)],
        "topological_order": order,
        "external_or_unknown_bases": sorted(unknown),
        "unresolved_base_is_not_mergeable_attestation": True,
        "parallel_overlaps": overlap,
        "merge_conflict_test_executed": False,
        "integration_approved": False,
        "scientific_AB_cycles": 0,
        "R5_open": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Read-only PR dependency/overlap analysis, never merge test")
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--snapshot", type=Path,
                        help="Explicit gh pr list JSON saved outside private originals")
    choice.add_argument("--live", action="store_true",
                        help="Read open PR metadata via installed gh CLI")
    parser.add_argument("--repo", default="GalexY3/politics-fantasy-league")
    args = parser.parse_args()
    if not REPO.fullmatch(args.repo):
        raise TopologyError("INVALID_REPO_NAME")
    if args.live:
        command = [
            "gh", "pr", "list", "--repo", args.repo, "--state", "open",
            "--limit", str(MAX_PRS),
            "--json", "number,headRefName,baseRefName,headRefOid,files",
        ]
        result = subprocess.run(command, capture_output=True, text=True,
                                timeout=30, check=True)
        raw = result.stdout
    else:
        # Windows PowerShell 5.1 Set-Content -Encoding UTF8 adds a BOM.
        # Accept that serialization detail, not a changed PR evidence claim.
        raw = args.snapshot.read_text(encoding="utf-8-sig")
    if len(raw) > 3_000_000:
        raise TopologyError("PR_SNAPSHOT_TOO_LARGE")
    prs = json.loads(raw)
    print(json.dumps(analyze(prs), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
