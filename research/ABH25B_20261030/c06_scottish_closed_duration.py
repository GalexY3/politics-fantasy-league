"""ABH25B-C06 — fixed Scottish closed-petition duration original audit."""
import hashlib,json,statistics,urllib.request
from datetime import datetime,timezone
from urllib.parse import urlsplit
SOURCE="https://petitions.parliament.scot/petitions.json?state=closed&page=9"
LIMIT=1_000_000
def instant(x):
    if x is None:return None
    if not isinstance(x,str):raise ValueError("NONSTRING_DATE")
    d=datetime.fromisoformat(x.replace("Z","+00:00"))
    if d.utcoffset() is None:raise ValueError("NAIVE_DATE")
    return d.astimezone(timezone.utc)
def durations(raw):
    if not isinstance(raw,bytes) or not 100<len(raw)<=LIMIT:raise ValueError("BAD_BYTES")
    obj=json.loads(raw);items=obj.get("data") if isinstance(obj,dict) else None
    if not isinstance(items,list) or not items:raise ValueError("API_SHAPE")
    seen=set();intervals=[];absent=0;reversed_=0;status={}
    for x in items:
        if not isinstance(x,dict) or not isinstance(x.get("attributes"),dict):raise ValueError("ROW_SCHEMA")
        ident=x.get("pe_number")
        if not isinstance(ident,str) or not ident or ident in seen:raise ValueError("DUPLICATE_ID")
        seen.add(ident);a=x["attributes"];kind=str(a.get("status"))
        status[kind]=status.get(kind,0)+1
        if kind!="closed":raise ValueError("STATE_MISMATCH")
        opened=instant(a.get("opened_at"));closed=instant(a.get("closed_at"))
        if opened is None or closed is None:absent+=1;continue
        days=(closed-opened).total_seconds()/86400
        if days<0:reversed_+=1;continue
        intervals.append(days)
    return dict(schema="pfl.abh25b.c06.scottish_closed_duration.v1",
      page=9,raw_sha256=hashlib.sha256(raw).hexdigest(),source_bytes=len(raw),
      observed_closed=len(seen),both_dates_valid=len(intervals),
      absent_dates=absent,reversed_dates=reversed_,statuses=status,
      median_calendar_days=statistics.median(intervals) if intervals else None,
      min_calendar_days=min(intervals) if intervals else None,
      max_calendar_days=max(intervals) if intervals else None,
      duration_over365=sum(x>365 for x in intervals),
      duration_over730=sum(x>730 for x in intervals),
      no_petition_ids_or_titles_exported=True,
      population="CLOSED_ONLY_SORTED_FIXED_PAGE_NONREPRESENTATIVE",
      cannot_estimate_open_case_hazards_or_signature_effect=True)
def main():
    req=urllib.request.Request(SOURCE,headers={"Accept":"application/json","User-Agent":"PFL-C06-source/0.1"})
    with urllib.request.urlopen(req,timeout=15) as f:
        u=urlsplit(f.url)
        if f.status!=200 or u.hostname!="petitions.parliament.scot" or u.scheme!="https":raise ValueError("INVALID_FINAL_URL")
        blob=f.read(LIMIT+1)
    print(json.dumps(durations(blob),sort_keys=True,indent=2))
if __name__=="__main__":main()
