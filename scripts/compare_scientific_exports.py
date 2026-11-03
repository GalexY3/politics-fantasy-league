"""Compare independently SHA-verified public S9 browser exports OFFLINE.

    python scripts/compare_scientific_exports.py early.json late.json
    python scripts/compare_scientific_exports.py --pair downloaded-pair.json

The exact source of truth is verify_scientific_snapshot.py. We do not compute
a second unverifiable pseudoreceipt, create identity links, or read private
origins. A pair download adds an independently checked *envelope* SHA, but
both nested exports are verified again before any comparison. The result is
author-stipulated visibility, never political change observed in Spain.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_scientific_snapshot as verifier  # noqa: E402

SCHEMA = "pfl.synthetic_scientific_offline_cut_comparison.v1"
PAIR_SCHEMA = "pfl.synthetic_scientific_registry_browser_pair_export.v1"
PAIR_RECEIPT_SCHEMA = "pfl.synthetic_scientific_registry_browser_pair_receipt.v1"
PAIR_KIND = "AUTHOR_STIPULATED_SNAPSHOT_VISIBILITY_NOT_REAL_CHANGE"
PAIR_FIELDS = frozenset((
    "schema", "evidence_class", "comparison_kind", "exports", "R5",
    "release_gates_passed", "scientific_ab_cycles",
    "rights_for_public_display_admitted", "external_authenticity_certified",
    "pair_receipt",
))
PAIR_RECEIPT_FIELDS = frozenset((
    "schema", "canonicalization", "canonical_json", "bytes", "sha256",
))


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
        "comparison_kind": PAIR_KIND,
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


def verify_pair(payload: object) -> dict:
    """Revalidate the EXACT downloaded pair bytes and both nested S9 receipts.

    A SHA-256 over an authored synthetic envelope is not publisher
    authentication, evidence of first-public dates, or a rights grant.
    """
    if type(payload) is not dict or payload.keys() != PAIR_FIELDS:
        raise ComparisonError("PAIR_CONTRACT_INVALID")
    if (payload["schema"] != PAIR_SCHEMA
            or payload["evidence_class"] != "SYNTHETIC_LAB_ONLY"
            or payload["comparison_kind"] != PAIR_KIND
            or payload["R5"] != "STOP_R5"
            or type(payload["release_gates_passed"]) is not int
            or payload["release_gates_passed"] != 0
            or type(payload["scientific_ab_cycles"]) is not int
            or payload["scientific_ab_cycles"] != 0
            or payload["rights_for_public_display_admitted"] is not False
            or payload["external_authenticity_certified"] is not False):
        raise ComparisonError("PAIR_CONTRACT_INVALID")

    receipt = payload["pair_receipt"]
    if (type(receipt) is not dict or receipt.keys() != PAIR_RECEIPT_FIELDS
            or receipt["schema"] != PAIR_RECEIPT_SCHEMA
            or receipt["canonicalization"] != "JSON_UTF8_SORTED_KEYS_COMPACT_V1"
            or type(receipt["canonical_json"]) is not str
            or type(receipt["bytes"]) is not int
            or not 0 < receipt["bytes"] <= verifier.MAX_INPUT_BYTES
            or not verifier.is_sha(receipt["sha256"])):
        raise ComparisonError("PAIR_RECEIPT_INVALID")
    canonical_bytes = receipt["canonical_json"].encode("utf-8")
    if len(canonical_bytes) != receipt["bytes"]:
        raise ComparisonError("PAIR_RECEIPT_LENGTH_MISMATCH")
    pair_sha = hashlib.sha256(canonical_bytes).hexdigest()
    if pair_sha != receipt["sha256"]:
        raise ComparisonError("PAIR_RECEIPT_SHA_MISMATCH")
    try:
        scope = verifier.parse_json(canonical_bytes)
        if verifier.canonical(scope) != canonical_bytes:
            raise ComparisonError("PAIR_CANONICAL_NOT_EXACT")
        # Compare against the whole envelope, not only a separately parsed
        # canonical string. The receipt field itself is the one excluded key.
        expected = {key: value for key, value in payload.items()
                    if key != "pair_receipt"}
        if verifier.canonical(expected) != canonical_bytes:
            raise ComparisonError("PAIR_RECEIPT_SCOPE_MISMATCH")
    except verifier.VerificationError as exc:
        raise ComparisonError("PAIR_CANONICAL_JSON_INVALID") from exc
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ComparisonError("PAIR_CANONICAL_JSON_INVALID") from exc

    exports = payload["exports"]
    if type(exports) is not dict or exports.keys() != {"early", "late"}:
        raise ComparisonError("PAIR_EXPORTS_INVALID")
    verified = []
    for cut in ("early", "late"):
        nested = exports[cut]
        try:
            summary = verifier.verify(nested)
            public = verifier.parse_json(
                nested["snapshot_receipt"]["canonical_json"].encode("utf-8")
            )
        except verifier.VerificationError as exc:
            raise ComparisonError("PAIR_NESTED_EXPORT_NOT_VERIFIED") from exc
        except (TypeError, KeyError, ValueError, UnicodeError,
                RecursionError) as exc:
            raise ComparisonError("PAIR_NESTED_EXPORT_NOT_VERIFIED") from exc
        verified.append((summary, public))

    early, late = verified
    if early[0]["cut"] != "early" or late[0]["cut"] != "late":
        raise ComparisonError("EARLY_AND_LATE_EXPORTS_REQUIRED")
    # The live UI holds the SAME validity date and family. Its single
    # publication selector is applied to late and CLAMPED at early.as_of.
    # This is a fixture-clock constraint, not a claim of real publication.
    if early[0]["valid_at"] != late[0]["valid_at"] or (
            early[0]["family"] != late[0]["family"]):
        raise ComparisonError("COMPARISON_FILTERS_DIFFER")
    expected_early_ceiling = min(late[0]["published_until"], early[0]["as_of"])
    if early[0]["published_until"] != expected_early_ceiling:
        raise ComparisonError("PAIR_PUBLICATION_CEILING_INCONSISTENT")
    result = compare(early, late)
    # Additional envelope digest; no source-private IDs or raw JSON emitted.
    return {**result, "pair_sha256": pair_sha}


def load_pair(path: Path) -> dict:
    """Read at most 1 MiB and reject duplicate keys at any JSON depth."""
    try:
        with Path(path).open("rb") as handle:
            raw = handle.read(verifier.MAX_INPUT_BYTES + 1)
        if len(raw) > verifier.MAX_INPUT_BYTES:
            raise ComparisonError("INPUT_TOO_LARGE")
        return verify_pair(verifier.parse_json(raw))
    except verifier.VerificationError as exc:
        raise ComparisonError("PAIR_JSON_NOT_VERIFIED") from exc
    except (OSError, TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise ComparisonError("PAIR_UNAVAILABLE_OR_INVALID") from exc


class SafeParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        del message
        raise ComparisonError("ARGUMENTS_INVALID")


def main(argv: list[str] | None = None) -> int:
    ap = SafeParser(description=(
        "Compara dos descargas S9 verificadas; no certifica fuentes externas."))
    ap.add_argument("--pair", metavar="downloaded-pair.json",
                    help="Descarga S9 conjunta, con recibo de sobre y dos recibos independientes")
    ap.add_argument("early_json", nargs="?")
    ap.add_argument("late_json", nargs="?")
    try:
        args = ap.parse_args(argv)
        if args.pair is not None:
            if args.early_json is not None or args.late_json is not None:
                raise ComparisonError("ARGUMENTS_INVALID")
            result = load_pair(Path(args.pair))
        else:
            if args.early_json is None or args.late_json is None:
                raise ComparisonError("ARGUMENTS_INVALID")
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
