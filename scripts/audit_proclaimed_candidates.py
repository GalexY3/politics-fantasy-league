#!/usr/bin/env python3
"""Reproducible narrow *official original* BOE candidacy-list audit.

BOE-A-2023-15066 June 27 proclaimed electoral candidacies, 256-page PDF.
Only Albacete CONGRESO headings before SENADO; no names/candidate
individuals exported. Never infer registered political party, affiliation,
membership, people identity, seat, party coalition components or influence
from a list label. Do not generalize eight local lists to Spain.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unicodedata

DOCUMENT="BOE-A-2023-15066"
ORIGINAL_URL="https://www.boe.es/boe/dias/2023/06/27/pdfs/BOE-A-2023-15066.pdf"
EXPECTED_CODE_SEQUENCE=(1,2,3,4,5,6,7,8)
# Source-specific labels, must agree exactly with original PDF.
EXPECTED_LABELS=("PSOE","FO","PP","PACMA","PUM+J","SUMAR","VOX","RECORTES CERO")
# Never use an acronym as a canonical legal-entity ID.
GROUP_RE=re.compile(r"^\s*(\d{1,2})[.\u2024\uff0e]\s+(.+?)\s*$",re.U)

def normalized(s):
    return " ".join(s.strip().split())

def is_upper_heading(title):
    chars=[x for x in title if x.isalpha()]
    return len(chars)>=6 and sum(x.isupper() for x in chars)/len(chars)>=.95

def extract_albacete_lists(text):
    if not isinstance(text,str) or "JUNTA ELECTORAL DE ALBACETE" not in text:
        raise ValueError("ALBACETE_ANCHOR_MISSING")
    text=text.split("JUNTA ELECTORAL DE ALBACETE",1)[1]
    if "CONGRESO DE LOS DIPUTADOS" not in text:
        raise ValueError("CONGRESS_SEGMENT_MISSING")
    text=text.split("CONGRESO DE LOS DIPUTADOS",1)[1]
    if "\nSENADO" not in text:
        raise ValueError("SENATE_BOUNDARY_MISSING")
    text=text.split("\nSENADO",1)[0]
    rows=[]
    for raw in text.splitlines():
        line=normalized(raw)
        match=GROUP_RE.match(line)
        if not match:continue
        seq=int(match.group(1));title=match.group(2)
        # Exclude candidate names, page footers, uppercase BOE headers.
        if not is_upper_heading(title):continue
        tail=re.search(r"\(([^()]+)\)\s*$",title)
        if not tail:continue
        acronym=tail.group(1)
        if len(acronym)>45:continue
        # Check that all group names are spelled in capital letters.
        rows.append({"order":seq,"electoral_candidacy_label":title,"acronym":acronym,
            "source_kind":"PROCLAIMED_ELECTORAL_CANDIDACY_NOT_LEGAL_PARTY",
            "province":"Albacete","chamber":"Congreso",
            "legal_party_registry_id":None,"people_records_exported":0,
            "not_proclaimed":False})
    orders=tuple(x["order"] for x in rows)
    if orders!=EXPECTED_CODE_SEQUENCE:
        raise ValueError("NOT_THE_EIGHT_ORDERED_CANDIDACIES:"+str(orders))
    got=tuple(x["acronym"] for x in rows)
    if got!=EXPECTED_LABELS:
        raise ValueError("ACRONYM_SEQUENCE_MISMATCH:"+str(got))
    return rows

def audit(pdf, text_override=None):
    path=Path(pdf)
    body=path.read_bytes()
    if not body.startswith(b"%PDF-") or b"%%EOF" not in body[-1024:]:
        raise ValueError("INVALID_ORIGINAL_PDF")
    if text_override is not None:
        text=text_override
    else:
        if shutil.which("pdftotext") is None: raise RuntimeError("PDFTOTEXT_MISSING")
        process=subprocess.run(["pdftotext","-f","1","-l","3","-layout",str(path),"-"],
            capture_output=True,text=True,check=True,timeout=20)
        text=process.stdout
    records=extract_albacete_lists(text)
    return {"source":DOCUMENT,"publisher_domain":"www.boe.es",
        "original_source_url":ORIGINAL_URL,"original_bytes":len(body),
        "sha256":hashlib.sha256(body).hexdigest(),"scope":"ALBACETE_CONGRESO_PROCLAIMED_2023_ONLY",
        "document_date":"2023-06-27","election_date":"2023-07-23",
        "n_candidacy_lists":len(records),"distinct_labels":len(set(x["acronym"] for x in records)),
        "legal_parties_validated":0,"real_people_identified_and_joined":0,
        "records":records,
        "warning":"A candidate list is not necessarily a registered party, nor does any listed name certify party membership or an elected seat."}

def main():
    if len(sys.argv)!=3:raise SystemExit("Usage: audit_proclaimed_candidates.py ORIGINAL.pdf OUTPUT_SUMMARY.json")
    result=audit(sys.argv[1])
    Path(sys.argv[2]).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    # Print aggregate and acronym labels only. Do not publish people names.
    print("BOE_CANDIDACY_ORIGINAL_AUDIT="+json.dumps({k:result[k] for k in
        ("source","sha256","original_bytes","scope","n_candidacy_lists","distinct_labels",
        "legal_parties_validated","real_people_identified_and_joined")},ensure_ascii=False))
    print("BOE_CANDIDACY_ACRONYMS="+json.dumps([x["acronym"] for x in result["records"]]))

if __name__=="__main__":main()
