"""ABH25B C09-C11: three DISTINCT preregistered UK original petition estimands.

Selected URL pages fixed prior to original bytes. All returned IDs/titles
are read in memory solely for duplicate checks; ONLY aggregates are emitted.
"""
import hashlib,json,sys,urllib.request
from collections import Counter
from urllib.parse import urlsplit
MAX=2_000_000
PROTOCOL={9:("open",(3,11)),10:("rejected",(4,16)),11:("closed",(3,5))}
def process(mode,raw_by_page):
    if mode not in PROTOCOL:raise ValueError("UNKNOWN_MODE")
    expected,pages=PROTOCOL[mode]
    if set(raw_by_page)!=set(pages):raise ValueError("PAGES_NOT_FROZEN")
    seen=set();counts=Counter();docs=[]
    for page in pages:
        raw=raw_by_page[page]
        if not isinstance(raw,bytes) or not 100<len(raw)<=MAX:raise ValueError("RAW_SIZE")
        obj=json.loads(raw);data=obj.get("data") if isinstance(obj,dict) else None
        if not isinstance(data,list) or not data or len(data)>100:raise ValueError("API_SHAPE")
        docs.append({"page":page,"bytes":len(raw),"raw_sha256":hashlib.sha256(raw).hexdigest(),"rows":len(data)})
        for entry in data:
            a=entry.get("attributes") if isinstance(entry,dict) else None
            ident=entry.get("id") if isinstance(entry,dict) else None
            if not isinstance(a,dict) or ident is None or ident in seen:
                raise ValueError("ROW_SCHEMA_OR_DUPLICATE")
            seen.add(ident)
            state=a.get("state")
            if state!=expected:
                raise ValueError("STATE_FILTER_MISMATCH")
            counts["n"]+=1
            if mode==9:
                sig=a.get("signature_count")
                if type(sig) is not int or sig<0:raise ValueError("SIGNATURE_COUNT_MISSING")
                counts["below_10000"]+=int(sig<10000)
                counts["at_least_10000_below_100000"]+=int(10000<=sig<100000)
                counts["at_least_100000"]+=int(sig>=100000)
                t=bool(a.get("response_threshold_reached_at"))
                response=bool(a.get("government_response_at"))
                counts["threshold_at"]+=t
                counts["response_at"]+=response
                counts["threshold_pending_response"]+=int(t and not response)
                counts["closed_at_while_open"]+=int(bool(a.get("closed_at")))
            elif mode==10:
                counts["rejected_at"]+=int(bool(a.get("rejected_at")))
                counts["rejection_object"]+=int(bool(a.get("rejection")))
                counts["response_at"]+=int(bool(a.get("government_response_at")))
                counts["petition_threshold_at"]+=int(bool(a.get("response_threshold_reached_at")))
                counts["closed_at"]+=int(bool(a.get("closed_at")))
            elif mode==11:
                sig=a.get("signature_count")
                if type(sig) is not int or sig<0:raise ValueError("SIGNATURE_COUNT_MISSING")
                eligible=sig>=100000
                counts["eligible_100k"]+=int(eligible)
                counts["eligible_with_debate_outcome"]+=int(eligible and bool(a.get("debate_outcome_at")))
                counts["eligible_with_debate_schedule"]+=int(eligible and bool(a.get("debate_scheduled_on")))
                counts["eligible_without_outcome_date"]+=int(eligible and not a.get("debate_outcome_at"))
                counts["eligible_with_response_at"]+=int(eligible and bool(a.get("government_response_at")))
                counts["sub100k_with_debate"]+=int(not eligible and bool(a.get("debate_outcome_at")))
    return {"schema":f"pfl.abh25b.c{mode:02}.uk_fixed_page_measurement.v1",
            "selected_state":expected,"original_receipts":docs,"aggregates":dict(sorted(counts.items())),
            "not_random_or_population_estimate":True,
            "no_names_titles_ids_or_petition_text_exported":True,
            "negative_absence_does_not_prove_no_institutional_action":True,"causal":False,
            "discriminating_support_ok":(mode!=11 or counts["eligible_100k"]>0)}
def main():
    mode=int(sys.argv[1]) if len(sys.argv)==2 else 0
    if mode not in PROTOCOL:raise ValueError("MODE_REQUIRED_9_10_11")
    state,pages=PROTOCOL[mode];raws={}
    for p in pages:
        uri=f"https://petition.parliament.uk/petitions.json?state={state}&page={p}"
        req=urllib.request.Request(uri,headers={"Accept":"application/json","User-Agent":"PFL-ABH25B-meta/0.1"})
        with urllib.request.urlopen(req,timeout=15) as res:
            u=urlsplit(res.url)
            if res.status!=200 or u.hostname!="petition.parliament.uk" or u.scheme!="https":
                raise ValueError("SOURCE_HOST_OR_STATUS")
            raws[p]=res.read(MAX+1)
    print(json.dumps(process(mode,raws),indent=2,sort_keys=True))
if __name__=="__main__":main()
