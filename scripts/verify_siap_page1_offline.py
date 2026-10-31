"""Independent, offline metadata replay of the one SIAP page captured on 2026-10-31.

No network, cookie access, outcomes, names, titles or source rows exported.
The original HTML remains outside Git, is validated by an exact byte digest,
and is only used to verify page/identifier *counts*. This independent parser
was added AFTER capture, hence is QA replication, NOT a preregistered study.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit

from politics_fantasy.procedural_index_contract import (
    CaseRef, FrameScope, PageEvidence, audit_pages, GateError,
)

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCE = ("https://www.parlament.cat/web/activitat-parlamentaria/"
                   "iniciatives-legislatives/proposicions-llei/index.html")
SHA_ORIGINAL = "3846b9fec8f20b426bfa1c231b717e0c20664d08aaf8586e49171339d927fc8d"
SHA_CAPTURE_RECEIPT = "57cd91bb7bf838aaf899305e67ac912223440d9268093282796706e941d1870b"
SHA_PRECAPTURE_FREEZE = "19d35816554f10c753c76657ccd8b4db97c757f402c7170390a90a2f2c29e7ea"
SHA_PRECAPTURE_PARSER = "ff14bbebc9fee8d56b3afa432eff9794ff4805e815cf99c955d3c8726b37ae3b"
SHA_METADATA = "ee2824bd526fec8e563ff7f8e08a0b4fb8c080645852fa334ce05320bd2d12c4"
CODE = re.compile(r"(?<![\w-])(202-\d{5}/\d{2})(?!\d)")
PAGER = re.compile(r"P[àa]gina\s+(\d+)\s+de\s+(\d+)",re.I)


def pairs_unique(pairs):
    obj={}
    for key,value in pairs:
        if key in obj:
            raise GateError("DUPLICATED_RECEIPT_KEY")
        obj[key]=value
    return obj


def pinned(path:Path,expected:str,limit:int) -> bytes:
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= limit:
        raise GateError("SOURCE_OR_RECEIPT_MISSING")
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=expected:
        raise GateError("ORIGINAL_OR_RECEIPT_HASH_CHANGED")
    return raw


class SIAPPage(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden=0
        self.anchor=None
        self.href=None
        self.text=[]
        self.ids=[]
        self.outside=[]
        self.discarded=0

    def handle_starttag(self,tag,attrs):
        if tag in ("script","style"):
            self.hidden += 1
        if tag=="a":
            if self.anchor is not None:
                raise GateError("NESTED_ANCHORS")
            self.anchor=[]
            self.href=dict(attrs).get("href")

    def handle_endtag(self,tag):
        if tag in ("script","style") and self.hidden:
            self.hidden -= 1
        if tag=="a" and self.anchor is not None:
            matches=CODE.findall("".join(self.anchor))
            if matches:
                url=urlsplit(urljoin(EXPECTED_SOURCE,self.href or ""))
                if (url.scheme!="https" or url.hostname!="www.parlament.cat"
                        or url.username or url.password or url.port):
                    self.discarded += len(matches)
                else:
                    self.ids.extend(matches)
            self.anchor=None
            self.href=None

    def handle_data(self,value):
        if self.hidden:
            return
        self.text.append(value)
        if self.anchor is not None:
            self.anchor.append(value)


def parse_only_pagination_and_source_keys(raw:bytes) -> tuple[int,int,tuple[str,...]]:
    if not isinstance(raw,bytes) or not 0 < len(raw) < 1_000_000:
        raise GateError("BAD_ORIGINAL_HTML_SIZE")
    try:
        txt=raw.decode("utf-8-sig","strict")
    except UnicodeError as exc:
        raise GateError("INVALID_SOURCE_HTML_ENCODING") from exc
    p=SIAPPage()
    p.feed(txt)
    p.close()
    page_pairs={(int(a),int(b)) for a,b in PAGER.findall(" ".join(p.text))}
    if len(page_pairs)!=1 or not p.ids or p.discarded:
        raise GateError("BAD_PAGINATION_OR_UNTRUSTED_SOURCE_LINKS")
    n,total=next(iter(page_pairs))
    if n!=1 or not 1<=total<=600 or len(p.ids)!=len(set(p.ids)):
        raise GateError("WRONG_PAGE_OR_DUPLICATE_LINKS")
    return n,total,tuple(p.ids)


def replay(directory:Path) -> dict:
    if directory.is_symlink():
        raise GateError("SYMLINK_CAPTURE_DIRECTORY")
    scratch=directory.resolve(strict=True)
    if (scratch == ROOT or ROOT in scratch.parents
            or ROOT.parent not in scratch.parents or not scratch.is_dir()):
        raise GateError("PRIVATE_CAPTURE_REQUIRED_OUTSIDE_GIT")
    raw_dir=scratch/"runs"
    raw=pinned(raw_dir/"siap_proposicions_page1_original.html",SHA_ORIGINAL,1_000_000)
    cr=json.loads(pinned(raw_dir/"siap_capture_receipt.json",SHA_CAPTURE_RECEIPT,10_000),
                  object_pairs_hook=pairs_unique)
    meta=json.loads(pinned(raw_dir/"siap_page1_metadata.json",SHA_METADATA,10_000),
                    object_pairs_hook=pairs_unique)
    freeze=json.loads(pinned(raw_dir/"siap_freeze.json",SHA_PRECAPTURE_FREEZE,10_000),
                      object_pairs_hook=pairs_unique)
    pinned(scratch/"parse_siap.py",SHA_PRECAPTURE_PARSER,30_000)
    if (freeze.get("A_J_scientific_preregistration") is not False
            or freeze.get("tests_passed") is not True
            or freeze.get("code_sha256",{}).get("parse_siap.py")!=SHA_PRECAPTURE_PARSER
            or cr.get("raw_sha256") != SHA_ORIGINAL
            or cr.get("raw_bytes") != len(raw)
            or cr.get("http_status")!=200
            or cr.get("source_url")!=EXPECTED_SOURCE
            or cr.get("terms_or_cookie_consent_clicked") is not False
            or cr.get("cookie_request_header_sent") is not False
            or cr.get("cookie_jar_enabled") is not False
            or cr.get("first_public_at") is not None):
        raise GateError("SOURCE_RIGHTS_OR_PROVENANCE_DRIFT")
    page,total,ids=parse_only_pagination_and_source_keys(raw)
    if (meta.get("schema")!="SIAP_PROPOSICIONS_METADATA_ONE_PAGE_V1"
            or meta.get("original_sha256")!=SHA_ORIGINAL
            or meta.get("original_bytes")!=len(raw)
            or meta.get("page_number")!=page
            or meta.get("advertised_pages_total")!=total
            or meta.get("unique_expediente_202_ids_on_this_page")!=len(ids)
            or meta.get("duplicate_id_links_on_page")!=0
            or meta.get("list_page_is_institution_wide_complete") is not False
            or meta.get("historical_source_vintage_attested") is not False
            or meta.get("statuses_or_outcomes_aggregated") is not False
            or meta.get("first_public_at") is not None):
        raise GateError("SOURCE_INDEX_METADATA_DRIFT")
    scope=FrameScope(
        institution="PARLAMENT_CATALUNYA", legislature="MIXED_UNADJUDICATED",
        family="PROPOSICIO_LLEI",
        risk_entry="SOURCE_REPORTED_REGISTRATION",
        selection_rule="UNKNOWN", registry_scope="PARTIAL_EDITORIAL_INDEX")
    record=PageEvidence(
        page=page,expected_pages=total,next_page=page+1,
        source_sha256=SHA_ORIGINAL,source_url=EXPECTED_SOURCE,
        captured_at=cr["finished_utc"],source_reported_total=None,scope=scope,
        cases=tuple(CaseRef(k,None) for k in ids),
        original_rights="GENERAL_NOTICE_UNRESOLVED")
    report=audit_pages([record]).report()
    if (report["distinct_case_keys"]!=20 or report["missing_pages"]!=list(range(2,45))
            or report["risk_population_denominator"] is not None):
        raise GateError("CENSUS_GATE_UNEXPECTEDLY_PROMOTED")
    # No actual identifiers, titles, institutions' personal names or status
    # terms are returned from the independent replay.
    return {
        "status":"INDEPENDENT_OFFLINE_REPLAY_METADATA_ONLY",
        "source_original_sha256":SHA_ORIGINAL,
        "source_capture_receipt_sha256":SHA_CAPTURE_RECEIPT,
        "source_parser_freeze_sha256":SHA_PRECAPTURE_FREEZE,
        "page_count":report["page_count"],"pages_advertised":report["expected_pages"],
        "pages_not_captured":len(report["missing_pages"]),
        "source_local_unique_ids_in_private_page":report["distinct_case_keys"],
        "cross_institutional_join_admitted":False,
        "full_entry_denominator":None,"outcomes_admitted":False,
        "first_public_at":None,"AB_cycles":0,
    }


if __name__=="__main__":
    p=argparse.ArgumentParser(description="One page SIAP, offline metadata-only replay")
    p.add_argument("--scratch",type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(replay(args.scratch),sort_keys=True,ensure_ascii=False))
