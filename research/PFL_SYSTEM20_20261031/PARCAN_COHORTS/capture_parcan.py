"""Single authorized-by-task bounded retrieval of a PDDL parliamentary dataset.

One specific direct distribution, listed at datos.parcan.es. No logins, no
cookies, no consent clicks, no retries, no redirects. Does not display rows.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parent
RUN = ROOT / "runs" / "2026-10-31"
URL = "https://www.parcan.es/api/iniciativas/2023/10/PPL?format=csv"
CANONICAL_URL = "https://www.parcan.es/api/iniciativas/2023/10/PPL/?format=csv"
SOURCE_DATASET = "https://datos.parcan.es/dataset/iniciativas_tipoppl_anio2023_xlegislatura/resource/dd23200f-d3df-4360-92d9-45807ba5da87"
LICENCE = "https://opendefinition.org/licenses/odc-pddl/"
LEGAL_NOTICE = "https://sede.parcan.es/sede/es/component/content/article/8-estatico/608-reutilizacion-de-la-informacion-y-derechos-de-propiedad-intelectual?Itemid=280"
MAX_BYTES = 2_000_000


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_new(path: Path, payload):
    with path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


class RefuseRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def capture(*, canonical: bool = False):
    RUN.mkdir(parents=True, exist_ok=True)
    target = CANONICAL_URL if canonical else URL
    label = "canonical" if canonical else "capture"
    marker = RUN / f"{label}_attempt.json"
    if marker.exists():
        print("BLOCKED: prior capture attempt exists. No retry.")
        return 2
    first = stamp()
    write_new(marker, {"url": target, "started_utc": first, "max_get_requests": 1,
                       "official_301_location_evidence": "/api/iniciativas/2023/10/PPL/?format=csv" if canonical else None})
    report = {
        "capture_started_utc": first, "capture_finished_utc": None,
        "url": target, "official_dataset_page": SOURCE_DATASET,
        "licence": LICENCE, "legal_notice": LEGAL_NOTICE,
        "right_to_download_assessment": "PDDL_LISTED_SPECIFIC_DISTRIBUTION_NO_INTERACTIVE_ACCEPTANCE_IDENTIFIED",
        "acceptance_clicked": False, "credentials_used": False, "cookies_set": False,
        "http_attempts": 1, "http_status": None, "http_date": None,
        "last_modified": None, "etag": None, "content_type": None,
        "effective_url": None, "raw_bytes": None, "raw_sha256": None,
        "status": "UNRESOLVED", "error": None, "raw_file": None,
        "scope": {"institution": "Parlamento de Canarias", "legislature": 10, "year": 2023,
                  "initiative_type_code": "PPL",
                  "universe": "Distribution only: PPL/2023/X; cross-category or cross-year completeness not established"},
        "source_first_public_at": None, "historical_publication_vintages_attested": False,
    }
    try:
        request = Request(target, headers={"User-Agent": "AcademicProvenanceAudit/0.1", "Accept": "text/csv"})
        with build_opener(RefuseRedirect()).open(request, timeout=18) as response:
            report.update({
                "http_status": response.status, "http_date": response.headers.get("Date"),
                "last_modified": response.headers.get("Last-Modified"),
                "etag": response.headers.get("ETag"),
                "content_type": response.headers.get("Content-Type"),
                "effective_url": response.geturl(),
            })
            if response.status != 200 or response.geturl() != target:
                raise ValueError("NOT_HTTP_200_OR_REDIRECTED")
            data = response.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                raise ValueError("OVER_MAX_BYTES")
            if not data or data.lstrip().lower().startswith((b"<html", b"<!doctype")):
                raise ValueError("EMPTY_OR_HTML_RESPONSE")
            mime = response.headers.get_content_type()
            if mime not in ("text/csv", "application/csv", "text/plain", "application/octet-stream"):
                raise ValueError(f"NON_CSV_MIME:{mime}")
            digest = sha256(data)
            destination = RUN / ("parcan_2023_X_PPL_original.csv" if canonical else "parcan_2023_X_PPL_uncanonical.csv")
            with destination.open("xb") as stream:
                stream.write(data)
            if sha256(destination.read_bytes()) != digest:
                raise ValueError("RAW_DIGEST_REPLAY_FAILED")
            report.update({"status": "RAW_CAPTURED_WITHOUT_POPULATION_CERTIFICATION",
                           "raw_file": destination.name, "raw_bytes": len(data),
                           "raw_sha256": digest})
    except HTTPError as error:
        report.update({"status": "BLOCKED_HTTP", "http_status": error.code,
                       "http_date": error.headers.get("Date") if error.headers else None,
                       "error": f"HTTPError_{error.code}"})
    except (URLError, TimeoutError, OSError, ValueError) as error:
        report.update({"status": "BLOCKED_NETWORK_OR_SCHEMA",
                       "error": f"{type(error).__name__}: {error}"[:300]})
    finally:
        report["capture_finished_utc"] = stamp()
        write_new(RUN / f"{label}_receipt.json", report)
        # only bounded metadata printed, never CSV rows or names.
        print(json.dumps({key: report.get(key) for key in (
            "status", "http_status", "http_date", "raw_bytes", "raw_sha256",
            "capture_started_utc", "capture_finished_utc", "error")}, indent=2))
    return 0 if report["status"] == "RAW_CAPTURED_WITHOUT_POPULATION_CERTIFICATION" else 1


if __name__ == "__main__":
    import sys
    if sys.argv[1:] not in (["capture"], ["capture-canonical"]):
        print("Usage: python capture_parcan.py capture|capture-canonical (one attempt per exact URL)", file=sys.stderr)
        sys.exit(2)
    sys.exit(capture(canonical=sys.argv[1:] == ["capture-canonical"]))
