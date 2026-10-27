"""Aggregate-only, read-only local inspection of private capture quarantine.

Never prints private URLs, person data, raw object locations or source records.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .private_audit import audit_private_root


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Inspect private capture quarantine without releasing content")
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = audit_private_root(args.root)
    except (OSError, ValueError, TypeError):
        print(json.dumps({"audit_error": "PRIVATE_AUDIT_UNAVAILABLE", "release_grade": False}))
        return 2
    print(json.dumps(result, sort_keys=True))
    objects = result["object_integrity"]
    malformed = any(key != "VALID_OBJECT" and count for key, count in objects.items())
    uncertain = (result["unreviewed_captures"] or result["legacy_captures_unlinked"]
                 or result["duplicate_manifest_capture_ids"] or result["legacy_size_without_bytes"]
                 or any(state not in {"QUARANTINED_SCHEMA_PASSED", "QUARANTINED_SCHEMA_FAILED",
                                      "QUARANTINED_INTEGRITY_FAILED"} and count
                        for state, count in result["quarantine_states"].items()))
    if malformed or uncertain or result["manifest_rows"] == 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
