"""BOE one-day capture adapter with a safely gated synthetic smoke test.

Network retrieval remains disabled pending explicit review of reuse terms.
No prediction, crawling, credentials, terms acceptance or non-scratch writes.
"""

from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from datetime import datetime, timezone
from urllib.parse import parse_qs, unquote, urljoin, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


EDITION_DATE = "2026-10-30"
SOURCE_URL = "https://www.boe.es/boe/dias/2026/10/30/"
LEGAL_URL = "https://www.boe.es/informacion/aviso_legal/index.php"
ROOT = Path(__file__).resolve().parent
RUN = ROOT / "runs" / EDITION_DATE
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
IDENTIFIER = re.compile(r"(?<![A-Za-z0-9-])BOE-A-(?:19|20)\d{2}-[1-9]\d*(?![A-Za-z0-9-])")
ALLOWED_HOST = "www.boe.es"
LIVE_FETCH_AUTHORIZED = False  # Future authorization requires a separate review.


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_json(path: Path, payload: object) -> None:
    """Create but never overwrite evidence or a prior attempt."""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=False)
        stream.write("\n")


def canonical_link(href: str) -> str | None:
    """Normalize a BOE HTTPS anchor URL, excluding foreign and unsafe URLs."""
    candidate = urlsplit(urljoin(SOURCE_URL, href.strip()))
    if candidate.scheme.lower() != "https" or candidate.netloc.lower() != ALLOWED_HOST:
        return None
    return urlunsplit(("https", ALLOWED_HOST, candidate.path, candidate.query, ""))


def ids_from_link(link: str) -> set[str]:
    parsed = urlsplit(link)
    found = set(IDENTIFIER.findall(unquote(parsed.path)))
    for key, values in parse_qs(parsed.query, keep_blank_values=False).items():
        if key.lower() == "id":
            for value in values:
                # Require an exact identifier in the id parameter.
                if IDENTIFIER.fullmatch(value):
                    found.add(value)
    return found


class BoeLinkParser(HTMLParser):
    """Extract only document identifiers and their links, no document text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors_seen = 0
        self.external_or_non_https = 0
        self.ambiguous_id_links = 0
        self.pairs: dict[tuple[str, str], int] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        self.anchors_seen += 1
        href = next((value for key, value in attrs if key.lower() == "href"), None)
        if not href:
            return
        link = canonical_link(href)
        if link is None:
            self.external_or_non_https += 1
            return
        ids = ids_from_link(link)
        if len(ids) > 1:
            self.ambiguous_id_links += 1
            return
        if ids:
            identifier = next(iter(ids))
            pair = (identifier, link)
            self.pairs[pair] = self.pairs.get(pair, 0) + 1


def extract_links(raw_html: bytes, charset: str = "utf-8") -> dict[str, object]:
    """Reconstruct a reproducible inventory from the original HTML bytes."""
    parser = BoeLinkParser()
    parser.feed(raw_html.decode(charset, errors="replace"))
    parser.close()

    grouped: dict[str, set[str]] = {}
    duplicate_pairs = []
    for (identifier, link), count in sorted(parser.pairs.items()):
        grouped.setdefault(identifier, set()).add(link)
        if count > 1:
            duplicate_pairs.append({"id": identifier, "url": link, "occurrences": count})

    ids = [{"id": key, "links": sorted(links)} for key, links in sorted(grouped.items())]
    multi_link_ids = sorted(key for key, links in grouped.items() if len(links) > 1)
    mismatched_year_ids = sorted(key for key in grouped if key.split("-")[2] != "2026")

    return {
        "ids": ids,
        "metrics": {
            "anchors_total": parser.anchors_seen,
            "anchors_rejected_external_or_non_https": parser.external_or_non_https,
            "anchors_rejected_multiple_identifiers": parser.ambiguous_id_links,
            "id_link_occurrences": sum(parser.pairs.values()),
            "unique_id_link_pairs": len(parser.pairs),
            "unique_ids": len(ids),
            "duplicate_id_link_occurrences": sum(pair["occurrences"] - 1 for pair in duplicate_pairs),
            "duplicate_pairs": duplicate_pairs,
            "ids_with_multiple_links": multi_link_ids,
            "ids_year_different_from_edition": mismatched_year_ids,
        },
    }


class NoRedirect(HTTPRedirectHandler):
    """Do not issue an unnoticed second HTTP request."""

    def redirect_request(self, request, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def get_one_page() -> tuple[bytes, dict[str, object]]:
    """Prepared bounded GET adapter. This function currently never contacts BOE."""
    if not LIVE_FETCH_AUTHORIZED:
        raise PermissionError("Real BOE GET is blocked pending explicit legal authorization")
    request = Request(
        SOURCE_URL,
        headers={
            "User-Agent": "PFL-BOE-Provenance-Smoke/0.1 (one archival request; research)",
            "Accept": "text/html",
        },
        method="GET",
    )
    opener = build_opener(NoRedirect())
    with opener.open(request, timeout=20) as response:
        info = {
            "http_status": response.status,
            "http_date": response.headers.get("Date"),
            "last_modified": response.headers.get("Last-Modified"),
            "etag": response.headers.get("ETag"),
            "content_type": response.headers.get("Content-Type"),
            "charset": response.headers.get_content_charset() or "utf-8",
            "effective_url": response.geturl(),
        }
        if response.geturl() != SOURCE_URL:
            raise ValueError("Unexpected final URL; request was not accepted")
        if response.headers.get_content_type() != "text/html":
            raise ValueError("Unexpected content type; HTML expected")
        raw = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ValueError("Response exceeds the 8 MiB smoke-test limit")
        return raw, info


def archive_real_capture(raw: bytes, info: dict[str, object]) -> dict[str, object]:
    """Prepared persist/verify step for a separately authorized future GET.

    This code is intentionally unreachable from the current CLI.
    """
    if not LIVE_FETCH_AUTHORIZED:
        raise PermissionError("Archiving a real BOE response needs separate authorization")
    if info.get("http_status") != 200 or info.get("effective_url") != SOURCE_URL:
        raise ValueError("Real archive requires HTTP 200 from the pinned daily URL")
    RUN.mkdir(parents=True, exist_ok=True)
    destination = RUN / "real"
    destination.mkdir(exist_ok=False)
    sha = hashlib.sha256(raw).hexdigest()
    with (destination / "original.html").open("xb") as output:
        output.write(raw)
    if hashlib.sha256((destination / "original.html").read_bytes()).hexdigest() != sha:
        raise ValueError("Mismatch between in-memory HTML and archived bytes")
    parsed = extract_links(raw, str(info.get("charset") or "utf-8"))
    new_json(destination / "ids.json", parsed["ids"])
    coverage = {
        "source_url": SOURCE_URL,
        "edition_date": EDITION_DATE,
        "extraction_scope": "BOE-A hrefs only, entire daily HTML; section I not isolated",
        "population_complete": False,
        "first_publication_for_all_links_verified": False,
        "metrics": parsed["metrics"],
    }
    new_json(destination / "coverage.json", coverage)
    receipt = {
        "source_url": SOURCE_URL,
        "edition_date": EDITION_DATE,
        "captured_utc": utc_now(),
        "http_status": info.get("http_status"),
        "http_date": info.get("http_date"),
        "last_modified": info.get("last_modified"),
        "etag": info.get("etag"),
        "content_type": info.get("content_type"),
        "effective_url": info.get("effective_url"),
        "raw_bytes": len(raw),
        "raw_sha256": sha,
        "raw_sha256_verified_after_save": True,
        "source_population_complete": False,
        "license_reference": LEGAL_URL,
    }
    new_json(destination / "receipt.json", receipt)
    return receipt


def smoke() -> int:
    """Perform one synthetic-only parse; record the reason for no live HTTP."""
    RUN.mkdir(parents=True, exist_ok=True)
    marker = RUN / "attempt.json"
    if marker.exists():
        print(f"BLOCKED: synthetic smoke already recorded. See {marker}")
        return 2
    started = utc_now()
    new_json(marker, {
        "source_url": SOURCE_URL,
        "edition_date": EDITION_DATE,
        "smoke_started_utc": started,
        "smoke_kind": "synthetic_only",
        "http_get_attempted": False,
    })
    receipt: dict[str, object] = {
        "edition_date": EDITION_DATE,
        "source_url": SOURCE_URL,
        "smoke_started_utc": started,
        "smoke_finished_utc": None,
        "http_status": None,
        "http_date": None,
        "http_get_attempted": False,
        "http_get_count": 0,
        "state": "live_fetch_blocked_legal_review_pending",
        "blocked_reason": "BOE reuse conditions may bind on download; no authorization to accept terms",
        "license_reference": LEGAL_URL,
        "terms_accepted": False,
        "real_html_downloaded": False,
        "real_raw_sha256": None,
        "synthetic_smoke": None,
    }
    try:
        fixture = ROOT / "fixtures" / "synthetic_day.html"
        raw = fixture.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        synthetic_dir = RUN / "synthetic"
        synthetic_dir.mkdir(exist_ok=True)
        with (synthetic_dir / "original.html").open("xb") as file:
            file.write(raw)
        persisted_hash = hashlib.sha256((synthetic_dir / "original.html").read_bytes()).hexdigest()
        if persisted_hash != sha:
            raise ValueError("Saved synthetic fixture hash differs from input")
        parsed = extract_links(raw)
        new_json(synthetic_dir / "ids.json", parsed["ids"])
        new_json(
            RUN / "coverage.json",
            {
                "edition_date": EDITION_DATE,
                "source_url": SOURCE_URL,
                "source_acquired": False,
                "live_http_status": None,
                "live_http_date": None,
                "live_coverage": None,
                "synthetic_source": "fixtures/synthetic_day.html",
                "synthetic_scope": "BOE-A IDs and anchor hrefs in a wholly fictitious HTML fragment",
                "notes": [
                    "Only identifiers carried by HTML links are counted; plain-text mentions are ignored.",
                    "One BOE-A identifier may have multiple legitimate HTML/PDF links.",
                    "A date in an index URL is not proof of a document's first publication.",
                    "Fixture metrics are not evidence for any real BOE publication.",
                    "No outcomes, hypotheses, fitted models or causal inferences were generated.",
                ],
                "synthetic_metrics": parsed["metrics"],
                "synthetic_raw_sha256": sha,
                "synthetic_raw_sha256_verified_after_save": True,
            },
        )
        receipt["synthetic_smoke"] = {
            "state": "pass" if parsed["ids"] else "fail_empty_index",
            "synthetic_original_file": "synthetic/original.html",
            "synthetic_ids_file": "synthetic/ids.json",
            "synthetic_raw_sha256": sha,
            "synthetic_raw_bytes": len(raw),
            "synthetic_unique_ids": parsed["metrics"]["unique_ids"],
            "synthetic_duplicate_occurrences": parsed["metrics"]["duplicate_id_link_occurrences"],
        }
    except (OSError, ValueError, LookupError, UnicodeError) as exc:
        receipt["synthetic_smoke"] = {"state": "fail", "error": f"{type(exc).__name__}: {exc}"}
    finally:
        receipt["smoke_finished_utc"] = utc_now()
        new_json(RUN / "receipt.json", receipt)
        print(json.dumps(receipt, indent=2, ensure_ascii=False))
    return 0 if receipt["synthetic_smoke"] and receipt["synthetic_smoke"]["state"] == "pass" else 1


if __name__ == "__main__":
    if sys.argv[1:] != ["smoke"]:
        print("Usage: python boe_capture.py smoke (synthetic only; live HTTP blocked)", file=sys.stderr)
        sys.exit(2)
    sys.exit(smoke())
