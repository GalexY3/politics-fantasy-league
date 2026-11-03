"""Compare two separately SHA-verified, public S9 browser exports OFFLINE.

    python scripts/compare_scientific_exports.py early.json late.json

The exact source of truth is verify_scientific_snapshot.py. We do not compute
a second unverifiable pseudoreceipt, create identity links, or read private
origins. The comparison is epistemic visibility between two AUTHOR-CLOSED
synthetic publication cuts, never an estimate of political change in Spain.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_scientific_snapshot as verifier  # noqa: E402

SCHEMA = "pfl.synthetic_scientific_offline_cut_comparison.v1"


class ComparisonError(Exception):
    """Stable, non-sensitive comparison failure."""


def load_export(path: Path) -> tuple[dict, dict]:
    try:
        with Path(path).open("rb") as handle:
            raw = handle.read(verifier.MAX_INPUT_BYTES + 1)
        if len(raw) > verifier.MAX_INPUT_BYTES:
            raise ComparisonError("INPUT_TOO_LARGE")
        export = verifier.parse_json(raw)
        summary = verifier.verify(export)
        # The verifier validated exact, sorted, SHA-256 canonical bytes.
        public = verifier.parse_json(
            export["snapshot_receipt"]["canonical_json"].encode("utf-8")
        )
        return summary, public
    except verifier.VerificationError as exc:
        raise ComparisonError("EXPORT_NOT_VERIFIED") from exc
    except (OSError, ValueError, TypeError, UnicodeError, RecursionError) as exc:
        raise ComparisonError("EXPORT_UNAVAILABLE_OR_INVALID") from exc


def compare(early: tuple[dict, dict], late: tuple[dict, dict]) -> dict:
    e, escope = early
    l, lscope = late
    if e["cut"] != "early" or l["cut"] != "late":
        raise ComparisonError("EARLY_AND_LATE_EXPORTS_REQUIRED")
    if e["valid_at"] != l["valid_at"] or e["family"] != l["family"]:
        raise ComparisonError("COMPARISON_FILTERS_DIFFER")
    if e["as_of"] >= l["as_of"]:
        raise ComparisonError("CUT_ORDER_INVALID")
    e_sources = {d["public_id"]: d for d in escope["distributions"]}
    l_sources = {d["public_id"]: d for d in lscope["distributions"]}
    e_ids, l_ids = set(e_sources), set(l_sources)
    common = e_ids & l_ids
    # Compare matching *public descriptors* only, never merge source-local
    # actor keys or infer that two distinct revisions are decisions or persons.
    revision_drift = sorted(
        k for k in common if (
            e_sources[k]["revision"] != l_sources[k]["revision"]
            or e_sources[k]["sha256_public_descriptor"]
            != l_sources[k]["sha256_public_descriptor"])
    )
    e_snap, l_snap = escope["snapshot"], lscope["snapshot"]

    def public_counts(snapshot: dict, descriptor_count: int) -> dict:
        graph = snapshot["graph"]
        def graph_count(part: dict | None) -> dict:
            return {"typed_nodes": part["node_count"] if part else 0,
                    "source_local_edges": part["edge_count"] if part else 0}
        return {
            "public_source_descriptors": descriptor_count,
            "synthetic_assessments": snapshot["admission_assessments"]["assessment_count"],
            "synthetic_intake_records": snapshot["synthetic_intake"]["intake_count"],
            "intake_revisions_not_new_decisions":
                snapshot["synthetic_intake"]["logical_decisions_count"] == 0,
            "chain": graph_count(graph["chain"]),
            "chronicle": graph_count(graph["chronicle"]),
        }

    return {
        "schema": SCHEMA,
        "status": "PASS",
        "comparison_kind": "AUTHOR_STIPULATED_SNAPSHOT_VISIBILITY_NOT_REAL_CHANGE",
        "source_integrity_verified_independently": True,
        "early": {"cut": "early", "as_of": e["as_of"],
                  "published_until": e["published_until"], "sha256": e["sha256"]},
        "late": {"cut": "late", "as_of": l["as_of"],
                 "published_until": l["published_until"], "sha256": l["sha256"]},
        "shared_valid_at": e["valid_at"],
        "shared_family": e["family"],
        "publication_ceilings_differ": (
            e["published_until"] != l["published_until"]),
        "descriptors": {
            "early_visible": len(e_ids),
            "late_visible": len(l_ids),
            "visible_both": sorted(common),
            "visible_only_early": sorted(e_ids - l_ids),
            "visible_only_late": sorted(l_ids - e_ids),
            "same_id_changed_revision_or_sha": revision_drift,
        },
        "typed_and_sandbox_counts": {
            "early": public_counts(e_snap, len(e_ids)),
            "late": public_counts(l_snap, len(l_ids))},
        "absence_means_negative": False,
        "independent_denominator_established": False,
        "publisher_identity_verified": False,
        "rights_for_public_display_admitted": False,
        "real_sources_admitted": 0,
        "R5": "STOP_R5",
        "scientific_ab_cycles": 0,
        "release_gates_passed": 0,
    }


class SafeParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        del message
        raise ComparisonError("ARGUMENTS_INVALID")


def main(argv: list[str] | None = None) -> int:
    ap = SafeParser(description=(
        "Compara dos descargas S9 verificadas; no certifica fuentes externas."))
    ap.add_argument("early_json")
    ap.add_argument("late_json")
    try:
        args = ap.parse_args(argv)
        result = compare(load_export(Path(args.early_json)),
                         load_export(Path(args.late_json)))
    except ComparisonError as exc:
        result = {"schema": SCHEMA, "status": "FAIL",
                  "error_code": str(exc), "R5": "STOP_R5",
                  "publisher_identity_verified": False,
                  "rights_for_public_display_admitted": False}
    except (KeyError, ValueError, TypeError) as exc:
        del exc
        result = {"schema": SCHEMA, "status": "FAIL",
                  "error_code": "VERIFIED_EXPORT_INCOMPATIBLE",
                  "R5": "STOP_R5",
                  "publisher_identity_verified": False,
                  "rights_for_public_display_admitted": False}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":"), allow_nan=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
