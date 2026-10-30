"""ABH25B C02: bounded Canadian Commons official petition XML schema audit.

No names, identifiers or petition text exported. No external entity parsing,
no official-source authentication claim beyond server URL and byte SHA256.
"""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from urllib.parse import urlsplit
from urllib.request import Request,urlopen
from xml.etree import ElementTree as ET

URL="https://www.ourcommons.ca/petitions/en/Petition/Search?Category=All&output=xml"
CAP=8_000_000
def local(tag):
    return tag.rsplit("}",1)[-1] if isinstance(tag,str) else "NONSTRING"
def inspect_xml(raw):
    if not isinstance(raw,bytes) or not 100<len(raw)<=CAP:
        raise ValueError("SOURCE_SIZE")
    sample=raw[:256].lstrip().lower()
    if b"<html" in sample or b"<!doctype html" in sample:
        raise ValueError("HTML_NOT_XML")
    if b"<!doctype" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("DOCTYPE_OR_ENTITY_NOT_ALLOWED")
    root=ET.fromstring(raw)
    tags=Counter(local(e.tag) for e in root.iter())
    total=sum(tags.values())
    if total>500_000:
        raise ValueError("STRUCTURE_TOO_LARGE")
    response_terms={k:v for k,v in tags.items()
                    if "response" in k.lower() or "reponse" in k.lower() or "réponse" in k.lower()}
    petition_terms={k:v for k,v in tags.items()
                    if "petitionnumber" in k.lower() or "petitio" in k.lower()
                    or "signature" in k.lower() or "status" in k.lower()}
    return {"schema":"pfl.abh25b.canadian_petition_xml_source.v1",
            "source_sha256":hashlib.sha256(raw).hexdigest(),
            "source_bytes":len(raw),"xml_root":local(root.tag),
            "total_xml_elements":total,"unique_element_tags":len(tags),
            "response_related_tag_counts":response_terms,
            "petition_status_signature_tag_counts":petition_terms,
            "has_explicit_response_field":bool(response_terms),
            "has_petition_or_signature_field":bool(petition_terms),
            "metadata_only_no_text_or_identifiers_exported":True,
            "publication_history_not_verified":True,
            "descriptive_schema_only":True}
def main():
    req=Request(URL,headers={"User-Agent":"PFL-ABH25B-research/0.1",
                             "Accept":"application/xml,text/xml"})
    with urlopen(req,timeout=20) as res:
        u=urlsplit(res.url)
        if res.status!=200 or u.scheme!="https" or u.hostname not in (
           "www.ourcommons.ca","ourcommons.ca","petitions.ourcommons.ca"):
            raise ValueError("NOT_OFFICIAL_FINAL_HOST")
        raw=res.read(CAP+1)
    print(json.dumps({"official_final_url":res.url,**inspect_xml(raw)},ensure_ascii=False,indent=2,sort_keys=True))
if __name__=="__main__":main()
