"""Conservative ONE-vote reconciliation of official nominal JSON, roster, and secondary codes.

No network, no names/codes in output. Not a historical eligibility certificate.
Fixtures, even if passing, are NOT evidence about real deputies.
"""
from __future__ import annotations
import hashlib
import json
from collections import Counter

LABEL = {"Sí":"S","No":"N","Abstención":"A","No vota":"X"}
OFFICIAL = {"S":"afavor","N":"enContra","A":"abstenciones","X":"noVotan"}
SECONDARY = {"S":"si","N":"no","A":"abstencion","X":"noVota"}

def _count(d, key):
    v=d.get(key)
    if type(v) is not int or v<0:
        raise ValueError("Invalid nonnegative integer: "+key)
    return v

def roster_mapping(raw: bytes) -> dict[str,str]:
    """Exact surname, first-name matching mirrors upstream, but fails on collisions."""
    result={}
    codes=set()
    for line in raw.decode("utf-8-sig").splitlines():
        if not line.strip(): continue
        p=line.split("|")
        if len(p)<3 or not all(v.strip() for v in p[:3]):
            raise ValueError("Incomplete roster row")
        code, surname, name=(v.strip() for v in p[:3])
        key=f"{surname}, {name}"
        if key in result or code in codes:
            raise ValueError("Ambiguous duplicate roster name or code")
        codes.add(code); result[key]=code
    if not result: raise ValueError("Empty roster")
    return result

def indexed_codes(record):
    groups=record.get("votos")
    if not isinstance(groups,dict) or any(k not in OFFICIAL for k in groups):
        raise ValueError("Invalid secondary dictionary")
    result={k:set() for k in OFFICIAL}
    seen=set()
    for category,raw in groups.items():
        if not isinstance(raw,str): raise ValueError("Codes must be whitespace-delimited")
        parts=raw.split()
        if len(set(parts))!=len(parts) or any(code in seen for code in parts):
            raise ValueError("Duplicate secondary code")
        seen.update(parts); result[category].update(parts)
    return result

def reconcile_vote(official_bytes:bytes, derivative:dict, roster_bytes:bytes)->dict:
    d=json.loads(official_bytes)
    if not isinstance(d,dict):raise ValueError("Official JSON must be object")
    d=d.get("data",d)
    if not isinstance(d,dict) or not isinstance(d.get("totales"),dict):
        raise ValueError("Unknown official schema")
    totals={k:_count(d["totales"],v) for k,v in OFFICIAL.items()}
    sec=derivative.get("totales")
    if not isinstance(sec,dict):raise ValueError("Missing secondary totals")
    sec_totals={k:_count(sec,v) for k,v in SECONDARY.items()}
    roster=roster_mapping(roster_bytes)
    observed=indexed_codes(derivative)
    common={
        "source_sha256":hashlib.sha256(official_bytes).hexdigest(),
        "roster_sha256":hashlib.sha256(roster_bytes).hexdigest(),
        "secondary_totals_match_official":sec_totals==totals,
        "indexed_secondary_counts_by_option":{k:len(v) for k,v in observed.items()},
        "source_evidence":"ONE_ORIGINAL_JSON_AND_DERIVED_RECORD"
    }
    rows=d.get("votaciones")
    if rows is None or rows==[]:
        return {**common,"status":"NO_ORIGINAL_NOMINAL_ROWS",
                "unmatched_names_by_option":None,"roster_resolution_coverage":None,
                "individual_match_status":"NOT_IDENTIFIABLE"}
    if not isinstance(rows,list):raise ValueError("Original vote rows must be list")
    used_names=set(); used_codes=set()
    counts=Counter(); missing=Counter(); resolved={k:set() for k in OFFICIAL}
    for row in rows:
        if not isinstance(row,dict) or row.get("voto") not in LABEL:
            raise ValueError("Invalid original vote category")
        name=row.get("diputado")
        if not isinstance(name,str) or not name.strip():raise ValueError("Missing original name")
        name=name.strip()
        if name in used_names:raise ValueError("Duplicate original name")
        used_names.add(name); cat=LABEL[row["voto"]];counts[cat]+=1
        code=roster.get(name)
        if code is None:missing[cat]+=1
        else:
            if code in used_codes:raise ValueError("Duplicate resolved code")
            used_codes.add(code);resolved[cat].add(code)
    equal=all(resolved[k]==observed[k] for k in OFFICIAL)
    nominal_totals_match=all(counts[k]==totals[k] for k in OFFICIAL)
    missing_total=sum(missing.values())
    if missing_total:
        individual_status="INCOMPLETE_UNMATCHED"
    elif not equal:
        individual_status="CODE_SET_MISMATCH"
    elif not nominal_totals_match:
        individual_status="NOMINAL_TOTAL_MISMATCH"
    elif sec_totals!=totals:
        individual_status="AGGREGATE_TOTAL_MISMATCH"
    else:
        individual_status="SAME_CODE_SETS"
    return {**common,"status":"STRUCTURAL_RECONCILIATION",
            "official_nominal_counts_match_official_totals":nominal_totals_match,
            "official_nominal_count_by_option":{k:counts[k] for k in OFFICIAL},
            "roster_resolved_count_by_option":{k:len(resolved[k]) for k in OFFICIAL},
            "unmatched_names_by_option":{k:missing[k] for k in OFFICIAL},
            "roster_resolution_coverage":{"resolved":len(used_codes),"nominal_rows":len(rows),
                                           "unmatched":missing_total},
            "secondary_codes_equal_resolved_official":equal,
            "individual_match_status":individual_status,
            "limitations":["No historical roster proof","One vote only","No first-publication timestamp"]}
