"""C14B: original UK public aggregate constituency shares for ONE frozen selection.

The sample selects the minimum petition ID on the already-fixed closed page3,
NOT by looking at a person's identity, wording or geographic outcome. UK
constituency count does NOT mean an MP signed or supports a petition. Existing
research on petition geography is acknowledged in prereg.
"""
import hashlib,json,urllib.request
from urllib.parse import urlsplit

PAGE="https://petition.parliament.uk/petitions.json?state=closed&page=3"
HOST="petition.parliament.uk"
LIMIT=2_000_000

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"PFL-ABH25B-spatial-audit/0.1",
                                            "Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=20) as resp:
        u=urlsplit(resp.url)
        if resp.status!=200 or u.hostname!=HOST or u.scheme!="https":
            raise ValueError("NOT_OFFICIAL_HOST")
        raw=resp.read(LIMIT+1)
    if not 100<len(raw)<=LIMIT:
        raise ValueError("SOURCE_SIZE")
    return raw
def select_id(raw):
    obj=json.loads(raw)
    rows=obj.get("data") if isinstance(obj,dict) else None
    if not isinstance(rows,list) or len(rows)!=25:
        raise ValueError("EXPECTED_25_PAGE")
    ids=[]
    for row in rows:
        if not isinstance(row,dict) or str(row.get("id","")).isdigit() is False:
            raise ValueError("NO_NUMERIC_PETITION_ID")
        ids.append(int(row["id"]))
        if row.get("attributes",{}).get("state")!="closed":
            raise ValueError("STATE_DRIFT")
    if len(set(ids))!=len(ids):
        raise ValueError("DUPLICATE_PETITION")
    return min(ids)
def evaluate(raw,petition_id):
    obj=json.loads(raw)
    detail=obj.get("data") if isinstance(obj,dict) else None
    if not isinstance(detail,dict) or int(detail.get("id",-1))!=petition_id:
        raise ValueError("DETAIL_MISMATCH")
    attrs=detail.get("attributes",{})
    parts=attrs.get("signatures_by_constituency")
    if not isinstance(parts,list) or not parts:
        raise ValueError("NO_OFFICIAL_CONSTITUENCY_BREAKDOWN")
    counts=[]
    for row in parts:
        if not isinstance(row,dict) or type(row.get("signature_count")) is not int:
            raise ValueError("BAD_AGGREGATE_COUNT")
        if row["signature_count"]<0:raise ValueError("NEGATIVE_COUNT")
        counts.append(row["signature_count"])
    total=sum(counts)
    if total<=0:raise ValueError("UNSUPPORTED_ZERO_DENOMINATOR")
    shares=[c/total for c in counts]
    hhi=sum(p*p for p in shares)
    return {"schema":"pfl.abh25b.uk_original_constituency_distribution.v1",
            "detail_source_sha256":hashlib.sha256(raw).hexdigest(),
            "detail_source_bytes":len(raw),"constituency_records":len(parts),
            "observed_constituency_signatures":total,
            "overall_petition_signatures":attrs.get("signature_count"),
            "hhi_raw_signature_shares":hhi,
            "effective_equally_weighted_constituencies":1/hhi,
            "top_ten_share":sum(sorted(shares,reverse=True)[:10]),
            "mathematical_uniform_hhi_reference":1/len(parts),
            "no_constituency_names_petition_id_or_person_data_exported":True,
            "not_population_normalized":True,"not_MP_or_party_support":True,
            "one_selected_petition_not_representative":True,"causal":False}
if __name__=="__main__":
    page=fetch(PAGE)
    chosen=select_id(page)
    detail=fetch("https://petition.parliament.uk/petitions/"+str(chosen)+".json")
    out=evaluate(detail,chosen)
    out["fixed_page_sha256"]=hashlib.sha256(page).hexdigest()
    out["page_records"]=25
    print(json.dumps(out,ensure_ascii=False,sort_keys=True))
