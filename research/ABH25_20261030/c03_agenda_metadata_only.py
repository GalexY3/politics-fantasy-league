#!/usr/bin/env python3
"""ABH25-C03 stage0: official French commission agenda metadata ONLY.

Forbidden in this stage: committee-minute HTML, petition outcomes, names/titles
or matching to decision_commission. This is not a valid scientific cycle.
"""
import csv
import hashlib
import io
import json
import urllib.request
from urllib.parse import urlsplit

URL = "https://data.assemblee-nationale.fr/static/openData/repository/17/vp/reunions/reunions_init_commission_libre_office.csv"
PUBLISHED_MD5 = "255fd1632c8993b3dcf6d6c303b3d2d3"
LIMIT = 30_000_000

def metadata(blob):
    if len(blob) < 50 or len(blob) > LIMIT:
        raise ValueError("SOURCE_SIZE")
    digest = hashlib.sha256(blob).hexdigest()
    md5 = hashlib.md5(blob).hexdigest()  # publisher file identity ONLY
    if md5 != PUBLISHED_MD5:
        raise ValueError("PUBLISHER_MD5_DRIFT:" + md5)
    text = blob.decode("utf-8-sig", errors="strict")
    try:
        dialect = csv.Sniffer().sniff(text[:8192], delimiters=";,")
        reader = csv.reader(io.StringIO(text), dialect)
        header = next(reader)
        count = sum(1 for _ in reader)
    except (csv.Error, StopIteration) as exc:
        raise ValueError("CSV_SCHEMA_OR_PARSE") from exc
    if not header or len(set(header)) != len(header):
        raise ValueError("EMPTY_OR_DUPLICATED_HEADER")
    return {"status":"OFFICIAL_METADATA_ONLY_NO_OUTCOMES",
            "source_sha256":digest,"source_bytes":len(blob),
            "publisher_md5_match":True,"header":header,
            "rows":count,"meeting_outcomes_read":False,
            "selection_frozen":False,"valid_AB_cycle":False}

def main():
    req = urllib.request.Request(URL,headers={"User-Agent":"PFL-methodology-audit/0.1"})
    with urllib.request.urlopen(req,timeout=20) as res:
        if res.status != 200 or urlsplit(res.url).hostname != "data.assemblee-nationale.fr":
            raise ValueError("SOURCE_REDIRECT_OR_STATUS")
        blob = res.read(LIMIT+1)
    print(json.dumps(metadata(blob),ensure_ascii=False,indent=2))

if __name__ == "__main__":
    main()
