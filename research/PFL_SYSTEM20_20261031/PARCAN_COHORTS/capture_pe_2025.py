"""One-shot, no-redirect capture of the independently located PE/2025/XI original.

Source: official CKAN package_show (HTTP 200, 2026-10-31), id
864c06c6-0174-4e7c-aaf1-b30c7d16eb0f, CSV resource
df9e92ed-8f51-495f-b275-4fd26109cddc, dataset licence odc-pddl.
The published URL redirects (HEAD 301) to the pinned canonical URL.
Only raw bytes and receipts outside Git; no scientific outcome analysis.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

REPO = Path(__file__).resolve().parents[3]
APPROVED_ROOT = REPO.parent
CATALOGUE = "https://datos.parcan.es/dataset/iniciativas_tipope_anio2025_xilegislatura"
PUBLISHED = "https://www.parcan.es/api/iniciativas/2025/11/PE?format=csv"
CANONICAL = "https://www.parcan.es/api/iniciativas/2025/11/PE/?format=csv"
RESOURCE_ID = "df9e92ed-8f51-495f-b275-4fd26109cddc"
PACKAGE_ID = "864c06c6-0174-4e7c-aaf1-b30c7d16eb0f"
FILENAME = "parcan_2025_XI_PE_original.csv"
MAX_BYTES = 4_000_000


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class RefuseRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def checked_destination(path: Path) -> Path:
    dest = path.resolve(strict=False)
    if dest == APPROVED_ROOT or APPROVED_ROOT not in dest.parents:
        raise ValueError("OUTSIDE_APPROVED_WORKSPACE")
    if dest == REPO or REPO in dest.parents:
        raise ValueError("RAW_MUST_STAY_OUTSIDE_GIT")
    if dest.exists() or not dest.parent.is_dir():
        raise ValueError("DESTINATION_MUST_BE_NEW_WITH_EXISTING_PARENT")
    return dest


def content_ok(raw: bytes, content_type: str | None) -> bool:
    if not raw or len(raw) > MAX_BYTES:
        return False
    kind = (content_type or "").split(";", 1)[0].strip().lower()
    if kind not in {"text/csv", "application/csv", "text/plain", "application/octet-stream"}:
        return False
    return not raw.lstrip().lower().startswith((b"<html", b"<!doctype"))


def save_new(path: Path, data: dict):
    with path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, sort_keys=True, indent=2, ensure_ascii=False)
        f.write("\n")


def capture_once(output_dir: Path) -> dict:
    dest = checked_destination(output_dir)
    dest.mkdir()
    receipt = {
        "schema": "pfl.parcan.pe2025.capture.v1",
        "publisher": "Parlamento de Canarias",
        "catalogue": CATALOGUE,
        "official_package_id": PACKAGE_ID,
        "official_resource_id": RESOURCE_ID,
        "catalogue_licence": "odc-pddl",
        "catalogue_metadata_confirmed_at": "2026-10-31",
        "published_url": PUBLISHED,
        "head_301_location": "/api/iniciativas/2025/11/PE/?format=csv",
        "request_url": CANONICAL,
        "source_scope": {"year": 2025, "legislature": 11, "initiative_type": "PE"},
        "credentials_used": False,
        "cookie_header_sent": False,
        "interactive_terms_accepted": False,
        "http_requests_get": 1,
        "started_utc": timestamp(),
        "finished_utc": None,
        "state": "UNRESOLVED",
        "http_status": None,
        "http_date": None,
        "content_type": None,
        "raw_file": None,
        "raw_bytes": None,
        "raw_sha256": None,
        "first_public_at": None,
        "historical_outcome_vintages_validated": False,
        "publisher_population_total_verified": False,
        "error": None,
    }
    save_new(dest / "attempt.json", {
        "timestamp": receipt["started_utc"], "request_url": CANONICAL,
        "max_attempts": 1, "no_follow_redirect": True,
        "allowed_bytes": MAX_BYTES,
    })
    try:
        req = Request(CANONICAL, method="GET", headers={
            "User-Agent": "AcademicProvenanceAudit/0.1", "Accept": "text/csv"})
        with build_opener(RefuseRedirect()).open(req, timeout=18) as resp:
            receipt["http_status"] = resp.status
            receipt["http_date"] = resp.headers.get("Date")
            receipt["content_type"] = resp.headers.get("Content-Type")
            if resp.status != 200 or resp.geturl() != CANONICAL:
                raise ValueError("UNEXPECTED_HTTP_STATUS_OR_REDIRECT")
            raw = resp.read(MAX_BYTES + 1)
            if not content_ok(raw, receipt["content_type"]):
                raise ValueError("REJECTED_CONTENT_OR_SIZE")
            digest = sha256(raw).hexdigest()
            target = dest / FILENAME
            with target.open("xb") as file:
                file.write(raw)
            if sha256(target.read_bytes()).hexdigest() != digest:
                raise ValueError("SOURCE_SHA_REPLAY_MISMATCH")
            receipt.update({
                "state": "RAW_CAPTURED_POPULATION_NOT_CERTIFIED",
                "raw_file": FILENAME, "raw_bytes": len(raw), "raw_sha256": digest,
            })
    except HTTPError as exc:
        receipt.update({"state": "HTTP_BLOCKED_NO_RETRY", "http_status": exc.code,
                        "error": f"HTTP_{exc.code}"})
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        receipt.update({"state": "CAPTURE_FAILED_NO_RETRY",
                        "error": f"{type(exc).__name__}: {str(exc)[:160]}"})
    finally:
        receipt["finished_utc"] = timestamp()
        save_new(dest / "capture_receipt.json", receipt)
    return {k: receipt[k] for k in ("state", "http_status", "raw_bytes", "raw_sha256", "error")}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-once", action="store_true", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = capture_once(args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["state"] == "RAW_CAPTURED_POPULATION_NOT_CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
