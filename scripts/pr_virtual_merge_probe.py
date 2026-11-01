"""Opt-in Git tree conflict probe for isolated PFL clones.

Unlike pr_topology_audit.py this uses local Git objects. Git's
`merge-tree --write-tree` DOES write temporary objects to the clone's object
database, but it does NOT update refs or the working tree. Therefore NEVER
run it in the protected PFL-trabajo checkout. Input is exact commit IDs,
not untrusted branch names or data paths. Only sanitized conflict filenames
are returned; merged code content is never emitted.

It is not a semantic interoperability, rights, R5, privacy or release audit.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess

from scripts.pr_topology_audit import COORDINATION, _safe_path

SHA = re.compile(r"[0-9a-f]{40}\Z")
MAX_MERGE_OUTPUT = 4_000_000


class ProbeError(ValueError):
    """The local Git witness cannot support the requested conclusion."""


def parse_merge_tree(stdout: str, returncode: int) -> dict:
    """Parse only `git merge-tree --write-tree --name-only` output.

    In the conflict case Git outputs the tree OID, a list of conflicted
    paths (possibly with a leading blank), a blank separator, and textual
    messages. No message body or merged document content is returned.
    """
    if (type(stdout) is not str or len(stdout) > MAX_MERGE_OUTPUT
            or type(returncode) is not int or returncode not in (0, 1)):
        raise ProbeError("INVALID_MERGE_TREE_OUTPUT")
    lines = stdout.splitlines()
    if not lines or SHA.fullmatch(lines[0]) is None:
        raise ProbeError("MISSING_MERGE_TREE_OID")
    paths = []
    if returncode == 1:
        rest = lines[1:]
        while rest and not rest[0]:
            rest.pop(0)
        for line in rest:
            if not line:
                break
            if not _safe_path(line) or line in paths:
                raise ProbeError("INVALID_CONFLICT_PATH")
            paths.append(line)
        if not paths:
            raise ProbeError("MERGE_REPORTED_CONFLICT_WITHOUT_PATH")
    elif len(lines) > 1 and any(line.strip() for line in lines[1:]):
        raise ProbeError("UNEXPECTED_CLEAN_MERGE_CONTENT")
    paths = sorted(paths)
    return {
        "schema": "pfl.pr_virtual_merge_conflicts.v1",
        "tree_oid": lines[0],
        "tree_merge_has_conflicts": returncode == 1,
        "conflict_paths": paths,
        "coordination_conflict_paths": [x for x in paths if x in COORDINATION],
        "substantive_conflict_paths": [x for x in paths if x not in COORDINATION],
        "git_objects_may_have_been_written": True,
        "git_refs_or_worktree_updated_by_this_command": False,
        "semantic_compatibility_verified": False,
        "integration_approved": False,
        "R5_open": False,
        "scientific_AB_cycles": 0,
    }


def probe_pair(left: str, right: str, *, repo_dir: Path) -> dict:
    if (type(left) is not str or SHA.fullmatch(left) is None
            or type(right) is not str or SHA.fullmatch(right) is None
            or left == right):
        raise ProbeError("EXACT_DISTINCT_COMMIT_SHA_REQUIRED")
    root = Path(repo_dir).resolve()
    if root.name.casefold() == "pfl-trabajo":
        raise ProbeError("PROTECTED_READONLY_CHECKOUT_FORBIDDEN")
    try:
        proc = subprocess.run(
            ["git", "merge-tree", "--write-tree", "--name-only", left, right],
            cwd=root, capture_output=True, text=True, timeout=45, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ProbeError("MERGE_TREE_UNAVAILABLE") from exc
    if proc.returncode not in (0, 1):
        raise ProbeError("MERGE_TREE_FAILED_MISSING_OBJECT_OR_BAD_REFS")
    result = parse_merge_tree(proc.stdout, proc.returncode)
    result.update({"left_sha": left, "right_sha": right})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe exact commits in an ISOLATED clone; writes temporary Git tree objects")
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--allow-isolated-object-writes", action="store_true", required=True)
    args = parser.parse_args()
    if not args.allow_isolated_object_writes:
        raise ProbeError("OBJECT_DATABASE_WRITE_NOT_ACKNOWLEDGED")
    print(json.dumps(probe_pair(args.left, args.right, repo_dir=Path.cwd()), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
