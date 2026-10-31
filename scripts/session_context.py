"""Read-only, exhaustive *byte* inventory of Git-tracked PFL files.

This does not claim that an LLM has semantically read every file. No files in
ignored/raw/private directories are opened. Network and source datasets are
never queried. Python 3.10+, standard library only.

Usage:
    python scripts/session_context.py audit
    python scripts/session_context.py audit --inventory-out ../PFL-context-receipt.json
    python scripts/session_context.py audit --require-clean
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import stat
import subprocess
import sys
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
INDEX_EXCLUSIONS = {"PROJECT_INDEX.json", "PROJECT_MAP.md", "research/INDEX.md"}
MANDATORY_SEMANTIC_ENTRY = (
    "AGENTS.md",
    "docs/SESSION_CONTEXT_PROTOCOL.md",
    "docs/VISION_CIENTIFICA_Y_ALCANCE_PFL.md",
    "docs/SISTEMA_POLITICO_ESPAÑOL_DELIMITACION_V0_20261031.md",
    "docs/WORKING_AGREEMENT.md",
    "START_HERE.md",
    "PROJECT_STATE.json",
    "METHOD_REFERENCE.json",
    "BRANCHES.json",
    "PROJECT_MAP.md",
    "PROJECT_INDEX.json",
    "research/INDEX.md",
    "HANDOFF.md",
    "research/PFL_SYSTEM20_20261031/AUTHORIZATION.json",
    "ab_atlas/README.md",
    "ab_atlas/CURRENT.md",
    "ab_atlas/ACHIEVEMENTS_README.md",
    "ab_atlas/ACHIEVEMENTS_REGISTRY.json",
)


def guide_link_audit(root: Path, paths: set[str]) -> tuple[list[str], list[str]]:
    """Check in-repo Markdown links; report out-of-repo paths as unverified."""
    errors = []
    out_of_scope = []
    for rel in MANDATORY_SEMANTIC_ENTRY:
        if not rel.endswith(".md") or rel not in paths:
            continue
        text = (root / rel).read_text(encoding="utf-8")
        for match in re.finditer(r"\]\(([^)]+)\)", text):
            url = match.group(1).strip().split()[0].split("#", 1)[0]
            if (not url or url.startswith(("http://", "https://", "mailto:", "#"))
                    or "://" in url):
                continue
            target = ((root / rel).parent / unquote(url)).resolve()
            if not target.is_relative_to(root):
                out_of_scope.append(f"OUT_OF_SCOPE_REFERENCE_NOT_CHECKED: {rel}: {url}")
                continue
            if not target.exists():
                errors.append(f"BROKEN_LOCAL_GUIDE_LINK: {rel}: {url}")
    return errors, out_of_scope


def git(*args: str, root: Path = ROOT) -> bytes:
    return subprocess.check_output(["git", *args], cwd=root, stderr=subprocess.PIPE)


def tracked_paths(root: Path) -> list[str]:
    raw = git("ls-files", "-z", root=root)
    paths = [p.decode("utf-8", errors="strict") for p in raw.split(b"\0") if p]
    if len(set(paths)) != len(paths):
        raise ValueError("DUPLICATE_TRACKED_PATHS")
    return sorted(paths)


def audit(root: Path = ROOT, *, inventory: bool = False) -> dict:
    """Hash all tracked worktree files, then compare exact project-index membership."""
    root = root.resolve()
    paths = tracked_paths(root)
    results = []
    problems: list[str] = []
    by_root = Counter()
    size_total = 0
    for rel in paths:
        target = root / rel
        try:
            if not target.resolve().is_relative_to(root):
                raise ValueError("OUTSIDE_PROJECT_ROOT")
            mode = target.lstat().st_mode
            if not stat.S_ISREG(mode):
                raise ValueError("NOT_A_REGULAR_FILE")
            digest = hashlib.sha256()
            total = 0
            with target.open("rb") as source:
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    digest.update(block)
                    total += len(block)
            results.append({"path": rel, "bytes": total, "sha256": digest.hexdigest()})
            by_root[rel.split("/", 1)[0]] += 1
            size_total += total
        except (OSError, ValueError) as exc:
            problems.append(f"{rel}: {type(exc).__name__}: {exc}")

    listed = set(paths) - INDEX_EXCLUSIONS
    catalogue_path = root / "PROJECT_INDEX.json"
    try:
        catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
        indexed = [item["path"] for item in catalogue["files"]]
        if len(set(indexed)) != len(indexed):
            problems.append("INDEX_DUPLICATE_PATH")
        missing_from_index = sorted(listed - set(indexed))
        extra_in_index = sorted(set(indexed) - listed)
        if missing_from_index or extra_in_index:
            problems.append("INDEX_MEMBERSHIP_DIFFERENCE")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        missing_from_index, extra_in_index = [], []
        problems.append(f"INDEX_UNREADABLE: {exc}")

    digest = hashlib.sha256()
    for item in results:
        digest.update(json.dumps(item, sort_keys=True, ensure_ascii=False,
                                 separators=(",", ":")).encode("utf-8") + b"\n")
    try:
        branch = git("branch", "--show-current", root=root).decode("utf-8").strip()
        head = git("rev-parse", "HEAD", root=root).decode("utf-8").strip()
        head_tree = git("rev-parse", "HEAD^{tree}", root=root).decode("utf-8").strip()
        clean = not bool(git("status", "--porcelain", "-z", root=root))
    except subprocess.CalledProcessError as exc:
        branch, head, head_tree, clean = None, None, None, False
        problems.append(f"GIT_STATE_UNAVAILABLE: {exc}")
    if len(results) != len(paths):
        problems.append("NOT_ALL_TRACKED_BYTES_READ")
    anchors_missing = [p for p in MANDATORY_SEMANTIC_ENTRY if p not in paths]
    if anchors_missing:
        problems.append("MISSING_SESSION_ENTRY_ANCHORS")
    try:
        guide_links, guide_external = guide_link_audit(root, set(paths))
    except (OSError, UnicodeError) as exc:
        guide_links = [f"GUIDE_LINK_AUDIT_UNAVAILABLE: {exc}"]
        guide_external = []
    problems.extend(guide_links)
    report = {
        "schema": "pfl.session_context_audit.v1",
        "head": head,
        "head_tree_oid": head_tree,
        "branch": branch,
        "worktree_clean": clean,
        "file_scope": "GIT_TRACKED_WORKTREE_ONLY",
        "bytes_read_purpose": "SHA256_AND_EXISTENCE_NOT_SEMANTIC_COMPREHENSION",
        "semantic_review_attested": False,
        "external_method_documents_read": False,
        "private_local_files_inspected": False,
        "tracked_paths": len(paths),
        "files_successfully_hashed": len(results),
        "bytes_hashed": size_total,
        "per_file_manifest_sha256": digest.hexdigest(),
        "digest_limit": "WORKTREE_BYTES_CAN_DIFFER_ACROSS_PLATFORMS_BY_EOL; COMPARE_HEAD_TREE_OID_FOR_CANONICAL_GIT_CONTENT",
        "top_level_counts": dict(sorted(by_root.items())),
        "index_membership_expected": len(listed),
        "index_membership_missing": missing_from_index,
        "index_membership_extra": extra_in_index,
        "semantic_reading_queue": list(MANDATORY_SEMANTIC_ENTRY),
        "semantic_reading_evidence": [],
        "anchors_missing": anchors_missing,
        "guide_link_errors": guide_links,
        "guide_references_outside_repo_unverified": guide_external,
        "problems": problems,
        "ok": not problems,
    }
    if inventory:
        report["per_file_manifest"] = results
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("audit",))
    parser.add_argument("--inventory-out", type=Path, help="Optional local receipt; never upload automatically")
    parser.add_argument("--require-clean", action="store_true")
    args = parser.parse_args()
    result = audit(inventory=bool(args.inventory_out))
    if args.require_clean and not result["worktree_clean"]:
        result["problems"].append("WORKTREE_NOT_CLEAN")
        result["ok"] = False
    if args.inventory_out:
        destination = args.inventory_out.resolve()
        if destination.is_relative_to(ROOT.resolve()):
            print("ERROR: --inventory-out must be outside project root", file=sys.stderr)
            return 2
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result["inventory_written_to"] = str(destination)
        result.pop("per_file_manifest")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
