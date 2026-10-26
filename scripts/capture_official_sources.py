#!/usr/bin/env python3
"""BR12M original source HTTPS-capture experiment (bounded and privacy-aware).

This is run in the CI network, never a claim of source access merely by URL.
Stores raw bytes only inside private GitHub Actions' short-lived artifact.
Computes SHA256, validates MIME/magic, bounded shape and HTTPS final host.
No person names or biographies are printed or exported in manifest.
A successful HTTPS transfer does not certify original publication date,
license or completeness of individual political affiliations.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import ssl
import time
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from urllib.error import HTTPError, URLError
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(os.environ.get("PF_CAPTURE_DIR", "/tmp/pf-official-source-capture")).resolve()
MAX_BYTES = 35_000_000
TARGETS = (
    ("congress_active_20260810", "https://www.congreso.es/webpublica/opendata/diputados/DiputadosActivos__20260810050006.json", "json", "www.congreso.es"),
    ("congress_all_20260810", "https://www.congreso.es/webpublica/opendata/diputados/Diput__20260810050141.json", "json", "www.congreso.es"),
    ("interior_congress_elections", "https://descargas.interior.gob.es/datasets/resultados_electorales/Elecciones-Congreso.xlsx", "xlsx", "descargas.interior.gob.es"),
    ("boe_jec_2023_original", "https://www.boe.es/boe/dias/2023/09/01/pdfs/BOE-A-2023-18907.pdf", "pdf", "www.boe.es"),
    ("boe_2023_proclaimed_lists", "https://www.boe.es/boe/dias/2023/06/27/pdfs/BOE-A-2023-15066.pdf", "pdf", "www.boe.es"),
)
XMLNS = {"s":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

def introspect(data:bytes, kind:str)->dict:
    if kind=="pdf":
        if not data.startswith(b"%PDF-") or b"%%EOF" not in data[-1024:]:
            raise ValueError("INVALID_PDF_MAGIC_OR_FOOTER")
        return {"format":"pdf","signature_valid":True,"size_bytes":len(data),
            "notice":"PDF original stored in private short-lived artifact; exact table text not certified automatically"}
    if kind=="xlsx":
        if not data.startswith(b"PK\x03\x04"):raise ValueError("WRONG_OFFICE_SIGNATURE")
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            names=z.namelist()
            if "xl/workbook.xml" not in names or "[Content_Types].xml" not in names:
                raise ValueError("NOT_XLSX")
            root=ET.fromstring(z.read("xl/workbook.xml"))
            sh=root.findall(".//s:sheets/s:sheet",XMLNS)
            sheets=[{"name_length":len(x.attrib.get("name","")),"sheetId":x.attrib.get("sheetId")} for x in sh]
            return {"format":"xlsx","sheets_count":len(sheets),"sheets_shape":sheets[:30],"ZIP_entries":len(names),
                "contains_workbook_xml":True,"privacy":"no cell contents in manifest"}
    if kind=="json":
        if len(data)>MAX_BYTES: raise ValueError("JSON_TOO_LARGE")
        raw=json.loads(data)
        if not isinstance(raw,(list,dict)):raise ValueError("JSON_ROOT_NOT_OBJECT_OR_ARRAY")
        if isinstance(raw,list):
            return {"format":"json","root":"array","top_level_count":len(raw),
                "first_object_keys":sorted(raw[0])[:30] if raw and isinstance(raw[0],dict) else [],
                "privacy":"keys only, no person values"}
        keys=sorted(raw.keys())
        result={"format":"json","root":"object","root_keys":keys[:50],
                "privacy":"keys only, no person values"}
        # Record list lengths but not individual rows
        result["top_level_collections"]={k:len(v) for k,v in raw.items() if isinstance(v,(list,dict))}
        return result
    raise ValueError("UNSUPPORTED_FORMAT")

def fetch_target(name,url,kind,required_hostname,opener=urlopen)->dict:
    result={"id":name,"official_catalogue_url":url,"expected_kind":kind,
        "capture_status":"NOT_CAPTURED","original_binary_captured":False,
        "license":"NOT_CERTIFIED","first_public_at":"NOT_CERTIFIED",
        "authority_authenticated_by_url":"UNVERIFIED_UNTIL_TRANSFER"}
    try:
        request=Request(url,headers={"User-Agent":"PFL-Research-SourceAudit/0.1 (research; access public data)","Accept":"application/json,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*"})
        with opener(request,timeout=22,context=ssl.create_default_context()) as reply:
            final=reply.geturl()
            parsed=urlparse(final)
            if parsed.scheme!="https" or parsed.hostname!=required_hostname:
                raise ValueError("HTTPS_REDIRECT_OUTSIDE_OFFICIAL_HOST")
            body=reply.read(MAX_BYTES+1)
            if len(body)>MAX_BYTES:raise ValueError("ORIGINAL_SOURCE_OVERSIZE")
            if len(body)<20:raise ValueError("ORIGINAL_SOURCE_TOO_SMALL")
            mime=reply.headers.get("content-type","")
            st=reply.status
            if st!=200:raise ValueError("SOURCE_HTTP_NOT_200")
        shape=introspect(body,kind)
        suffix={"json":".json","xlsx":".xlsx","pdf":".pdf"}[kind]
        destination=ROOT/(name+suffix)
        destination.write_bytes(body)
        result.update({"capture_status":"RAW_BYTES_CAPTURED","original_binary_captured":True,
            "https_final_url":final,"http_status":st,"content_type":mime,
            "bytes":len(body),"sha256":hashlib.sha256(body).hexdigest(),
            "download_observed_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
            "shape":shape,
            "provenance_boundary":"HTTPS to expected institutional host with system TLS, but no publisher-signed content hash",
            "raw_filename":destination.name})
    except (HTTPError,URLError,TimeoutError,OSError,ValueError,json.JSONDecodeError,zipfile.BadZipFile,ET.ParseError) as e:
        result.update({"capture_status":"STOP_R5_NETWORK_OR_FORMAT","error_type":type(e).__name__,
            "error":str(e)[:250].replace("\n"," ")})
    return result

def run():
    ROOT.mkdir(parents=True,exist_ok=True)
    items=[fetch_target(*params) for params in TARGETS]
    record={"campaign":"PF-BR12M","as_of_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
        "original_download_attempts":len(items),
        "raw_downloads_success":sum(bool(x["original_binary_captured"]) for x in items),
        "no_raw_political_person_values_printed":True,
        "copyright_or_rights_to_redistribute_individual_rows":"NOT_CERTIFIED",
        "first_public_at_individual_rows":"UNKNOWN",
        "sources":items}
    (ROOT/"capture_manifest.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("OFFICIAL_CAPTURE_RESULTS="+json.dumps({k:record[k] for k in ("original_download_attempts","raw_downloads_success")},ensure_ascii=False))
    for item in items:
        print("OFFICIAL_CAPTURE_TARGET="+json.dumps({k:item.get(k) for k in ("id","capture_status","bytes","sha256","error_type","error","shape")},ensure_ascii=False))
    return record

if __name__=="__main__":run()
