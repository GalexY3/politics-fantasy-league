"""Read-only diagnosis of an ALREADY RUNNING loopback science-only beta.

    python -B scripts/diagnose_live_science_beta.py \
        --origin http://127.0.0.1:8787 [--guest-query '?pfl_guest=v1&...']

Only bounded GETs are made, with no browser, SQLite, account I/O, artifact
creation, or fallback to a newly launched demo. An author-stipulated S9 SHA
cannot certify any external publisher, rights, identities, or real changes.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import http.client
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import parse_qsl, urlencode

# An invocation from any working directory must import the actual local
# launcher/parser and the existing independent offline S9 verifiers.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import run_demo  # noqa: E402
import compare_scientific_exports as comparison  # noqa: E402
import verify_scientific_snapshot as verifier  # noqa: E402
from politics_fantasy.scientific_integration_lab import CUTS  # noqa: E402


SCHEMA = "pfl.synthetic_live_science_beta_diagnostic.v1"
COMPARISON_KIND = "AUTHOR_STIPULATED_SNAPSHOT_VISIBILITY_NOT_REAL_CHANGE"
DEFAULT_QUERY = (
    "?pfl_guest=v1&cut=late&valid_at=2026-09-15&family=all"
    "&published_until=as_of&scenario=baseline&view=compare"
)
ORIGIN_PATTERN = re.compile(r"http://127\.0\.0\.1:([1-9][0-9]{0,4})", re.ASCII)
MAX_RESPONSE_BYTES = verifier.MAX_INPUT_BYTES
CONNECT_TIMEOUT_SECONDS = 1.5


class DoctorError(Exception):
    """Stable public code only: never preserve a URL, payload or OS exception."""


def parse_origin(origin: str) -> int:
    if type(origin) is not str or len(origin) > 31:
        raise DoctorError("ORIGIN_INVALID")
    match = ORIGIN_PATTERN.fullmatch(origin)
    if not match:
        raise DoctorError("ORIGIN_INVALID")
    port = int(match.group(1))
    if not 1 <= port <= 65535:
        raise DoctorError("ORIGIN_INVALID")
    return port


def parse_guest_recipe(value: str | None) -> dict[str, str]:
    try:
        canonical = run_demo.resume_guest_query(
            DEFAULT_QUERY if value is None else value)
        return dict(parse_qsl(canonical, strict_parsing=True))
    except (ValueError, TypeError, UnicodeError) as exc:
        raise DoctorError("GUEST_QUERY_INVALID") from exc


def _all_finite(value: object) -> bool:
    """Also reject a JSON exponent such as 1e999 that Python parses as inf."""
    if type(value) is float:
        return math.isfinite(value)
    if type(value) is dict:
        return all(_all_finite(child) for child in value.values())
    if type(value) is list:
        return all(_all_finite(child) for child in value)
    return True


def _get_json(port: int, route: str) -> tuple[int, object]:
    """One bounded GET with a fixed numeric loopback host and no redirects.

    The caller owns route construction from allowlisted values only.
    """
    try:
        with closing(http.client.HTTPConnection(
                "127.0.0.1", port, timeout=CONNECT_TIMEOUT_SECONDS)) as conn:
            conn.request("GET", route, headers={
                "Host": f"127.0.0.1:{port}",
                "Accept": "application/json",
                "Connection": "close",
            })
            response = conn.getresponse()
            status = response.status
            # Never follow redirects, including those to another loopback
            # address or a remote host, and do not parse arbitrary error bodies.
            if status not in (200, 401):
                return status, None
            if not response.getheader("Content-Type", "").lower().startswith(
                    "application/json"):
                raise DoctorError("RESPONSE_INVALID")
            declared = response.getheader("Content-Length")
            if declared is not None:
                if not declared.isascii() or not declared.isdigit():
                    raise DoctorError("RESPONSE_INVALID")
                if int(declared) > MAX_RESPONSE_BYTES:
                    raise DoctorError("RESPONSE_TOO_LARGE")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except DoctorError:
        raise
    except (OSError, TimeoutError, ValueError, http.client.HTTPException) as exc:
        raise DoctorError("SERVER_UNAVAILABLE") from exc
    if len(raw) > MAX_RESPONSE_BYTES:
        raise DoctorError("RESPONSE_TOO_LARGE")
    try:
        parsed = verifier.parse_json(raw)
        if not _all_finite(parsed):
            raise DoctorError("RESPONSE_INVALID")
        return status, parsed
    except (verifier.VerificationError, TypeError, ValueError,
            UnicodeError, RecursionError) as exc:
        raise DoctorError("RESPONSE_INVALID") from exc


def _required(port: int, route: str, *, kind: str) -> object:
    status, body = _get_json(port, route)
    if status == 400:
        raise DoctorError("HTTP_400_INVALID_QUERY")
    if status == 503:
        codes = {
            "registry": "HTTP_503_REGISTRY_UNAVAILABLE",
            "lab": "HTTP_503_LAB_UNAVAILABLE",
            "readiness": "HTTP_503_READINESS_UNAVAILABLE",
        }
        raise DoctorError(codes.get(kind, "SERVER_UNAVAILABLE"))
    if status != 200:
        raise DoctorError("SERVER_UNAVAILABLE")
    return body


def _check_session(payload: object) -> None:
    if (type(payload) is not dict
            or payload.get("authenticated") is not False
            or payload.get("science_only") is not True
            or payload.get("error") != "LOCAL_SCIENCE_ONLY"):
        raise DoctorError("SCIENCE_ONLY_REQUIRED")


def _check_health(payload: object) -> None:
    if (type(payload) is not dict
            or payload.get("ok") is not True
            or payload.get("mode") != "SYNTHETIC_SCIENCE_ONLY"
            or payload.get("accounts_enabled") is not False
            or payload.get("real_player_scoring") is not False):
        raise DoctorError("SCIENCE_ONLY_REQUIRED")


def _check_readiness(payload: object) -> None:
    if type(payload) is not dict:
        raise DoctorError("READINESS_UNVERIFIED")
    local = payload.get("local_runtime")
    admission = payload.get("scientific_admission")
    release = payload.get("public_release")
    if (payload.get("schema") != "pfl.beta_readiness.v1"
            or payload.get("ok") is not True
            or type(local) is not dict
            or local.get("scope") != "LOOPBACK_SYNTHETIC_SCIENCE_ONLY"
            or local.get("status") != "READY_FOR_LOCAL_PREFLIGHT"
            or local.get("anonymous_readiness_get") is not True
            or local.get("full_user_journey_attested") is not False
            or type(local.get("checks")) is not dict
            or local["checks"] != {
                "loopback_binding": True,
                "web_assets_present": True,
                "accounts_disabled_intentionally": True,
            }
            or type(admission) is not dict
            or admission.get("r5_status") != "STOP_R5"
            or type(admission.get("system20_valid_ab_cycles")) is not int
            or admission["system20_valid_ab_cycles"] != 0
            or admission.get("empirical_study_eligible") is not False
            or type(release) is not dict
            or release.get("status") != "BLOCKED_PENDING_INDEPENDENT_ATTESTATION"
            or release.get("eligible") is not False
            or release.get("gates_total") != 6
            or type(release.get("gates_with_attestation_records")) is not int
            or release["gates_with_attestation_records"] != 0
            or release.get("public_hosting_authorized") is not False
            or release.get("real_person_scoring") is not False):
        raise DoctorError("READINESS_UNVERIFIED")


def _check_lab(payload: object, *, cut: str, scenario: str) -> None:
    if type(payload) is not dict:
        raise DoctorError("LAB_UNVERIFIED")
    explorer = payload.get("explorer")
    admission = explorer.get("admission") if type(explorer) is dict else None
    catalog = explorer.get("catalog") if type(explorer) is dict else None
    observatory = explorer.get("observatory") if type(explorer) is dict else None
    rights = payload.get("rights")
    assets = rights.get("per_asset") if type(rights) is dict else None
    if (payload.get("schema") != "pfl.synthetic_scientific_integration_lab.v1"
            or payload.get("evidence_class") != "SYNTHETIC_LAB_ONLY"
            or payload.get("cut") != cut
            or payload.get("as_of") != CUTS[cut]
            or payload.get("scenario") != scenario
            or payload.get("R5") != "STOP_R5"
            or type(payload.get("scientific_AB_cycles")) is not int
            or payload["scientific_AB_cycles"] != 0
            or type(payload.get("release_gates_passed")) is not int
            or payload["release_gates_passed"] != 0
            or payload.get("independent_all_received_denominator") is not None
            or payload.get("right_censoring_independently_attested") is not False
            or payload.get("real_corpus_ingestion_allowed") is not False
            or payload.get("real_people_scoring_enabled") is not False
            or payload.get("scientific_estimator_admitted") is not False
            or type(explorer) is not dict
            or explorer.get("schema") != "pfl.synthetic_scientific_explorer.v1"
            or explorer.get("evidence_class") != "SYNTHETIC_LAB_ONLY"
            or type(admission) is not dict
            or admission.get("R5") != "STOP_R5"
            or admission.get("scientific_AB_cycles") != 0
            or admission.get("real_denominator") is not None
            or admission.get("real_distribution_rights_admitted") is not False
            or admission.get("real_person_scoring") is not False
            or admission.get("real_source_ingestion") is not False
            or type(rights) is not dict
            or rights.get("reuse_admitted") is not False
            or rights.get("real_originals_approved") is not False
            or rights.get("independent_attestation") is not False
            or type(assets) is not dict
            # privacy_probe intentionally suppresses the asset list; absence
            # here is not permission to reuse or a negative empirical record.
            or len(assets) > 2
            or any(type(asset) is not dict
                   or asset.get("reuse_admitted") is not False
                   or asset.get("status") != "QUARANTINED"
                   for asset in assets.values())
            or type(catalog) is not dict
            or catalog.get("schema") != "pfl.synthetic_distribution_catalog.v1"
            or catalog.get("independent_rights_verified") is not False
            or catalog.get("witness_distributions_redacted") is not True
            or type(catalog.get("distributions")) is not list
            or any(type(item) is not dict
                   or item.get("real_publisher_authenticated") is not False
                   or item.get("rights_for_requested_purpose_admitted") is not False
                   or item.get("empirical_distribution_admitted") is not False
                   for item in catalog["distributions"])
            or type(observatory) is not dict
            or observatory.get("schema") != "pfl.synthetic_bitemporal_observatory.v1"
            or observatory.get("temporal_domains_joined_as_real_identities") is not False
            or observatory.get("real_actor_identity_verified") is not False
            or observatory.get("real_outcomes_attested") is not False):
        raise DoctorError("LAB_UNVERIFIED")


def _verify_registry(
    payload: object, *, cut: str, valid_at: str,
    family: str, selected_ceiling: str,
) -> tuple[dict, dict]:
    """Rebuild EXACT existing browser single export, verify independently."""
    expected_ceiling = (CUTS[cut] if selected_ceiling == "as_of" else
                        min(selected_ceiling, CUTS[cut]))
    if type(payload) is not dict:
        raise DoctorError("RECEIPT_UNVERIFIED")
    receipt = payload.get("snapshot_receipt")
    registry = payload.get("registry")
    models = payload.get("models")
    if (payload.keys() != {
            "schema", "evidence_class", "cut", "as_of", "valid_at",
            "family", "published_until", "registry", "snapshot",
            "snapshot_receipt", "snapshot_receipt_sha256", "models",
            "R5", "independent_denominator", "real_source_ingestion_allowed",
            "scientific_ab_cycles", "release_gates_passed",
        }
            or payload.get("schema") != "pfl.synthetic_scientific_registry.v1"
            or payload.get("evidence_class") != "SYNTHETIC_LAB_ONLY"
            or payload.get("cut") != cut
            or payload.get("as_of") != CUTS[cut]
            or payload.get("valid_at") != valid_at
            or payload.get("family") != family
            or payload.get("published_until") != expected_ceiling
            or payload.get("R5") != "STOP_R5"
            or type(payload.get("scientific_ab_cycles")) is not int
            or payload["scientific_ab_cycles"] != 0
            or type(payload.get("release_gates_passed")) is not int
            or payload["release_gates_passed"] != 0
            or payload.get("independent_denominator") is not None
            or payload.get("real_source_ingestion_allowed") is not False
            or type(receipt) is not dict
            or payload.get("snapshot_receipt_sha256") != receipt.get("sha256")
            or type(registry) is not dict
            or registry.get("schema_version") != 4
            or registry.keys() != {
                "schema_version", "persistent", "migration_history",
                "source_catalog_kind", "distributions",
                "visible_distribution_count", "recorded_distribution_count",
                "internal_uncatalogued_fixture_receipts", "source_bytes_exposed",
                "private_source_ids_exposed", "originals_accepted",
                "fixture_bytes_sha256_checked_at_read",
            }
            or registry.get("persistent") is not True
            or registry.get("source_catalog_kind") != "FIXED_PUBLIC_DESCRIPTORS_ONLY"
            or registry.get("source_bytes_exposed") is not False
            or registry.get("private_source_ids_exposed") is not False
            or registry.get("originals_accepted") is not False
            or registry.get("fixture_bytes_sha256_checked_at_read") is not True
            or type(registry.get("distributions")) is not list
            or type(registry.get("visible_distribution_count")) is not int
            or registry["visible_distribution_count"] != len(registry["distributions"])
            or type(models) is not dict
            or models.keys() != {
                "s3_s7_endpoint", "computed_from_registry",
                "separate_existing_python_node_oracle",
                "empirical_model_admitted",
            }
            or models.get("s3_s7_endpoint") != "/api/scientific-integration-lab"
            or models.get("computed_from_registry") is not False
            or models.get("separate_existing_python_node_oracle") is not True
            or models.get("empirical_model_admitted") is not False):
        raise DoctorError("RECEIPT_UNVERIFIED")
    try:
        canonical_bytes = receipt["canonical_json"].encode("utf-8")
        scope = verifier.parse_json(canonical_bytes)
        required_scope = {
            "schema": "pfl.synthetic_scientific_registry_snapshot.v1",
            "cut": cut, "as_of": CUTS[cut], "valid_at": valid_at,
            "family": family, "published_until": expected_ceiling,
            "distributions": registry["distributions"],
            "snapshot": payload["snapshot"],
        }
        if scope != required_scope or verifier.canonical(scope) != canonical_bytes:
            raise DoctorError("RECEIPT_UNVERIFIED")
        nested = {
            "schema": "pfl.synthetic_scientific_registry_browser_export.v1",
            "evidence_class": "SYNTHETIC_LAB_ONLY",
            "query": {
                "cut": cut, "as_of": CUTS[cut], "valid_at": valid_at,
                "family": family, "published_until": expected_ceiling,
            },
            "source_contract": payload["schema"],
            "receipt_schema": receipt["schema"],
            "snapshot_receipt": receipt,
            "R5": "STOP_R5", "release_gates_passed": 0,
            "scientific_ab_cycles": 0,
            "external_authenticity_certified": False,
            "rights_for_public_display_admitted": False,
        }
        return verifier.verify(nested), scope
    except DoctorError:
        raise
    except (verifier.VerificationError, KeyError, ValueError, TypeError,
            UnicodeError, RecursionError, OverflowError) as exc:
        raise DoctorError("RECEIPT_UNVERIFIED") from exc


def diagnose(port: int, recipe: dict[str, str]) -> dict:
    status, session = _get_json(port, "/api/session")
    if status != 401:
        raise DoctorError("SCIENCE_ONLY_REQUIRED")
    _check_session(session)
    _check_health(_required(port, "/api/health", kind="health"))
    _check_readiness(_required(port, "/api/beta-readiness", kind="readiness"))
    lab_route = "/api/scientific-integration-lab?" + urlencode([
        ("cut", recipe["cut"]), ("scenario", recipe["scenario"]),
    ])
    _check_lab(_required(port, lab_route, kind="lab"),
               cut=recipe["cut"], scenario=recipe["scenario"])
    verified = []
    for cut in ("early", "late"):
        published = recipe["published_until"]
        # A selected later clock cannot be projected backwards into early.
        if published != "as_of" and published > CUTS[cut]:
            published = "as_of"
        route = "/api/scientific-registry?" + urlencode([
            ("cut", cut), ("valid_at", recipe["valid_at"]),
            ("family", recipe["family"]), ("published_until", published),
        ])
        response = _required(port, route, kind="registry")
        verified.append(_verify_registry(
            response, cut=cut, valid_at=recipe["valid_at"],
            family=recipe["family"],
            selected_ceiling=recipe["published_until"],
        ))
    try:
        compared = comparison.compare(verified[0], verified[1])
    except (comparison.ComparisonError, KeyError, ValueError, TypeError,
            RecursionError) as exc:
        raise DoctorError("RECEIPT_UNVERIFIED") from exc
    if (compared.get("status") != "PASS"
            or compared.get("comparison_kind") != COMPARISON_KIND
            or compared.get("source_integrity_verified_independently") is not True
            or compared.get("rights_for_public_display_admitted") is not False
            or compared.get("publisher_identity_verified") is not False
            or compared.get("independent_denominator_established") is not False
            or compared.get("R5") != "STOP_R5"
            or compared.get("release_gates_passed") != 0
            or compared.get("scientific_ab_cycles") != 0):
        raise DoctorError("RECEIPT_UNVERIFIED")
    counts = compared["descriptors"]
    # No public IDs or descriptor rows in the diagnostic: only integers and
    # verified closed-fixture SHA hashes.
    return {
        "schema": SCHEMA, "status": "PASS",
        "evidence_class": "SYNTHETIC_LAB_ONLY",
        "comparison_kind": COMPARISON_KIND,
        "science_only": True,
        "early": {
            "sha256": verified[0][0]["sha256"],
            "visible_public_descriptors": counts["early_visible"],
        },
        "late": {
            "sha256": verified[1][0]["sha256"],
            "visible_public_descriptors": counts["late_visible"],
        },
        "R5": "STOP_R5", "release_gates_passed": 0,
        "scientific_ab_cycles": 0,
        "rights_for_public_display_admitted": False,
        "external_authenticity_certified": False,
        "publisher_identity_verified": False,
    }


class SafeParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        del message
        raise DoctorError("ARGUMENTS_INVALID")


def main(argv: list[str] | None = None) -> int:
    parser = SafeParser(description="Diagnostica una beta científica local ya activa.")
    parser.add_argument("--origin", required=True)
    parser.add_argument("--guest-query", default=None)
    try:
        args = parser.parse_args(argv)
        port = parse_origin(args.origin)
        recipe = parse_guest_recipe(args.guest_query)
        result = diagnose(port, recipe)
    except DoctorError as exc:
        result = {"schema": SCHEMA, "status": "FAIL", "error_code": str(exc)}
    except (KeyError, TypeError, ValueError, UnicodeError, OverflowError,
            RecursionError) as exc:
        del exc
        result = {"schema": SCHEMA, "status": "FAIL",
                  "error_code": "RECEIPT_UNVERIFIED"}
    print(json.dumps(result, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=True, allow_nan=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
