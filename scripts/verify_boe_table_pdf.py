#!/usr/bin/env python3
"""Compare *actual original BOE PDF bytes* against a declared Table-I transcription.

The check is independent of the other 2023 electoral CSV source. It verifies
the original page's 52 lines and six electoral totals via pdftotext -layout.
Does NOT verify individual candidature identities or first publication of a
later derived dataset. Exit !=0 on any mismatch or unsupported PDF extraction.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import unicodedata


def compact(value):
    base=unicodedata.normalize("NFKD",value).casefold()
    return "".join(c for c in base if not unicodedata.combining(c) and c.isalnum())


def reference_rows(path):
    raw=Path(path).read_text(encoding="utf8")
    rows=[]
    for line in raw.splitlines():
        if not line or line.startswith("#") or line.startswith("province_code|"):
            continue
        fields=line.split("|")
        if len(fields)!=8:
            raise ValueError("MANUAL_TRANSCRIPTION_WRONG_WIDTH")
        province=fields[1]
        nums=list(map(int,fields[2:]))
        if len(nums)!=6:raise ValueError("MANUAL_TRANSCRIPTION_INCOMPLETE")
        rows.append({"province_code":fields[0],"province":province,"counts":nums})
    if len(rows)!=52 or len(set(r["province_code"] for r in rows))!=52:
        raise ValueError("MANUAL_TRANSCRIPTION_NOT_52")
    return rows


def parse_pdf_lines(text):
    lines=[]
    for line in text.splitlines():
        # Layout PDF output keeps aligned columns, one province per line.
        parts=re.findall(r"\d+(?:\.\d{3})*|\S+",line)
        if len(parts)<7:
            continue
        numbers=re.findall(r"(?<!\w)\d{1,3}(?:\.\d{3})+|\b\d+\b",line)
        if len(numbers)<6:
            continue
        if len(numbers)>6:
            continue
        seq=" ".join(numbers)
        pos=line.find(numbers[0])
        if pos<=0:
            continue
        province=line[:pos].strip()
        if not province or any(c.isdigit() for c in province):
            continue
        values=[int(x.replace(".","")) for x in numbers]
        lines.append({"province":province,"counts":values})
    return lines


def verify(pdf,transcript,runner=None):
    pdf=Path(pdf)
    data=pdf.read_bytes()
    if not data.startswith(b"%PDF-") or b"%%EOF" not in data[-1024:]:
        raise ValueError("PDF_SIGNATURE_INVALID")
    if runner is None:
        if not shutil.which("pdftotext"):
            raise RuntimeError("PDFTOTEXT_UNAVAILABLE")
        cmd=["pdftotext","-f","2","-l","2","-layout",str(pdf),"-"]
        process=subprocess.run(cmd,capture_output=True,encoding="utf8",timeout=20,check=True)
        text=process.stdout
    else:
        text=runner
    source=reference_rows(transcript)
    actual=parse_pdf_lines(text)
    by_name={}
    for row in actual:
        key=compact(row["province"])
        by_name.setdefault(key,[]).append(row["counts"])
    matches=[]
    errors=[]
    for row in source:
        k=compact(row["province"])
        found=by_name.get(k,[])
        if len(found)!=1:
            errors.append({"province_code":row["province_code"],"type":"NOT_UNIQUELY_FOUND", "matches":len(found)})
            continue
        if found[0]!=row["counts"]:
            errors.append({"province_code":row["province_code"],"type":"SIX_FIELDS_DISAGREE","actual":found[0],"previous_transcription":row["counts"]})
        else:
            matches.append(row["province_code"])
    return {
        "source":"BOE-A-2023-18907 Cuadro I original PDF page 2",
        "raw_sha256":hashlib.sha256(data).hexdigest(),
        "original_bytes":len(data),
        "pdf_text_extraction":"pdftotext -f 2 -l 2 -layout (or supplied text for tests)",
        "reference_provinces":52,"unique_provinces_matched":len(matches),
        "reconciled_cells":len(matches)*6,
        "errors":errors,
        "full_table_verified":len(matches)==52 and len(errors)==0,
        "scope_warning":"Checks numerical Table I only; no complete legal party/person roster or individual vote attribution"
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("transcription")
    ap.add_argument("--output",default=None)
    args=ap.parse_args()
    report=verify(args.pdf,args.transcription)
    if args.output:
        Path(args.output).write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print("BOE_PDF_TABLE_AUDIT="+json.dumps({k:report[k] for k in ("raw_sha256","original_bytes","reference_provinces","unique_provinces_matched","reconciled_cells","full_table_verified","errors")},ensure_ascii=False))
    if not report["full_table_verified"]:
        raise SystemExit(2)


if __name__=="__main__":main()
