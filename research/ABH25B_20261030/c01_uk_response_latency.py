"""ABH25B-C01: frozen nonadaptive UK institutional response-lag audit.

Fixed non-adjacent pages 7,17,37,67. First two pages examined previously are
excluded. Results aggregate original public response timestamps only, never
petition names, creator names, text or identifiers. This is NOT random sampling.
"""
from __future__ import annotations
import hashlib
import json
import statistics
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urlsplit

PAGES=(7,17,37,67)
BASE="https://petition.parliament.uk/petitions.json?state=closed&page="
MAX_BYTES=2_000_000
def timestamp(value):
    if not isinstance(value,str) or not value.strip():
        return None
    dt=datetime.fromisoformat(value.replace("Z","+00:00"))
    if dt.utcoffset() is None:
        raise ValueError("NAIVE_RESPONSE_DATE")
    return dt.astimezone(timezone.utc)
def summarize_pages(raw_by_page):
    if set(raw_by_page)!=set(PAGES):
        raise ValueError("UNEXPECTED_SELECTED_PAGES")
    rows=[]; pages=[]; ids=set(); statuses=Counter()
    for page in PAGES:
        raw=raw_by_page[page]
        if not isinstance(raw,bytes) or not 100<len(raw)<=MAX_BYTES:
            raise ValueError("PAGE_SIZE_OR_FORMAT")
        document=json.loads(raw)
        if not isinstance(document,dict) or not isinstance(document.get("data"),list):
            raise ValueError("API_SHAPE")
        entries=document["data"]
        if not entries or len(entries)>100:
            raise ValueError("EMPTY_OR_OVERSIZED_PAGE")
        pages.append({"page":page,"raw_sha256":hashlib.sha256(raw).hexdigest(),
                      "raw_bytes":len(raw),"records":len(entries)})
        for entry in entries:
            attrs=entry.get("attributes") if isinstance(entry,dict) else None
            if not isinstance(attrs,dict) or "id" not in entry:
                raise ValueError("MISSING_ID_OR_ATTRIBUTES")
            if entry["id"] in ids:
                raise ValueError("CROSS_PAGE_DUPLICATE")
            ids.add(entry["id"])
            if attrs.get("state")!="closed":
                raise ValueError("STATE_FILTER_DRIFT")
            for name in ("response_threshold_reached_at","government_response_at","signature_count"):
                if name not in attrs:
                    raise ValueError("MISSING_MEASUREMENT_FIELD")
            statuses[str(attrs["state"])]+=1
            t=timestamp(attrs["response_threshold_reached_at"])
            d=timestamp(attrs["government_response_at"])
            sig=attrs["signature_count"]
            if type(sig) is not int or sig<0:
                raise ValueError("INVALID_SIGNATURE_COUNT")
            lag=(d-t).total_seconds()/86400.0 if t and d else None
            rows.append((sig,t,d,lag,bool(attrs.get("government_response")),bool(attrs.get("debate_outcome_at"))))
    both=[r for r in rows if r[1] is not None and r[2] is not None]
    lags=[r[3] for r in both if r[3]>=0]
    output=dict(schema="pfl.abh25b.uk_response_latency.v1",source="UK_PARLIAMENT_OFFICIAL_JSON",
                fixed_pages=list(PAGES),page_receipts=pages,
                n=len(rows),states=dict(statuses),
                threshold_present=sum(r[1] is not None for r in rows),
                government_response_at_present=sum(r[2] is not None for r in rows),
                government_response_object_present=sum(r[4] for r in rows),
                threshold_only=sum(r[1] is not None and r[2] is None for r in rows),
                response_without_threshold=sum(r[1] is None and r[2] is not None for r in rows),
                inverted_response_dates=sum(r[3] is not None and r[3]<0 for r in rows),
                eligible_lags=len(lags),
                median_days=statistics.median(lags) if lags else None,
                mean_days=statistics.mean(lags) if lags else None,
                lag_le14=sum(x<=14 for x in lags),
                lag_gt14_le21=sum(14<x<=21 for x in lags),
                lag_gt21=sum(x>21 for x in lags),
                min_days=min(lags) if lags else None,
                max_days=max(lags) if lags else None,
                signature_ge100k=sum(r[0]>=100000 for r in rows),
                debate_outcome_timestamp=sum(r[5] for r in rows),
                results_by_signature_band={})
    for label, filt in (("below_100k",lambda s:s<100000),
                        ("at_least_100k",lambda s:s>=100000)):
        arr=[r[3] for r in both if filt(r[0]) and r[3]>=0]
        output["results_by_signature_band"][label]={
            "eligible":len(arr),"median_days":statistics.median(arr) if arr else None,
            "late_over_21":sum(x>21 for x in arr)}
    output.update(no_titles_or_person_data_exported=True,
        sample="FOUR_NONADJACENT_FIXED_SORTED_PAGES_NOT_RANDOM",
        causal=False,response_date_is_published_api_metadata_not_independent_publication_attestation=True,
        source_timing_not_reconstructed_historically=True)
    return output
def main():
    data={}
    for p in PAGES:
        url=BASE+str(p)
        req=urllib.request.Request(url,headers={
            "User-Agent":"PFL-institutional-metadata-audit/0.1","Accept":"application/json"})
        with urllib.request.urlopen(req,timeout=15) as response:
            u=urlsplit(response.url)
            if response.status!=200 or u.hostname!="petition.parliament.uk" or u.scheme!="https":
                raise ValueError("UNTRUSTED_FINAL_HOST")
            data[p]=response.read(MAX_BYTES+1)
    print(json.dumps(summarize_pages(data),ensure_ascii=False,indent=2,sort_keys=True))
if __name__=="__main__":
    main()
