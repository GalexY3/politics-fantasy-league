"""Conservative raw snapshot importer; no assumptions about official JSON schemas.

Never use this to launch mass requests before reviewing each source's reuse policy.
A fetch is a byte-exact immutable snapshot plus a manifest for later parsing.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ALLOWED_HOSTS = {"www.congreso.es", "www.senado.es", "www.boe.es"}
MAX_BYTES = 20 * 1024 * 1024  # for a single pilot document; large backfills need an explicit design


def import_url(*, url: str, source: str, root: Path, min_interval: float = 3.0,
               timeout: float = 30.0, opener=urlopen) -> dict:
    parts = urlparse(url)
    if parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS or parts.username:
        raise ValueError("This pilot only accepts verified HTTPS official-host URLs")
    if source not in {"congreso", "senado", "boe"}:
        raise ValueError("Unknown source")
    if min_interval < 1:
        raise ValueError("Rate limit below 1s disallowed in pilot")
    # Caller must validate the source's terms, robots, and download cadence first.
    req = Request(url, headers={"User-Agent": "PoliticsFantasyResearch/0.1 (academic pilot)",
                                "Accept": "application/json, application/xml, text/xml, text/csv, */*"})
    with opener(req, timeout=timeout) as response:
        content = response.read(MAX_BYTES + 1)
        if len(content) > MAX_BYTES:
            raise ValueError("Resource exceeds 20 MiB pilot limit; no truncated save")
        final = urlparse(response.geturl())
        if final.hostname not in ALLOWED_HOSTS or final.scheme != 'https':
            raise ValueError("Redirected away from approved official HTTPS host")
        status = int(response.status)
        if status != 200:
            raise ValueError(f"Bad HTTP status {status}")
        headers = response.headers
        digest = hashlib.sha256(content).hexdigest()
        body_dir = root / "objects" / digest[:2]
        body_dir.mkdir(parents=True, exist_ok=True)
        dest = body_dir / digest
        if dest.exists() and dest.read_bytes() != content:
            raise ValueError("SHA collision/corrupted store")
        if not dest.exists():
            tmp = body_dir / (digest + ".tmp")
            tmp.write_bytes(content)
            os.replace(tmp, dest)
        record = {"source_id": source, "url": url, "final_url": response.geturl(),
                  "fetched_at": datetime.now(timezone.utc).isoformat(),
                  "sha256": digest, "bytes": len(content), "http_status": status,
                  "content_type": headers.get("Content-Type"),
                  "etag": headers.get("ETag"), "last_modified": headers.get("Last-Modified"),
                  "raw_object": str(dest.relative_to(root)), "ingest_version": "0.1.0",
                  "license_status": "REQUIRES_PER_SOURCE_REVIEW"}
        with (root / "manifest.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    time.sleep(min_interval)  # simple single-process pacing; not a domain-global rate limiter
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description="Single-document official-source snapshot importer")
    parser.add_argument("--url", required=True)
    parser.add_argument("--source", required=True, choices=("congreso", "senado", "boe"))
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--min-interval", type=float, default=3)
    args = parser.parse_args()
    print(json.dumps(import_url(url=args.url, source=args.source, root=args.out,
                                min_interval=args.min_interval), indent=2))


if __name__ == "__main__":
    main()