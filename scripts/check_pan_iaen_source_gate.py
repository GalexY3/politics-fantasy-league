"""Local-only PP-03 metadata gate. Does not access the network or raw files."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from politics_fantasy.pan_iaen_preaccess_gate import validate_preaccess_source_manifest


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    out: dict = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("PAN_IAEN_DUPLICATE_JSON_KEY")
        out[key] = value
    return out


def main() -> int:
    manifest = (ROOT / "research/PFL_POLICY_PUBLICAS_20261031/SOURCE_DECISION_GATE.json")
    if manifest.stat().st_size > 64_000:
        raise ValueError("PAN_IAEN_MANIFEST_SIZE_LIMIT")
    data = json.loads(manifest.read_text(encoding="utf-8"),
                      object_pairs_hook=_reject_duplicate_keys)
    result = validate_preaccess_source_manifest(data)
    print(json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
