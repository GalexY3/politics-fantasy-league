#!/usr/bin/env python3
"""Bounded documentary extraction of 2023 BOE original proclaimed candidacies.

Observational unit: (document, territorial electoral commission, chamber,
ordinal), NOT a registered political party and NOT a candidate person.
Original binary PDF must be downloaded independently from www.boe.es via
verified TLS and SHA256. Any unexpected split/order is logged as unresolved.
No raw person names, ideological affiliations or scores are exported.
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

BOE="BOE-A-2023-15066"
BOE_URL="https://www.boe.es/boe/dias/2023/06/27/pdfs/BOE-A-2023-15066.pdf"
ORIGINAL_SHA256="d1c179fcfab9889df272753ad3d44513f86cec703805219834b7d048ef0eda20"
JUNTA=re.compile(r"(?m)^[ \t]*JUNTA ELECTORAL DE ([A-ZÁÉÍÓÚÜÑÀÈÏÒÇ\-/ .]+)[ \t]*$")
SENADO=re.compile(r"(?m)^[ \t]*SENADO[ \t]*$")
CONGRESO=re.compile(r"(?m)^[ \t]*CONGRESO DE LOS DIPUTADOS[ \t]*$")
HEADER=re.compile(r"^[ \t]*(\d{1,3})[.\u2024\uff0e]\s+(.+?)\s*$",re.U)

def clean(s:str)->str:
    return " ".join(s.split())

def is_title(s:str)->bool:
    letters=[z for z in s if z.isalpha()]
    return len(letters)>6 and sum(z.isupper() for z in letters)/len(letters)>.95

def province_id(s:str)->str:
    normalized=unicodedata.normalize("NFKD",s.upper())
    letters="".join(c for c in normalized if not unicodedata.combining(c))
    return re.sub(r"[^A-Z0-9]+","_",letters).strip("_")

def extract(text:str)->dict:
    if not isinstance(text,str):raise ValueError("TEXT_MUST_BE_STRING")
    marks=list(JUNTA.finditer(text))
    if not marks:raise ValueError("NO_PROVINCIAL_JUNTAS")
    parsed=[]
    issues=[]
    for index,m in enumerate(marks):
        province=clean(m.group(1))
        body=text[m.end():marks[index+1].start() if index+1<len(marks) else len(text)]
        head=CONGRESO.search(body)
        if head is None:
            issues.append({"province":province,"code":"CONGRESS_HEADING_MISSING"})
            continue
        senator=SENADO.search(body,head.end())
        if senator is None:
            issues.append({"province":province,"code":"SENADO_HEADING_MISSING"})
            continue
        segment=body[head.end():senator.start()]
        lists=[]
        for line in segment.splitlines():
            a=HEADER.match(line)
            if a is None:continue
            title=clean(a.group(2))
            # A nominating list needs a capitalized ORGANIZATION LABEL and
            # a final acronym in parentheses. Person list entries are skipped.
            if not is_title(title):continue
            acronym=re.search(r"\(([^()]{1,55})\)$",title)
            if acronym is None:continue
            n=int(a.group(1))
            value=clean(acronym.group(1))
            lists.append({"candidacy_id":f"{BOE}:{province_id(province)}:CONGRESO:{n:03d}",
                "province_label":province,"position":n,
                "label":title,"acronym":value,
                "entity_semantics":"ELECTORAL_LIST_NOT_REGISTERED_PARTY",
                "person_count_joined":0,"legal_party_registration_id":None})
        indices=[x["position"] for x in lists]
        if not lists:
            issues.append({"province":province,"code":"NO_LIST_HEADINGS_EXTRACTED"})
            continue
        if indices!=list(range(1,len(indices)+1)):
            issues.append({"province":province,"code":"NON_SEQUENTIAL_LIST_POSITIONS",
                "indices":indices[:30]})
            # Fail closed for that province: inconsistent section cannot be certified.
            continue
        if any("NO PROCLAMADA" in z for z in segment.upper().splitlines()):
            issues.append({"province":province,"code":"CONTAINS_NON_PROCLAMATION_NOTICE_REVIEW"})
        parsed.append({"province_label":province,"province_id":province_id(province),
                       "congress_candidacies":len(lists),"lists":lists,
                       "legal_registered_parties_confirmed":0,
                       "people_identified":0})
    unique={x["province_id"] for x in parsed}
    if len(unique)!=len(parsed):
        issues.append({"code":"DUPLICATED_PROVINCE_HEADING","count":len(parsed)-len(unique)})
    return {"source_document":BOE,"election":"2023-07-23",
        "source_date":"2023-06-27",
        "population_scope":"OFFICIAL_NOMINATIONS_2023_CONGRESS_TERRITORIAL_JUNTAS",
        "province_sections_detected":len(marks),
        "province_sections_parsed":len(parsed),
        "list_headings_extracted":sum(x["congress_candidacies"] for x in parsed),
        "distinct_label_acronyms":len({x["acronym"] for p in parsed for x in p["lists"]}),
        "provinces":parsed,"issues":issues,
        "uncertain_province_sections":len(issues),
        "legal_parties_confirmed":0,"people_public_roles_joined":0,
        "official_population_denominator_confirmed":False,
        "no_candidate_person_names_exported":True,
        "coverage_claim":"EXTRACTED_FROM_2023_BOE_PDF_ONLY; completeness of national election must be separately audited",
        "interpretation":"All rows are candidacies, not legal parties, coalitions automatically resolved or persons with political memberships."}

def audit(pdf:Path,text_override:str|None=None,verify_sha:bool=True)->dict:
    raw=Path(pdf).read_bytes()
    if not raw.startswith(b"%PDF-") or b"%%EOF" not in raw[-1024:]:
        raise ValueError("INVALID_PDF_BYTES")
    sha=hashlib.sha256(raw).hexdigest()
    if verify_sha and sha!=ORIGINAL_SHA256:
        raise ValueError("ORIGINAL_PDF_SHA256_CHANGED")
    if text_override is None:
        if shutil.which("pdftotext") is None:raise RuntimeError("PDFTOTEXT_NOT_AVAILABLE")
        x=subprocess.run(["pdftotext","-layout",str(pdf),"-"],
            capture_output=True,text=True,timeout=120,check=True)
        text=x.stdout
    else:text=text_override
    outcome=extract(text)
    outcome.update({"sha256":sha,"original_bytes":len(raw),
        "source_url":BOE_URL,"hash_matches_known_original":sha==ORIGINAL_SHA256})
    return outcome

def main():
    if len(sys.argv)!=3:raise SystemExit("Usage: audit_boe_nominations_all.py ORIGINAL.pdf OUT.json")
    a=audit(Path(sys.argv[1]))
    Path(sys.argv[2]).write_text(json.dumps(a,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    summary={k:a[k] for k in ("sha256","province_sections_detected","province_sections_parsed",
        "list_headings_extracted","distinct_label_acronyms","uncertain_province_sections")}
    print("BOE_NOMINATION_ATLAS="+json.dumps(summary,ensure_ascii=False))
    print("BOE_NOMINATION_ERRORS="+json.dumps(a["issues"][:12],ensure_ascii=False))
    # Log bounded, ASCII-escaped PUBLIC CANDIDACY LABELS only, never people names.
    # Chunks enable reproducible import without putting PDF/persons into Git commits.
    safe={k:a[k] for k in ("source_document","source_date","election","sha256",
        "original_bytes","province_sections_detected","province_sections_parsed",
        "list_headings_extracted","distinct_label_acronyms","provinces","issues",
        "legal_parties_confirmed","people_public_roles_joined",
        "official_population_denominator_confirmed")}
    compact=json.dumps(safe,ensure_ascii=True,separators=(",",":"))
    chunks=[compact[i:i+3600] for i in range(0,len(compact),3600)]
    for k,part in enumerate(chunks):
        print(f"BOE_PUBLIC_AGG_CHUNK={k+1}/{len(chunks)}:"+part)

    # Genuine incompleteness remains a recorded STOP, not a silently corrected one.
    if a["province_sections_parsed"]<2:
        raise SystemExit("INSUFFICIENT_PROVINCIAL_SECTIONS")
if __name__=="__main__":main()
