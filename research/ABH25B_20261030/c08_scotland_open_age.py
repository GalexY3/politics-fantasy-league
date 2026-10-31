"""ABH25B C08: preselected Scottish under-consideration petition right-censor audit."""
from collections import Counter
from datetime import datetime,timezone
from urllib.parse import urlsplit
import hashlib,json,statistics,urllib.request

SOURCE="https://petitions.parliament.scot/petitions.json?state=under_consideration&page=5"
CUT=datetime(2026,10,30,tzinfo=timezone.utc)
MAX=1_000_000
def at(value):
    if value is None:return None
    if not isinstance(value,str):raise ValueError("BAD_DATE")
    d=datetime.fromisoformat(value.replace("Z","+00:00"))
    if d.utcoffset() is None:raise ValueError("NAIVE_DATE")
    return d.astimezone(timezone.utc)
def analysis(raw):
    if not isinstance(raw,bytes) or not 100<len(raw)<=MAX:raise ValueError("RAW_SIZE")
    obj=json.loads(raw);rows=obj.get("data") if isinstance(obj,dict) else None
    if not isinstance(rows,list) or not rows:raise ValueError("SHAPE_OR_EMPTY")
    seen=set();ages=[];missing=0;future=0;already_closed=0;statuses=Counter()
    for x in rows:
        if not isinstance(x,dict) or not isinstance(x.get("attributes"),dict):raise ValueError("ROW_SHAPE")
        name=x.get("pe_number")
        if not isinstance(name,str) or not name or name in seen:raise ValueError("DUPLICATE_ID")
        seen.add(name);a=x["attributes"];statuses[str(a.get("status"))]+=1
        if a.get("status") not in ("under_consideration","under consideration"):
            raise ValueError("STATE_MISMATCH")
        if a.get("closed_at"):already_closed+=1
        d=at(a.get("opened_at"))
        if d is None:missing+=1
        elif d>CUT:future+=1
        else:ages.append((CUT-d).total_seconds()/86400)
    return dict(schema="pfl.abh25b.c08.scotland_right_censored_open_ages.v1",
      fixed_page=5,as_of="2026-10-30T00:00:00Z",raw_sha256=hashlib.sha256(raw).hexdigest(),
      raw_bytes=len(raw),records=len(rows),statuses=dict(statuses),
      valid_open_ages=len(ages),missing_opened_at=missing,future_opened_at=future,
      closed_at_when_open=already_closed,median_observed_age_days=statistics.median(ages) if ages else None,
      min_age_days=min(ages) if ages else None,max_age_days=max(ages) if ages else None,
      age_gt365=sum(x>365 for x in ages),
      right_censored=True,closure_duration_not_observed=True,
      no_titles_or_ids_exported=True,not_random_no_population_hazard=True)
def main():
    req=urllib.request.Request(SOURCE,headers={"Accept":"application/json","User-Agent":"PFL-C08/0.1"})
    with urllib.request.urlopen(req,timeout=15) as res:
        u=urlsplit(res.url)
        if res.status!=200 or u.hostname!="petitions.parliament.scot" or u.scheme!="https":raise ValueError("UNTRUSTED_FINAL_URL")
        raw=res.read(MAX+1)
    print(json.dumps(analysis(raw),indent=2,sort_keys=True))
if __name__=="__main__":main()
