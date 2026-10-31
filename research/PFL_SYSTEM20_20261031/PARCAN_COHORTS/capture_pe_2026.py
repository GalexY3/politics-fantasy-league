"""Pinned official PE/2024 and PE/2026 XI distributions with PDDL licensing."""

from __future__ import annotations
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener
from capture_parcan import RUN, LICENCE, LEGAL_NOTICE, RefuseRedirect, stamp, sha256, write_new

URI = "https://www.parcan.es/api/iniciativas/2026/11/PE/?format=csv"
DATASET = "https://datos.parcan.es/dataset/iniciativas_tipope_anio2026_xilegislatura"
PUBLISHED_LINK = "https://www.parcan.es/api/iniciativas/2026/11/PE?format=csv"
HEAD_LOCATION = "/api/iniciativas/2026/11/PE/?format=csv"
URI_2024 = "https://www.parcan.es/api/iniciativas/2024/11/PE/?format=csv"
DATASET_2024 = "https://datos.parcan.es/dataset/iniciativas_tipope_anio2024_xilegislatura"
PUBLISHED_2024 = "https://www.parcan.es/api/iniciativas/2024/11/PE?format=csv"
HEAD_2024 = "/api/iniciativas/2024/11/PE/?format=csv"
MAX_CAPTURE_BYTES = 4_000_000


def capture(*, cohort_year: int = 2026):
    if cohort_year not in (2024, 2026):
        raise ValueError("ONLY_OFFICIALLY_VERIFIED_COHORT_URLS")
    target_url = URI_2024 if cohort_year == 2024 else URI
    dataset = DATASET_2024 if cohort_year == 2024 else DATASET
    published_url = PUBLISHED_2024 if cohort_year == 2024 else PUBLISHED_LINK
    redirect_location = HEAD_2024 if cohort_year == 2024 else HEAD_LOCATION
    RUN.mkdir(parents=True, exist_ok=True)
    attempt = RUN / f"pe_{cohort_year}_attempt.json"
    if attempt.exists():
        print("BLOCKED: prior attempt exists")
        return 2
    started = stamp()
    write_new(attempt, {"started_utc": started, "url": target_url, "max_get": 1,
                        "official_catalogue_link": published_url, "independent_HEAD_location": redirect_location})
    receipt = {
        "dataset": dataset, "publisher": "Parlamento de Canarias",
        "licence": LICENCE, "legal_notice": LEGAL_NOTICE,
        "no_consent_clicked": True, "credentials_used": False, "cookie_header_sent": False,
        "request_url": target_url, "source_scope": {
            "year": cohort_year, "legislature": 11, "initiative_type": "PE",
            "population": "preguntas con respuesta escrita, one published year/type/legislature distribution"
        },
        "started_utc": started, "finished_utc": None,
        "http_status": None, "http_date": None, "http_last_modified": None, "content_type": None,
        "effective_url": None, "raw_bytes": None, "raw_sha256": None, "raw_file": None,
        "state": "UNRESOLVED", "error": None, "publisher_population_total_verified": False,
        "first_public_at": None, "archive_vintage_validated": False, "http_requests": 1
    }
    try:
        req = Request(target_url, method="GET", headers={"User-Agent": "AcademicProvenanceAudit/0.1", "Accept": "text/csv"})
        with build_opener(RefuseRedirect()).open(req, timeout=18) as res:
            receipt.update({"http_status": res.status, "http_date": res.headers.get("Date"),
                            "http_last_modified": res.headers.get("Last-Modified"),
                            "content_type": res.headers.get("Content-Type"), "effective_url": res.geturl()})
            if res.status != 200 or res.geturl() != target_url:
                raise ValueError("WRONG_STATUS_OR_REDIRECT")
            raw = res.read(MAX_CAPTURE_BYTES + 1)
            if not raw or len(raw) > MAX_CAPTURE_BYTES or raw.lstrip().lower().startswith((b"<html", b"<!doctype")):
                raise ValueError("EMPTY_OVERSIZE_OR_HTML_RESPONSE")
            if res.headers.get_content_type() not in ("text/csv", "application/csv", "text/plain", "application/octet-stream"):
                raise ValueError("WRONG_CONTENT_TYPE")
            sha = sha256(raw)
            target = RUN / f"parcan_{cohort_year}_XI_PE_original.csv"
            with target.open("xb") as stream:
                stream.write(raw)
            if sha256(target.read_bytes()) != sha:
                raise ValueError("SHA_REPLAY_MISMATCH")
            receipt.update({"raw_bytes": len(raw), "raw_sha256": sha, "raw_file": target.name,
                            "state": "RAW_CAPTURED_POPULATION_NOT_CERTIFIED"})
    except HTTPError as e:
        receipt.update({"state": "BLOCKED_HTTP", "http_status": e.code,
                        "http_date": e.headers.get("Date") if e.headers else None, "error": f"HTTP_{e.code}"})
    except (URLError, TimeoutError, OSError, ValueError) as e:
        receipt.update({"state": "BLOCKED_NETWORK_OR_CONTENT", "error": f"{type(e).__name__}: {str(e)[:150]}"})
    finally:
        receipt["finished_utc"] = stamp()
        write_new(RUN / f"pe_{cohort_year}_receipt.json", receipt)
        print(json.dumps({field: receipt[field] for field in ("state", "http_status", "http_date", "raw_bytes", "raw_sha256", "error")}, indent=2))
    return 0 if receipt["state"] == "RAW_CAPTURED_POPULATION_NOT_CERTIFIED" else 1


if __name__ == "__main__":
    import sys
    if sys.argv[1:] not in (["capture"], ["capture-2024"]):
        print("Usage: python capture_pe_2026.py capture|capture-2024", file=sys.stderr)
        sys.exit(2)
    sys.exit(capture(cohort_year=2024 if sys.argv[1:] == ["capture-2024"] else 2026))
