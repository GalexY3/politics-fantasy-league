"""ABH25B C09–C16: eight frozen public institutional measurement contrasts.

No petition text, person names, petition identifiers or URLs are ever persisted.
Each endpoint is fixed before source access; a blocked endpoint stays blocked.
Never infer that a missing stage or response is a negative institutional action.
"""
import hashlib
import json
import urllib.request
from collections import Counter
from datetime import datetime,timezone
from urllib.parse import urlsplit

SOURCES={
 "C09":("https://petitions.senedd.wales/petitions.json?state=all&page=1","petitions.senedd.wales"),
 "C10":("https://petitions.senedd.wales/petitions.json?state=open&page=1","petitions.senedd.wales"),
 "C11":("https://petitions.senedd.wales/petitions.json?state=completed&page=1","petitions.senedd.wales"),
 "C12":("https://petition.parliament.uk/petitions.json?state=open&page=12","petition.parliament.uk"),
 "C13":("https://petition.parliament.uk/petitions.json?state=closed&page=3","petition.parliament.uk"),
 "C14":("https://petitions.parliament.scot/petitions.json?state=under_consideration&page=12","petitions.parliament.scot"),
 "C15":("https://petitions.senedd.wales/petitions.json?state=referred&page=1","petitions.senedd.wales"),
 "C16":("https://petition.parliament.uk/petitions.json?state=rejected&page=5","petition.parliament.uk")
}
LIMIT=2_000_000
def parse(id, raw):
    if id not in SOURCES or not isinstance(raw,bytes) or not 80<len(raw)<=LIMIT:
        raise ValueError("SOURCE_BOUNDS")
    obj=json.loads(raw)
    if not isinstance(obj,dict) or not isinstance(obj.get("data"),list):
        raise ValueError("SCHEMA_NO_DATA_LIST")
    data=obj["data"]
    if not 0<len(data)<=100:
        raise ValueError("EMPTY_OR_OVERSIZED_PAGE")
    attrs=[]
    ids=set()
    key_count=Counter()
    for row in data:
        if not isinstance(row,dict) or not isinstance(row.get("attributes"),dict):
            raise ValueError("BAD_ROW")
        if row.get("id") is not None:
            if str(row["id"]) in ids:
                raise ValueError("DUPLICATE_ID")
            ids.add(str(row["id"]))
        a=row["attributes"]
        attrs.append(a)
        key_count.update(a.keys())
    # Values exported only for state/stage enumerations, numeric support and
    # date presence. Do NOT include names, titles or other text in output.
    states=Counter(str(a.get("state",a.get("status","UNOBSERVED")))[:64] for a in attrs)
    fields=tuple(sorted(k for k in key_count if any(t in k.lower()
       for t in ("state","status","signatur","support","response","debat",
                 "referr","complet","closed","opened","published","updated"))))
    supported=[]
    for a in attrs:
        n=a.get("signature_count",a.get("signatures_count",None))
        if type(n) is int and n>=0:
            supported.append(n)
    threshold250=sum(n>=250 for n in supported)
    threshold10k=sum(n>=10000 for n in supported)
    threshold100k=sum(n>=100000 for n in supported)
    response_date=sum(bool(a.get("government_response_at")) for a in attrs)
    debate_date=sum(bool(a.get("debate_outcome_at")) for a in attrs)
    response_threshold=sum(bool(a.get("response_threshold_reached_at")) for a in attrs)
    debate_threshold=sum(bool(a.get("debate_threshold_reached_at")) for a in attrs)
    return dict(cycle=id,status="SCHEMA_OBSERVED_ONE_FIXED_PAGE",
        source_sha256=hashlib.sha256(raw).hexdigest(),
        bytes=len(raw),records=len(attrs),ids_present=len(ids),
        state_counts=dict(states),measurement_field_presence={k:key_count[k] for k in fields},
        supported_signature_count=len(supported),
        signatures_ge250=threshold250,signatures_ge10000=threshold10k,
        signatures_ge100000=threshold100k,
        government_response_date_present=response_date,
        threshold_reached_date_present=response_threshold,
        debate_threshold_date_present=debate_threshold,
        debate_outcome_date_present=debate_date,
        no_ids_titles_people_exported=True,one_nonrandom_page=True,
        unavailable_not_zero=True,causal=False)
def run(id):
    url,host=SOURCES[id]
    request=urllib.request.Request(url,headers={
        "Accept":"application/json","User-Agent":"PFL-ABH25B/1.0-public-aggregate"})
    with urllib.request.urlopen(request,timeout=20) as res:
        fin=urlsplit(res.url)
        if fin.scheme!="https" or fin.hostname!=host or res.status!=200:
            raise ValueError("UNVERIFIED_FINAL_HOST")
        raw=res.read(LIMIT+1)
    return parse(id,raw)
if __name__=="__main__":
    # Distinct original tasks, each may fail without preventing others.
    for key in SOURCES:
        try:
            val=run(key)
        except Exception as ex:
            val={"cycle":key,"status":"BLOCKED_NO_VALID_ORIGINAL_PAGE",
                 "error_type":type(ex).__name__,
                 "error_code":str(ex)[:160],"counted":False}
        print(json.dumps(val,ensure_ascii=False,sort_keys=True))
