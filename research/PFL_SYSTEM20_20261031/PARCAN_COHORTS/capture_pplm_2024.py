"""Single bounded GET of a second, separately catalogued Canary PDDL dataset."""

from __future__ import annotations
import json
from urllib.request import Request, build_opener
from urllib.error import HTTPError, URLError
from capture_parcan import (
    RUN, SOURCE_DATASET, LICENCE, LEGAL_NOTICE, MAX_BYTES,
    RefuseRedirect, stamp, sha256, write_new
)

CANONICAL = "https://www.parcan.es/api/iniciativas/2024/11/PPLM/?format=csv"
CATALOGUE = "https://datos.parcan.es/dataset/iniciativas_tipopplm_anio2024_xilegislatura"
PUBLISHED_RESOURCE = "https://datos.parcan.es/dataset/iniciativas_tipopplm_anio2024_xilegislatura/resource/47fd1b6c-9f90-42d9-a378-5688ebaf4aed"
REDIRECT_EVIDENCE = {
    "method": "HEAD",
    "tested_noncanonical_url": "https://www.parcan.es/api/iniciativas/2024/11/PPLM?format=csv",
    "http_status": 301,
    "location": "/api/iniciativas/2024/11/PPLM/?format=csv"
}


def capture():
    RUN.mkdir(parents=True, exist_ok=True)
    if (RUN / "pplm_2024_attempt.json").exists():
        print("BLOCKED: prior attempt recorded")
        return 2
    started = stamp()
    write_new(RUN / "pplm_2024_attempt.json", {
        "started_utc": started,
        "url": CANONICAL,
        "max_get": 1,
        "official_redirect_evidence": REDIRECT_EVIDENCE
    })
    receipt = {
        "source": "Parlamento de Canarias",
        "source_dataset": CATALOGUE,
        "catalogue_resource": PUBLISHED_RESOURCE,
        "rights": {"catalogue_licence": LICENCE, "no_consent_or_login": True, "acceptance_clicked": False, "notice": LEGAL_NOTICE},
        "source_scope": {"year": 2024, "legislature": 11, "initiative_type": "PPLM", "population": "proposiciones de ley, per official type/year subcatalogue"},
        "request_url": CANONICAL,
        "started_utc": started,
        "finished_utc": None,
        "http_status": None,
        "http_date": None,
        "http_last_modified": None,
        "effective_url": None,
        "raw_bytes": None,
        "raw_sha256": None,
        "raw_file": None,
        "state": "UNRESOLVED",
        "blocked_reason": None,
        "first_public_at": None,
        "rows_verified": None,
        "source_universe_complete": False,
        "redirect_evidence": REDIRECT_EVIDENCE
    }
    try:
        req = Request(CANONICAL, method="GET", headers={"User-Agent": "AcademicProvenanceAudit/0.1", "Accept": "text/csv"})
        with build_opener(RefuseRedirect()).open(req, timeout=18) as response:
            receipt.update({"http_status": response.status, "http_date": response.headers.get("Date"),
                           "http_last_modified": response.headers.get("Last-Modified"), "effective_url": response.geturl(),
                            "content_type": response.headers.get("Content-Type")})
            if response.status != 200 or response.geturl() != CANONICAL:
                raise ValueError("UNEXPECTED_HTTP_STATUS_OR_REDIRECT")
            content = response.read(MAX_BYTES + 1)
            if len(content) > MAX_BYTES or not content or content.lstrip().lower().startswith((b"<html", b"<!doctype")):
                raise ValueError("CSV_TOO_LARGE_EMPTY_OR_HTML")
            if response.headers.get_content_type() not in ("text/csv", "application/csv", "text/plain", "application/octet-stream"):
                raise ValueError("UNEXPECTED_CONTENT_TYPE")
            digest = sha256(content)
            destination = RUN / "parcan_2024_XI_PPLM_original.csv"
            with destination.open("xb") as stream:
                stream.write(content)
            if sha256(destination.read_bytes()) != digest:
                raise ValueError("SHA256_REPLAY_ERROR")
            receipt.update({"state": "RAW_CAPTURED_NO_COMPLETENESS_CERTIFICATION",
                           "raw_bytes": len(content), "raw_sha256": digest, "raw_file": destination.name})
    except HTTPError as error:
        receipt.update({"state": "HTTP_BLOCKED", "http_status": error.code,
                        "http_date": error.headers.get("Date") if error.headers else None,
                        "blocked_reason": f"HTTP_{error.code}"})
    except (URLError, ValueError, TimeoutError, OSError) as error:
        receipt.update({"state": "BLOCKED_NETWORK_OR_CONTENT", "blocked_reason": f"{type(error).__name__}: {str(error)[:120]}"})
    finally:
        receipt["finished_utc"] = stamp()
        write_new(RUN / "pplm_2024_receipt.json", receipt)
        print(json.dumps({key: receipt[key] for key in ("state", "http_status", "http_date", "raw_bytes", "raw_sha256", "blocked_reason")}, ensure_ascii=False, indent=2))
    return 0 if receipt["state"] == "RAW_CAPTURED_NO_COMPLETENESS_CERTIFICATION" else 1


if __name__ == "__main__":
    import sys
    if sys.argv[1:] != ["capture"]:
        print("Usage: python capture_pplm_2024.py capture", file=sys.stderr)
        sys.exit(2)
    sys.exit(capture())
