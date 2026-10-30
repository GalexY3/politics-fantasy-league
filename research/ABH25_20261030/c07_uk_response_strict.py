"""ABH25 C07: official UK petitions second CLOSED page, response vs threshold."""
import hashlib, json, urllib.request
URL="https://petition.parliament.uk/petitions.json?state=closed&page=2"
LIMIT=2_000_000
def extract(raw):
    obj=json.loads(raw);items=obj.get('data') if isinstance(obj,dict) else None
    if not isinstance(items,list) or not items:raise ValueError('API_OR_EMPTY')
    counts=dict(records=0,closed=0,threshold_at=0,response_at=0,response_object=0,
                threshold_without_response_at=0,response_before_threshold=0,
                debate_at=0,date_unparseable=0)
    for item in items:
        a=item.get('attributes')
        if not isinstance(a,dict): raise ValueError('ROW_SCHEMA')
        if any(k not in a for k in ('government_response_at','response_threshold_reached_at',
                                    'government_response','state','signature_count')):raise ValueError('FIELD_MISSING')
        counts['records']+=1
        counts['closed']+=int(a['state']=='closed')
        t=a['response_threshold_reached_at'];u=a['government_response_at']
        counts['threshold_at']+=int(bool(t))
        counts['response_at']+=int(bool(u))
        counts['response_object']+=int(bool(a['government_response']))
        counts['threshold_without_response_at']+=int(bool(t) and not bool(u))
        counts['response_before_threshold']+=int(bool(t) and bool(u) and str(u)<str(t))
        counts['debate_at']+=int(bool(a.get('debate_outcome_at')))
    if counts['closed']!=counts['records']:raise ValueError('STATE_FILTER_DRIFT')
    if counts['response_before_threshold']:raise ValueError('TEMPORAL_INCONSISTENCY_IN_RAW_DATA')
    return {**counts,'raw_sha256':hashlib.sha256(raw).hexdigest(),'raw_bytes':len(raw),
            'sample':'SECOND_PAGE_ONLY_NONREPRESENTATIVE','not_evidence_of_compliance':True,
            'identifiers_or_titles_exported':False}
if __name__=='__main__':
    req=urllib.request.Request(URL,headers={'User-Agent':'PFL-ABH25-C07/1.0'})
    with urllib.request.urlopen(req,timeout=20) as z:
        if z.status!=200 or z.geturl().split('/')[2]!='petition.parliament.uk':raise ValueError('HOST')
        raw=z.read(LIMIT+1)
    if not 50<len(raw)<=LIMIT:raise ValueError('SIZE')
    print(json.dumps(extract(raw),indent=2))
