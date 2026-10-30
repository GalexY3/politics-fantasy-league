"""ABH25-C04. Exactly one official UK closed petition page, aggregate metadata only."""
import hashlib,json,urllib.request
from urllib.parse import urlsplit
URL='https://petition.parliament.uk/petitions.json?state=closed&page=1'
LIMIT=2_000_000
def analyze(raw):
    if not 100<=len(raw)<=LIMIT: raise ValueError('SIZE_GUARD')
    obj=json.loads(raw)
    if not isinstance(obj,dict) or not isinstance(obj.get('data'),list): raise ValueError('UNEXPECTED_API_SCHEMA')
    items=obj['data']
    if not items: raise ValueError('EMPTY_SAMPLE')
    keys=set();n_response=0;n_debate=0;n_missing_response=0;closed=0
    response_type_counts={};status_counts={}
    for item in items:
        if not isinstance(item,dict) or not isinstance(item.get('attributes'),dict): raise ValueError('ROW_SCHEMA')
        a=item['attributes'];keys.update(a.keys())
        state=a.get('state');status_counts[str(state)]=status_counts.get(str(state),0)+1
        if state=='closed': closed+=1
        vals={k:v for k,v in a.items() if 'response' in k.lower()}
        response_type_counts.update({k:response_type_counts.get(k,0)+1 for k in vals})
        if any(v not in (None,'',[],{}) for v in vals.values()): n_response+=1
        else:n_missing_response+=1
        if any('debate' in k.lower() and v not in (None,'',[],{}) for k,v in a.items()): n_debate+=1
    return dict(schema='pfl.abh25.c04.uk_measurement.v1',sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),
       records=len(items),closed_count=closed,state_counts=status_counts,attribute_keys=sorted(keys),
       response_field_presence=response_type_counts,nonempty_response_related_rows=n_response,
       missing_or_empty_response_related_rows=n_missing_response,nonempty_debate_related_rows=n_debate,
       interpretation='NONEMPTY_RESPONSE_RELATED_FIELD_NOT_INDEPENDENT_GOVERNMENT_RESPONSE_VERIFICATION',
       sample='FIRST_PAGE_ONLY_NONREPRESENTATIVE',human_details_exported=False,
       causal=False,other_pages_read=False)
def main():
    req=urllib.request.Request(URL,headers={'User-Agent':'PFL-ABH25-research-audit/0.1','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=20) as resp:
        if resp.status!=200 or urlsplit(resp.url).hostname!='petition.parliament.uk':raise ValueError('HTTP_REDIRECT_OR_STATUS')
        data=resp.read(LIMIT+1)
    print(json.dumps(analyze(data),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
