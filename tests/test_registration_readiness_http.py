"""Local read-only HTTP integration; retrospective source existence is private."""
import http.client
from http.server import ThreadingHTTPServer
import json
from threading import Thread

import pytest

from politics_fantasy.server import handler_factory


@pytest.fixture
def local(tmp_path):
    s=ThreadingHTTPServer(("127.0.0.1",0),handler_factory(tmp_path/"db.sqlite",None,None))
    thread=Thread(target=s.serve_forever,daemon=True)
    thread.start()
    try:
        yield s.server_port
    finally:
        s.shutdown()
        s.server_close()
        thread.join(timeout=3)


def fetch(port,query,host=None):
    c=http.client.HTTPConnection("127.0.0.1",port,timeout=4)
    c.request("GET","/api/registration-readiness"+query,
              headers={"Host":host} if host else {})
    r=c.getresponse()
    result=r.status,json.loads(r.read()),dict(r.getheaders())
    c.close()
    return result


def test_future_and_unknown_indistinguishable_http(local):
    a=fetch(local,"?source_id=ARAGON_GENERAL_ACCESS_STATISTICS&as_of=2026-10-31T12%3A00%3A00Z")
    b=fetch(local,"?source_id=ANY_UNSEEN_SOURCE&as_of=2026-10-31T12%3A00%3A00Z")
    assert a[:2]==b[:2]
    assert a[0]==200 and a[1]["source"] is None
    assert "ARAGON" not in json.dumps(a[1])
    assert a[2]["Cache-Control"]=="no-store"


def test_http_provenance_temporal_rights_states_and_unknowns(local):
    a=fetch(local,"?source_id=GENCAT_SAIP_INITIAL_FILINGS&as_of=2026-11-01T00%3A00%3A00Z")
    assert a[0]==200
    doc=a[1]
    assert doc["status"]=="SOURCE_VISIBLE_WITHOUT_CERTIFIED_REGISTRATION_POPULATION"
    assert doc["clocks"]["first_public_at"] is None
    assert doc["population"]["independent_all_received_denominator"] is None
    assert doc["rights"]["real_original_ingestion_authorized"] is False
    assert doc["states"]["pending_known"] is None
    assert doc["official_links"]["confirmed_dual_id_edges"] is None
    assert "person_name" not in json.dumps(doc).lower()


@pytest.mark.parametrize("query",[
    "", "?source_id=", "?as_of=2026-11-01T00:00:00Z",
    "?source_id=GENCAT_SAIP_INITIAL_FILINGS&case_id=PRIVATE",
    "?source_id=GENCAT_SAIP_INITIAL_FILINGS&source_id=ARAGON_GENERAL_ACCESS_STATISTICS",
    "?source_id=GENCAT_SAIP_INITIAL_FILINGS&as_of=2026-10-31",
    "?source_id=%3Cscript%3E",
    "?source_id=GENCAT_SAIP_INITIAL_FILINGS&as_of=bad",
])
def test_queries_cannot_access_cases_or_bypass_cut(local,query):
    assert fetch(local,query)[0]==400


def test_http_wrong_host_rejected(local):
    assert fetch(local,"?source_id=GENCAT_SAIP_INITIAL_FILINGS",
                 host="evil.example")[0]==403


def test_r16_sources_hidden_pre_cut_and_visible_only_as_uncertified_documentary(local):
    before="&as_of=2026-10-31T23%3A59%3A59Z"
    unknown=fetch(local,"?source_id=DOES_NOT_EXIST"+before)
    r16=fetch(local,"?source_id=SINDIC_CV_COMPLAINT_REGISTRATION"+before)
    assert r16[:2]==unknown[:2]
    assert r16[0]==200
    assert "SINDIC" not in json.dumps(r16[1])
    after="&as_of=2026-11-01T00%3A00%3A00Z"
    code,sind,_=fetch(local,"?source_id=SINDIC_CV_COMPLAINT_REGISTRATION"+after)
    assert code==200
    assert sind["source"]["source_id"]=="SINDIC_CV_COMPLAINT_REGISTRATION"
    assert sind["population"]["independent_all_received_denominator"] is None
    assert "RECEIPT_3_VS_5_DAYS" in sind["clocks"]["r16_procedural_editorial_conflict"]
    assert sind["clocks"]["first_public_at"] is None
    assert not sind["rights"]["real_original_ingestion_authorized"]
    code,ct,_=fetch(local,
        "?source_id=CTPDA_ANDALUCIA_SELECTED_REVIEW_RESOLUTIONS"+after)
    assert code==200
    assert set(ct["rights"]["by_distribution"])=={"CSV","ODS","XLS","XML"}
    assert all("NOT_EXACT_CASE" in label for label in
               ct["rights"]["by_distribution"].values())
    assert ct["states"]["terminal_known"] is None
    assert ct["states"]["right_censored_known"] is None
