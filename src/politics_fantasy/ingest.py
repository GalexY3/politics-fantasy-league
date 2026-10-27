"""Conservative single-source raw snapshot importer (local research, not HTTP API).

Allowed HTTPS authority and source identity are checked before the initial
request AND before each urllib redirect. Redirect metadata is not a publisher
attestation; snapshots always need independent per-source license/as-of review.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from .secure_store import store_bytes, append_private_jsonl, preflight_private_storage
import time
from datetime import datetime, timezone
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

SOURCE_HOSTS = {
    "congreso": "www.congreso.es",
    "senado": "www.senado.es",
    "boe": "www.boe.es",
}
ALLOWED_HOSTS = set(SOURCE_HOSTS.values())
MAX_BYTES = 20 * 1024 * 1024
MAX_REDIRECTS = 5


def _check_official_url(url: str, source: str) -> None:
    """Strict source↔authority binding; never accept an arbitrary allowed host."""
    if source not in SOURCE_HOSTS:
        raise ValueError("UNKNOWN_SOURCE")
    if not isinstance(url, str) or any(ord(c) < 32 or ord(c) == 127 for c in url):
        raise ValueError("INVALID_OFFICIAL_URL")
    try:
        parsed = urlsplit(url)
    except ValueError as exc:
        raise ValueError("INVALID_OFFICIAL_URL") from exc
    expected = SOURCE_HOSTS[source]
    # Restrict literal authority rather than DNS string suffixes, userinfo,
    # unusual ports, scheme-relative, Unicode lookalikes or backslashes.
    if (parsed.scheme != "https"
            or parsed.netloc.lower() not in (expected, expected + ":443")
            or not parsed.hostname == expected
            or parsed.fragment):
        raise ValueError("SOURCE_HOST_OR_SCHEME_MISMATCH")


class SourceScopedRedirects(HTTPRedirectHandler):
    """Reject every unsafe Location before urllib can connect to its target."""

    def __init__(self, source: str):
        super().__init__()
        if source not in SOURCE_HOSTS:
            raise ValueError("UNKNOWN_SOURCE")
        self.source = source
        self.hops: list[str] = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _check_official_url(newurl, self.source)
        if len(self.hops) >= MAX_REDIRECTS:
            raise ValueError("TOO_MANY_REDIRECTS")
        next_request = super().redirect_request(req, fp, code, msg, headers, newurl)
        if next_request is not None:
            self.hops.append(next_request.full_url)
        return next_request


def import_url(*, url: str, source: str, root: Path, min_interval: float = 3.0,
               timeout: float = 30.0, opener=None) -> dict:
    _check_official_url(url, source)
    if (isinstance(min_interval, bool) or not isinstance(min_interval, (int, float))
            or not math.isfinite(min_interval) or min_interval < 1):
        raise ValueError("RATE_LIMIT_INVALID")
    if (isinstance(timeout, bool) or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout) or timeout <= 0):
        raise ValueError("TIMEOUT_INVALID")
    preflight_private_storage(root, "manifest.jsonl")
    # Production path installs the redirect guard in urllib itself. An injected
    # opener exists for offline tests only: it cannot attest redirects itself.
    guard = SourceScopedRedirects(source) if opener is None else None
    open_resource = build_opener(guard).open if guard is not None else opener
    req = Request(url, headers={"User-Agent": "PoliticsFantasyResearch/0.1 (academic pilot)",
                                "Accept": "application/json, application/xml, text/xml, text/csv, */*"})
    with open_resource(req, timeout=timeout) as response:
        final_url = response.geturl()
        _check_official_url(final_url, source)
        # Without our redirect guard, we cannot inspect intermediate requests.
        if guard is None and final_url != req.full_url:
            raise ValueError("UNVERIFIED_INJECTED_REDIRECT")
        if guard is not None and guard.hops and final_url != guard.hops[-1]:
            raise ValueError("REDIRECT_CHAIN_MISMATCH")
        status = int(response.status)
        if status != 200:
            raise ValueError(f"BAD_HTTP_STATUS_{status}")
        headers = response.headers
        declared_length = headers.get("Content-Length")
        if declared_length is not None:
            if (not isinstance(declared_length, str) or not declared_length.isascii()
                    or not declared_length.isdecimal()
                    or str(int(declared_length)) != declared_length):
                raise ValueError("INVALID_CONTENT_LENGTH")
            if int(declared_length) > MAX_BYTES:
                raise ValueError("RESOURCE_EXCEEDS_20_MIB")
        content = response.read(MAX_BYTES + 1)
        if len(content) > MAX_BYTES:
            raise ValueError("RESOURCE_EXCEEDS_20_MIB")
        if declared_length is not None and len(content) != int(declared_length):
            raise ValueError("TRUNCATED_OR_INCONSISTENT_RESPONSE_LENGTH")
        digest = hashlib.sha256(content).hexdigest()
        relative_object = store_bytes(root, content, digest)
        record = {
            "source_id": source, "url": url, "final_url": final_url,
            "redirect_chain": [url, *(guard.hops if guard is not None else ())],
            "redirect_chain_checked_before_contact": guard is not None,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "sha256": digest, "bytes": len(content), "http_status": status,
            "content_type": headers.get("Content-Type"),
            "etag": headers.get("ETag"), "last_modified": headers.get("Last-Modified"),
            "raw_object": relative_object, "ingest_version": "0.3.0",
            "license_status": "REQUIRES_PER_SOURCE_REVIEW",
            "first_public_at": None, "release_grade": False,
        }
        append_private_jsonl(root, "manifest.jsonl", record)
    time.sleep(min_interval)  # single-process pacing, NOT a domain-global throttle
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description="Single-document official-source snapshot importer")
    parser.add_argument("--url", required=True)
    parser.add_argument("--source", required=True, choices=tuple(SOURCE_HOSTS))
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--min-interval", type=float, default=3)
    args = parser.parse_args()
    print(json.dumps(import_url(url=args.url, source=args.source, root=args.out,
                                min_interval=args.min_interval), indent=2))


if __name__ == "__main__":
    main()
