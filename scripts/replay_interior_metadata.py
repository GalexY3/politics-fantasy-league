"""Reproduce *metadata-only* Interior XLSX aggregates from local originals.

Preserves the frozen original parser and tests, replays their archived
capture without any network, and compares outputs excluding execution time.
Not an AB-H experiment, individual/political outcome analysis or historical
publication-time authentication.

Usage from repo root:
  python scripts/replay_interior_metadata.py --originals-dir ../PFL-raw-primary/interior_20261031 --output-dir ../PFL-replay-interior-NEW
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from shutil import copyfile


ROOT = Path(__file__).resolve().parents[1]
PARSER_ROOT = ROOT / "research/PFL_SYSTEM20_20261031/INTERIOR_METADATA"
RECEIPTS = PARSER_ROOT / "receipts"
MANIFEST = ROOT / "data/source_manifests/interior_congreso_20261031.json"
POLICY_SHA = "bfb0548942cf0f6f03336d0a4eb86c0d7408118bb9594abbe4975217b2e7e929"


class ReplayError(ValueError):
    pass


def digest(path: Path) -> str:
    with path.open("rb") as file:
        hasher = hashlib.sha256()
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            hasher.update(chunk)
        return hasher.hexdigest()


def replay(originals: Path, output_dir: Path) -> dict:
    originals = originals.resolve(strict=True)
    output_dir = output_dir.resolve(strict=False)
    if output_dir == ROOT or ROOT in output_dir.parents:
        raise ReplayError("OUTPUT_DIRECTORY_INSIDE_REPOSITORY")
    if output_dir.exists():
        raise ReplayError("OUTPUT_DIRECTORY_EXISTS_REFUSE_OVERWRITE")
    if digest(PARSER_ROOT / "metadata_policy.json") != POLICY_SHA:
        raise ReplayError("METADATA_POLICY_CHANGED_SINCE_FIRST_OUTCOME")
    frozen = json.loads((RECEIPTS / "frozen_code.json").read_text(encoding="utf-8"))
    for name, expected in frozen["code_sha256"].items():
        if digest(PARSER_ROOT / name) != expected:
            raise ReplayError("CODE_CHANGED_SINCE_FROZEN_METADATA_AUDIT")
    if digest(RECEIPTS / "phase1_final.json") != frozen["phase1_sha256"]:
        raise ReplayError("PHASE1_CHANGED_SINCE_FROZEN_METADATA_AUDIT")
    # Source bytes still need to match the original signed-off local manifest;
    # digest equality alone does not attest historical publisher or rights.
    from verify_interior_originals import replay as check_bytes
    check_bytes(originals, MANIFEST)
    spec = importlib.util.spec_from_file_location("pfl_interior_xlsx_replay", PARSER_ROOT / "xlsx_reader.py")
    if spec is None or spec.loader is None:
        raise ReplayError("FROZEN_PARSER_NOT_LOADABLE")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.SOURCE_ROOT = originals
    module.MANIFEST = MANIFEST
    module.RUN = output_dir
    output_dir.mkdir(parents=True, exist_ok=False)
    for name in ("phase1_final.json", "frozen_code.json"):
        copyfile(RECEIPTS / name, output_dir / name)
    module.phase2()
    new = json.loads((output_dir / "phase2.json").read_text(encoding="utf-8"))
    old = json.loads((RECEIPTS / "phase2.json").read_text(encoding="utf-8"))
    # No case-level outcomes; compare only bounded, non-person aggregate metadata.
    for key in ("phase", "outputs", "policy_sha256", "frozen_code_sha256",
                "original_manifest_sha256", "licence_ref", "download_requests",
                "raw_originals_recaptured", "source_first_public_at"):
        if new.get(key) != old.get(key):
            raise ReplayError("AGGREGATE_METADATA_REPLAY_DISAGREEMENT:" + key)
    return {
        "status": "EXPLORATORY_METADATA_REPLAY_EQUAL",
        "source_originals": 2, "rows_from_sources": [o["rows_scanned"] for o in new["outputs"]],
        "source_first_public_at_verified": False,
        "political_outcomes_ingested": False,
        "person_rows_exported": False,
        "source_congress_initiative_population_complete": False,
        "ab_cycles_charged": 0,
        "replay_output_directory": str(output_dir),
        "original_aggregate_sha256": digest(RECEIPTS / "phase2.json"),
        "replay_aggregate_sha256": digest(output_dir / "phase2.json"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--originals-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(replay(args.originals_dir, args.output_dir), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
