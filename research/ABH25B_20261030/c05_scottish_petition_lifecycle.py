"""ABH25B-C05: Scottish Parliament petition API source schema (one fixed page).

This diagnostic reads public JSON original bytes and publishes only aggregate
field-presence counts. This does not identify parliamentary intervention outcomes.
"""
from __future__ import annotations
from collections import Counter
import hashlib,json
import urllib.request
from urllib.parse import urlsplit

URL="https://petitions.parliament.scot/petitions.json?state=closed&page=4"
MAX=1_000_000
KEYWORDS=("response","minister","government_reply","first_public","publication_version")
def audit(raw):
    if not isinstance(raw,bytes) or not 100<len(raw)<=MAX:
        raise ValueError("RAW_SIZE")
    doc=json.loads(raw)
    if not isinstance(doc,dict) or not isinstance(doc.get("data"),list) or not doc["data"]:
        raise ValueError("API_SHAPE")
    counts=Counter();statuses=Counter();seen=set();named=Counter()
    for x in doc["data"]:
        if not isinstance(x,dict) or not isinstance(x.get("attributes"),dict):
            raise ValueError("ROW_SHAPE")
        identity=x.get("pe_number")
        if not isinstance(identity,str) or not identity:
            raise ValueError("MISSING_PETITION_KEY")
        if identity in seen:
            raise ValueError("DUPLICATE_PETITION_KEY")
        seen.add(identity)
        a=x["attributes"]
        statuses[str(a.get("status"))]+=1
        for key in ("created_at","opened_at","updated_at","under_consideration_at",
                    "closed_at","archived_at","first_public_at"):
            counts[key]+=int(bool(a.get(key)))
        for key,value in a.items():
            if any(fragment in key.lower() for fragment in KEYWORDS):
                named[key]+=1
    return dict(schema="pfl.abh25b.scotland_petition_lifecycle.v1",
      fixed_page=4,raw_sha256=hashlib.sha256(raw).hexdigest(),
      raw_bytes=len(raw),records=len(seen),status_counts=dict(statuses),
      date_field_nonempty_counts=dict(counts),
      response_or_publication_related_field_presence=dict(named),
      can_identify_first_public_history_from_current_page=False,
      no_person_names_petition_titles_or_ids_emitted=True,
      interpretation="STAGE_FIELDS_ARE_NOT_PROOF_OF_GOVERNMENT_RESPONSE",
      population_generalization=False,causal=False)
def main():
    req=urllib.request.Request(URL,headers={"Accept":"application/json",
                                             "User-Agent":"PFL-ABH25B-Scottish-source/0.1"})
    with urllib.request.urlopen(req,timeout=15) as resp:
        u=urlsplit(resp.url)
        if resp.status!=200 or u.scheme!="https" or u.hostname!="petitions.parliament.scot":
            raise ValueError("UNTRUSTED_SOURCE")
        raw=resp.read(MAX+1)
    print(json.dumps(audit(raw),ensure_ascii=False,sort_keys=True,indent=2))
if __name__=="__main__":main()
