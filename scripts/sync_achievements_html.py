"""Check or regenerate the local self-contained Achievements HTML JSON snapshot.

Only changes the embedded JSON, live count and heading. Does not adjudicate awards.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "ab_atlas/ACHIEVEMENTS_REGISTRY.json"
HTML = ROOT / "ab_atlas/ACHIEVEMENTS_Atlas_Politics_Fantasy.html"


def projected(html: str, registry: dict) -> str:
    total = sum(a["status"] != "retired" for a in registry["achievements"])
    serialized = json.dumps(registry, ensure_ascii=False, separators=(",", ":"))
    # JSON is inert in its script tag but must never allow literal closing tags.
    serialized = serialized.replace("<", "\\u003c")
    marker = r'(<script type="application/json" id="baseline">)(.*?)(</script><script>)'
    html, n = re.subn(marker, lambda m: m.group(1) + serialized + m.group(3),
                      html, count=1, flags=re.DOTALL)
    if n != 1:
        raise ValueError("MISSING_OR_AMBIGUOUS_BASELINE_SCRIPT")
    html, n = re.subn(r'(<b id="total">)\d+(</b>)', rf'\g<1>{total}\g<2>', html, count=1)
    if n != 1:
        raise ValueError("MISSING_TOTAL_COUNTER")
    html, n = re.subn(r'\d+ metas (?:de largo recorrido — [^.]+|activas, con diez originales por cada área V4 y nuevas metas auditadas)\.',
                      f'{total} metas activas, con diez originales por cada área V4 y nuevas metas auditadas.',
                      html, count=1)
    if n != 1:
        raise ValueError("MISSING_ACHIEVEMENTS_HEADING")
    return html


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write projection after review")
    args = parser.parse_args()
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    current = HTML.read_text(encoding="utf-8")
    wanted = projected(current, registry)
    if current == wanted:
        print("OK: achievements HTML snapshot matches canonical registry")
        return 0
    if not args.write:
        print("STALE: HTML achievement snapshot; run --write after reviewing registry")
        return 2
    HTML.write_text(wanted, encoding="utf-8", newline="\n")
    print("UPDATED: HTML embedded achievement snapshot; no awards adjudicated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
