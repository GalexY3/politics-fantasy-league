"""S9 synthetic durable SQLite registry; no external sources or person data.

S9 is a NEW engineering capability, not a claimed PREPATCH production defect.
The only input is the closed fixture replay and a dedicated local SQLite path.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import http.client
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from threading import Thread
from urllib.parse import urlencode

import pytest

from politics_fantasy import scientific_registry as registry
from politics_fantasy.server import handler_factory


@pytest.fixture
def db(tmp_path:Path):
    return tmp_path/"scientific_registry_synthetic.sqlite3"


@pytest.fixture
def local_registry_http(tmp_path:Path):
    game_db=tmp_path/"game-demo.sqlite3"
    server=ThreadingHTTPServer(("127.0.0.1",0),handler_factory(game_db,None,None))
    thread=Thread(target=server.serve_forever,daemon=True)
    thread.start()

    def get(route:str,method:str="GET"):
        conn=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=12)
        conn.request(method,route)
        response=conn.getresponse()
        status=response.status
        cache=response.getheader("Cache-Control")
        payload=json.loads(response.read())
        conn.close()
        return status,cache,payload
    try:
        yield get,registry.registry_path(game_db)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _assert_gate(payload:dict):
    assert payload["schema"]=="pfl.synthetic_scientific_registry.v1"
    assert payload["evidence_class"]=="SYNTHETIC_LAB_ONLY"
    assert payload["R5"]=="STOP_R5"
    assert payload["independent_denominator"] is None
    assert payload["real_source_ingestion_allowed"] is False
    assert payload["scientific_ab_cycles"]==0
    assert payload["release_gates_passed"]==0
    assert payload["models"]=={
        "s3_s7_endpoint":"/api/scientific-integration-lab",
        "computed_from_registry":False,
        "separate_existing_python_node_oracle":True,
        "empirical_model_admitted":False,
    }
    assert payload["registry"]["schema_version"]==4
    assert payload["registry"]["migration_history"]==[1,2,3,4]
    assert payload["registry"]["source_bytes_exposed"] is False
    assert payload["registry"]["private_source_ids_exposed"] is False
    assert payload["registry"]["originals_accepted"] is False
    assert payload["registry"]["fixture_bytes_sha256_checked_at_read"] is True
    assert payload["snapshot"]["graph"]["cross_issuer_links_created"] is False
    assert payload["snapshot"]["episodes"]["source_local_all_received_denominator"] is None
    assert payload["snapshot"]["episodes"]["right_censor_independently_attested"] is False
    assert payload["snapshot"]["pp04"]["unplanned_is_a_terminal_negative"] is False
    assert payload["snapshot"]["pp04"]["independent_crosswalk_between_pan_iaen"] is False
    intake=payload["snapshot"]["synthetic_intake"]
    assert intake["schema"]=="pfl.synthetic_intake_overlay.v1"
    assert intake["intake_count"] in (0,1,2,3,4)
    assert intake["history_event_count"]==intake["intake_count"]*2
    assert intake["validated_count"]+intake["rejected_count"]==intake["intake_count"]
    assert intake["source_rows_added_to_canonical"]==0
    assert intake["independent_denominator"] is None
    assert intake["real_source_ingestion_allowed"] is False
    assert intake["rights_for_public_display"] is False
    assert intake["scientific_admission_allowed"] is False
    assert intake["source_local_identifiers_exposed"] is False
    assert intake["real_enrollment_at"] is None
    assert intake["logical_decisions_count"]==0
    assert intake["graph"]["cross_issuer_links_created"] is False
    assessments=payload["snapshot"]["admission_assessments"]
    assert assessments["schema"]=="pfl.synthetic_admission_assessments.v1"
    assert assessments["assessment_temporal_axis"]=="AS_OF_NOT_FACT_VALID_AT"
    assert assessments["assessment_count"] in (0,8)
    assert assessments["registered_count"]==assessments["assessment_count"]
    assert assessments["assessed_rejected_r5_count"]==assessments["assessment_count"]
    assert assessments["history_event_count"]==assessments["assessment_count"]*2
    assert assessments["source_rows_ingested"]==0
    assert assessments["real_admission_allowed"] is False
    assert assessments["independent_denominator"] is None
    assert assessments["source_local_identifiers_exposed"] is False
    for entry in assessments["assessments"]:
        assert entry["status"]=="ASSESSED_REJECTED_R5"
        assert entry["source_rows_imported"]==0
        assert entry["rights_for_public_display"] is False
        assert entry["real_original_admitted"] is False
        assert entry["real_first_public_at"] is None
        verified={k:v for k,v in entry.items() if k!="public_receipt_sha256"}
        assert hashlib.sha256(registry._json(verified).encode()).hexdigest()==entry["public_receipt_sha256"]
    receipt=payload["snapshot_receipt"]
    assert receipt["schema"]=="pfl.synthetic_registry_snapshot_receipt.v1"
    assert receipt["content_scope"]=="CLOSED_PUBLIC_SYNTHETIC_QUERY_ONLY"
    assert receipt["external_authenticity_certified"] is False
    assert hashlib.sha256(receipt["canonical_json"].encode()).hexdigest()==receipt["sha256"]
    assert len(receipt["canonical_json"].encode())==receipt["bytes"]
    assert payload["snapshot_receipt_sha256"]==receipt["sha256"]
    scoped=json.loads(receipt["canonical_json"])
    assert scoped["snapshot"]==payload["snapshot"]
    assert scoped["distributions"]==payload["registry"]["distributions"]
    assert scoped["as_of"]==payload["as_of"]
    raw=json.dumps(payload,ensure_ascii=False)
    for internal in ("SYN:CHRONICLE", "SYN:CHAIN", "SYN:S9_INTERNAL_STAGE",
                     "SYNTHETIC:IAEN24", "SYNTHETIC:PAN24",
                     "SYNTHETIC_STAGE_DOCUMENT", "SYNTHETIC TYPED CHAIN",
                     "SYN:S8_NEW_DISTRIBUTION", "SYN:S8_LOCAL_TEST",
                     "REAL:UNVERIFIED", "SYNTHETIC S8 ADMISSION FIXTURE",
                     "AUTHOR_ALPHA:FILE_1", "AUTHOR_BETA:FILE_1",
                     "SYN:S9_AUTHOR_ALPHA", "SYN:S9_AUTHOR_BETA",
                     "REAL:UNVERIFIED_FIXTURE", "SYNTHETIC S9 AUTHOR-CLOSED INTAKE"):
        assert internal not in raw,internal


def test_s9_atomic_seed_restart_exact_bytes_and_versioned_schema(db):
    assert not db.exists()
    registry.seed_registry(db)
    assert db.exists() and db.stat().st_size>100
    first=registry.query_registry(db,cut="late")
    assert first["registry"]["visible_distribution_count"]==6
    assert first["registry"]["recorded_distribution_count"]==6
    assert first["registry"]["internal_uncatalogued_fixture_receipts"]==1
    with sqlite3.connect(db) as con:
        assert con.execute("PRAGMA user_version").fetchone()[0]==4
        recorded=con.execute("SELECT source_id,source_bytes,source_sha256 FROM distribution ORDER BY 1").fetchall()
        assert len(recorded)==7
        for source_id,bytes_,sha in recorded:
            assert isinstance(bytes_,bytes)
            assert hashlib.sha256(bytes_).hexdigest()==sha
        assert {r[0] for r in con.execute("SELECT DISTINCT issuer FROM typed_fact")}=={
            "SYN:CHAIN","SYN:CHRONICLE","SYN:PP04_PARSER","SYN:S9_LOCAL_STAGE"}
        assert con.execute("SELECT COUNT(*) FROM typed_fact").fetchone()[0]==20
        assert con.execute("SELECT COUNT(*) FROM typed_edge").fetchone()[0]==6
        assert con.execute("SELECT COUNT(*) FROM assessment_event").fetchone()[0]==16
    registry.seed_registry(db)
    second=registry.query_registry(db,cut="late")
    assert second==first
    _assert_gate(first)


def test_s9_bootstrap_concurrent_queries_replay_once_and_consistent(db):
    def load(_):
        return registry.query_registry(db,cut="early")["registry"]["distributions"]
    with ThreadPoolExecutor(max_workers=8) as executor:
        outcomes=list(executor.map(load,range(16)))
    assert outcomes and all(x==outcomes[0] for x in outcomes)
    assert len(outcomes[0])==2
    with sqlite3.connect(db) as con:
        assert con.execute("SELECT COUNT(*) FROM registry_meta").fetchone()[0]==1
        assert con.execute("SELECT COUNT(*) FROM distribution").fetchone()[0]==7


def test_s9_two_independent_python_processes_restart_same_real_sqlite_bytes(db):
    script=Path(__file__).resolve().parents[1]/"src"
    env={**os.environ,"PYTHONPATH":str(script)}

    def external_read():
        proc=subprocess.run([sys.executable,"-m","politics_fantasy.scientific_registry",
                             "--db",str(db)],cwd=script.parent,env=env,
                            text=True,capture_output=True,timeout=12)
        assert proc.returncode==0,proc.stderr
        return json.loads(proc.stdout)

    first=external_read()
    assert db.exists()
    with sqlite3.connect(db) as con:
        before_rows=con.execute("SELECT source_id,source_bytes,source_sha256 FROM distribution ORDER BY 1").fetchall()
        assert con.execute("PRAGMA user_version").fetchone()[0]==4
    second=external_read()
    assert second==first
    assert second["registry"]["persistent"] is True
    assert second["snapshot_receipt_sha256"]==first["snapshot_receipt_sha256"]
    with sqlite3.connect(db) as con:
        assert con.execute("SELECT source_id,source_bytes,source_sha256 FROM distribution ORDER BY 1").fetchall()==before_rows
        assert con.execute("SELECT COUNT(*) FROM registry_meta").fetchone()[0]==1
    _assert_gate(second)


def test_s9_1_v3_eight_dry_run_assessments_are_immutable_separate_records(db):
    from politics_fantasy.scientific_integration_lab import synthetic_candidate_admission

    late=registry.query_registry(db,cut="late")
    panel=late["snapshot"]["admission_assessments"]
    assert panel["assessment_count"]==8
    assert panel["registered_count"]==8
    assert panel["assessed_rejected_r5_count"]==8
    assert panel["history_event_count"]==16
    assert len({row["assessment_id"] for row in panel["assessments"]})==8
    assert {row["candidate"] for row in panel["assessments"]}==set(registry._ASSESSMENT_VARIANTS)
    for row in panel["assessments"]:
        assert row["status"]=="ASSESSED_REJECTED_R5"
        assert row["captured_at_fixture"]=="2026-10-31T12:00:00Z"
        assert row["history"]==[
            {"status":"REGISTERED","recorded_at":"2026-10-31T12:15:00Z"},
            {"status":"ASSESSED_REJECTED_R5","recorded_at":"2026-10-31T13:00:00Z"},
        ]
        raw=synthetic_candidate_admission(candidate=row["candidate"])
        assert row["checks"]==raw["checks"]
        assert row["blockers"]==raw["blockers"]
        assert row["source_rows_imported"]==raw["source_rows_imported"]==0
    with sqlite3.connect(db) as con:
        assert con.execute("PRAGMA user_version").fetchone()[0]==4
        assert con.execute("SELECT COUNT(*) FROM distribution").fetchone()[0]==7
        assert con.execute("SELECT COUNT(*) FROM typed_fact").fetchone()[0]==20
        assert con.execute("SELECT COUNT(*) FROM typed_edge").fetchone()[0]==6
        assert con.execute("SELECT COUNT(*) FROM assessment_event").fetchone()[0]==16
        rows=con.execute("SELECT assessment_id,event_sequence,status,receipt_bytes,receipt_sha256 "
                         "FROM assessment_event ORDER BY event_id").fetchall()
        assert len({r[0] for r in rows})==8
        for _,sequence,status,body,digest in rows:
            assert sequence==1 if status=="REGISTERED" else sequence==2
            assert hashlib.sha256(body).hexdigest()==digest
            assert json.loads(body)["status"]==status
        private_sources={r[0] for r in con.execute(
            "SELECT DISTINCT fixture_source_id FROM assessment_event")}
        assert private_sources=={"SYN:S8_NEW_DISTRIBUTION"}
        assert not con.execute("SELECT 1 FROM distribution WHERE source_id='SYN:S8_NEW_DISTRIBUTION'").fetchone()
    _assert_gate(late)


def test_s9_1_assessments_do_not_leak_across_knowledge_or_publication_cut(db):
    early=registry.query_registry(db,cut="early")
    late=registry.query_registry(db,cut="late")
    prior=registry.query_registry(db,cut="late",published_until="2026-10-30T12:00:00Z")
    chain=registry.query_registry(db,cut="late",family="CHAIN")
    other_valid=registry.query_registry(db,cut="late",valid_at="2026-09-11")
    a=lambda r:r["snapshot"]["admission_assessments"]
    assert (a(early)["assessment_count"],a(prior)["assessment_count"],
            a(chain)["assessment_count"],a(late)["assessment_count"])==(0,0,0,8)
    assert a(other_valid)==a(late)  # audit clock != event's valid_at
    for item in (early,late,prior,chain):
        assert item["snapshot"]["admission_assessments"]==json.loads(
            item["snapshot_receipt"]["canonical_json"])["snapshot"]["admission_assessments"]
        _assert_gate(item)
    assert late["snapshot_receipt_sha256"]!=early["snapshot_receipt_sha256"]
    assert prior["snapshot_receipt_sha256"]!=late["snapshot_receipt_sha256"]


def test_s9_1_v2_to_v3_migration_preserves_all_previous_bytes_and_typed_rows(db):
    # Construct a real previous-version S9 fixture; NO fake reset/reseed.
    with registry._connect(db) as con:
        con.execute("BEGIN IMMEDIATE")
        registry._migration_v1(con)
        registry._migration_v2(con)
        con.execute("INSERT INTO registry_meta VALUES(1,?,?,?,?)",(
            registry.FIXTURE_ID,registry._manifest_hash(),
            "2026-11-01T12:00:00Z","STOP_R5"))
        registry._insert_rows(con,"distribution",registry.SOURCES_COLUMNS,
                              registry._closed_sources())
        registry._insert_rows(con,"typed_fact",registry.FACT_COLUMNS,
                              registry._closed_facts())
        registry._insert_rows(con,"typed_edge",registry.EDGE_COLUMNS,
                              registry._closed_edges())
        assert con.execute("PRAGMA user_version").fetchone()[0]==2
        original={table:[tuple(row) for row in con.execute(f"SELECT * FROM {table} ORDER BY 1")]
                  for table in ("distribution","typed_fact","typed_edge")}
        con.commit()
    registry.seed_registry(db)
    with sqlite3.connect(db) as con:
        assert con.execute("PRAGMA user_version").fetchone()[0]==4
        assert con.execute("SELECT COUNT(*) FROM assessment_event").fetchone()[0]==16
        assert [r[0] for r in con.execute("SELECT version FROM schema_history ORDER BY version")]==[1,2,3,4]
        for table,rows in original.items():
            assert list(con.execute(f"SELECT * FROM {table} ORDER BY 1"))==rows
    assert registry.query_registry(db)["snapshot"]["admission_assessments"]["assessment_count"]==8


def test_s9_1_two_process_restart_assessments_retained_and_sha_stable(db):
    root=Path(__file__).resolve().parents[1]/"src"
    env={**os.environ,"PYTHONPATH":str(root)}
    def replay():
        proc=subprocess.run([sys.executable,"-m","politics_fantasy.scientific_registry",
                             "--db",str(db)],cwd=root.parent,env=env,
                            capture_output=True,text=True,timeout=12)
        assert proc.returncode==0,proc.stderr
        return json.loads(proc.stdout)
    first=replay()
    with sqlite3.connect(db) as con:
        before=con.execute("SELECT event_id,receipt_bytes,receipt_sha256 FROM assessment_event ORDER BY event_id").fetchall()
    second=replay()
    with sqlite3.connect(db) as con:
        after=con.execute("SELECT event_id,receipt_bytes,receipt_sha256 FROM assessment_event ORDER BY event_id").fetchall()
    assert before==after and len(before)==16
    assert first==second
    assert first["snapshot_receipt_sha256"]==second["snapshot_receipt_sha256"]


@pytest.mark.parametrize("field,value",[
    ("receipt_bytes",b"SYNTHETIC ALTERED ASSESSMENT"),
    ("receipt_sha256","0"*64),
    ("fixture_source_id","REAL:PERSON"),
    ("fixture_issuer_claim","REAL:INSTITUTION"),
    ("recorded_at","2026-11-02T13:00:00Z"),
    ("first_public_known_at","2026-09-19T12:00:00Z"),
    ("captured_at","2026-10-30T11:00:00Z"),
    ("candidate","baseline"),
])
def test_s9_1_tampered_assessment_event_even_with_trigger_bypass_is_503(db,field,value):
    registry.seed_registry(db)
    with sqlite3.connect(db) as con:
        trigger="registry_assessment_immutable_update"
        old=con.execute("SELECT sql FROM sqlite_master WHERE name=?",(trigger,)).fetchone()[0]
        con.execute(f"DROP TRIGGER {trigger}")
        con.execute(f"UPDATE assessment_event SET {field}=? WHERE event_id='S9:AUDIT_02_2'",
                    (value,))
        con.execute(old)
        con.commit()
    with pytest.raises(registry.RegistryIntegrityError):
        registry.query_registry(db)


def test_s9_1_assessment_event_immutability_and_rights_check_constraint(db):
    registry.seed_registry(db)
    with sqlite3.connect(db) as con:
        for sql in (
            "UPDATE assessment_event SET status='REGISTERED' WHERE event_id='S9:AUDIT_02_2'",
            "DELETE FROM assessment_event WHERE event_id='S9:AUDIT_02_2'",
        ):
            with pytest.raises(sqlite3.DatabaseError,match="IMMUTABLE_ASSESSMENT_EVENT"):
                con.execute(sql)
        update=con.execute("SELECT sql FROM sqlite_master WHERE name='registry_assessment_immutable_update'").fetchone()[0]
        con.execute("DROP TRIGGER registry_assessment_immutable_update")
        for sql in (
            "UPDATE assessment_event SET rights_for_public_display=1",
            "UPDATE assessment_event SET real_issuer_authenticated=1",
            "UPDATE assessment_event SET source_rows_imported=1",
            "UPDATE assessment_event SET real_first_public_at='2026-10-30T12:00:00Z'",
            "UPDATE assessment_event SET independent_denominator=2",
        ):
            with pytest.raises(sqlite3.IntegrityError):
                con.execute(sql)
        con.execute(update)
        con.commit()
    _assert_gate(registry.query_registry(db))


def test_s9_1_http_v3_200_400_503_and_no_internal_source_leak(local_registry_http):
    get,path=local_registry_http
    status,cache,late=get("/api/scientific-registry?cut=late")
    assert status==200 and cache=="no-store"
    _assert_gate(late)
    assert len(late["snapshot"]["admission_assessments"]["assessments"])==8
    status,_,early=get("/api/scientific-registry?cut=early")
    assert status==200 and early["snapshot"]["admission_assessments"]["assessment_count"]==0
    status,_,invalid=get("/api/scientific-registry?assessment_id=S9%3AASSESS_01")
    assert status==400 and invalid=={"error":"INVALID_SYNTHETIC_REGISTRY_QUERY"}
    with sqlite3.connect(path) as con:
        trigger="registry_assessment_immutable_update"
        statement=con.execute("SELECT sql FROM sqlite_master WHERE name=?",(trigger,)).fetchone()[0]
        con.execute(f"DROP TRIGGER {trigger}")
        con.execute("UPDATE assessment_event SET receipt_sha256=? WHERE event_id='S9:AUDIT_02_2'",
                    ("0"*64,))
        con.execute(statement)
        con.commit()
    status,cache,failed=get("/api/scientific-registry?cut=late")
    assert (status,cache,failed)==(503,"no-store",{"error":"SYNTHETIC_REGISTRY_UNAVAILABLE"})


def test_s9_v1_to_v4_transactional_migration_preserves_existing_source_bytes(db):
    with registry._connect(db) as con:
        con.execute("BEGIN IMMEDIATE")
        registry._migration_v1(con)
        con.execute("INSERT INTO registry_meta VALUES(1,?,?,?,?)",(
            registry.FIXTURE_ID,registry._manifest_hash(),
            "2026-11-01T12:00:00Z","STOP_R5"))
        registry._insert_rows(con,"distribution",registry.SOURCES_COLUMNS,
                              registry._closed_sources())
        assert con.execute("PRAGMA user_version").fetchone()[0]==1
        pre_sha=hashlib.sha256(b"".join(row[0] for row in
            con.execute("SELECT source_bytes FROM distribution ORDER BY 1"))).hexdigest()
        con.commit()
    registry.seed_registry(db)
    with sqlite3.connect(db) as con:
        assert con.execute("PRAGMA user_version").fetchone()[0]==4
        post_sha=hashlib.sha256(b"".join(row[0] for row in
            con.execute("SELECT source_bytes FROM distribution ORDER BY 1"))).hexdigest()
        assert pre_sha==post_sha
        assert con.execute("SELECT count(*) FROM schema_history").fetchone()[0]==4
        assert con.execute("SELECT count(*) FROM assessment_event").fetchone()[0]==16
    assert registry.query_registry(db)["R5"]=="STOP_R5"


def test_s9_failed_v1_migration_rolls_back_whole_transaction(db):
    with registry._connect(db) as con:
        con.execute("BEGIN IMMEDIATE")
        registry._migration_v1(con)
        con.execute("INSERT INTO registry_meta VALUES(1,?,?,?,?)",(
            registry.FIXTURE_ID,registry._manifest_hash(),
            "2026-11-01T12:00:00Z","STOP_R5"))
        source=registry._closed_sources()[0].copy()
        source["issuer"]="REAL:FAKE"
        registry._insert_rows(con,"distribution",registry.SOURCES_COLUMNS,[source])
        con.commit()
    with pytest.raises(registry.RegistryIntegrityError,match="REGISTRY_V1_MIGRATION_SOURCE_MISMATCH"):
        registry.seed_registry(db)
    with sqlite3.connect(db) as con:
        assert con.execute("PRAGMA user_version").fetchone()[0]==1
        assert not con.execute("SELECT name FROM sqlite_master WHERE name='typed_fact'").fetchone()
        assert con.execute("SELECT COUNT(*) FROM distribution").fetchone()[0]==1


def test_s9_fixed_bitemporal_role_revision_and_explicit_stage_semantics(db):
    early_11=registry.query_registry(db,cut="early",valid_at="2026-09-11")
    early_15=registry.query_registry(db,cut="early",valid_at="2026-09-15")
    late_15=registry.query_registry(db,cut="late",valid_at="2026-09-15")
    early_oct=registry.query_registry(db,cut="early",valid_at="2026-10-10")
    late_oct=registry.query_registry(db,cut="late",valid_at="2026-10-10")
    for item in (early_11,early_15,late_15,early_oct,late_oct):
        _assert_gate(item)
    assert early_11["snapshot"]["episodes"]["chain_process_state"]=="UNKNOWN_FOLLOWUP_NOT_NEGATIVE"
    assert early_15["snapshot"]["episodes"]["chain_process_state"]=="PENDING_NOT_NEGATIVE"
    assert late_15["snapshot"]["episodes"]["chain_process_state"]=="APPROVED_AS_OF_SYNTHETIC_EVIDENCE"
    assert early_15["snapshot"]["episodes"]["explicit_negative_documented"]==0
    assert late_15["snapshot"]["episodes"]["explicit_negative_documented"]==1
    assert late_15["snapshot"]["episodes"]["pending_documented_not_negative"]==1
    assert early_15["snapshot"]["pp04"]["not_included_source_local_not_negative"]==0
    assert late_15["snapshot"]["pp04"]["not_included_source_local_not_negative"]==2
    early_nodes=early_oct["snapshot"]["graph"]["chronicle"]["nodes"]
    late_nodes=late_oct["snapshot"]["graph"]["chronicle"]["nodes"]
    assert not any(n["kind"]=="ROLE" for n in early_nodes)
    assert sum(n["kind"]=="ROLE" for n in late_nodes)==1
    events=[n for n in late_nodes if n["kind"]=="EVENT"]
    assert len(events)==1
    assert events[0]["documentary_revision_count"]==2
    chain=[n for n in late_15["snapshot"]["graph"]["chain"]["nodes"]
           if n["kind"]=="COMMUNICATION"]
    assert len(chain)==1 and chain[0]["documentary_revision_count"]==2


def test_s9_closed_family_query_and_publication_filter_no_lookahead(db):
    late=registry.query_registry(db,cut="late")
    prior=registry.query_registry(db,cut="late",published_until="2026-09-19T12:00:00Z")
    ch=registry.query_registry(db,cut="late",family="CHRONICLE")
    pp=registry.query_registry(db,cut="late",family="PP04")
    early=registry.query_registry(db,cut="early",family="PP04")
    assert len(late["registry"]["distributions"])==6
    assert len(prior["registry"]["distributions"])==2
    assert len(ch["registry"]["distributions"])==2
    assert len(pp["registry"]["distributions"])==2
    assert len(early["registry"]["distributions"])==0
    assert late["snapshot_receipt_sha256"]!=prior["snapshot_receipt_sha256"]
    assert prior["snapshot_receipt_sha256"]!=early["snapshot_receipt_sha256"]
    assert not prior["snapshot"]["graph"]["chain"]["nodes"][-1].get("first_public_at_real")
    assert prior["snapshot"]["episodes"]["explicit_negative_documented"]==0
    assert prior["snapshot"]["pp04"]["not_included_source_local_not_negative"]==0
    assert early["snapshot"]["graph"]["chain"] is None
    with pytest.raises(ValueError,match="CEILING_AFTER_AS_OF"):
        registry.query_registry(db,cut="early",published_until="2026-10-30T12:00:00Z")
    for bad in ({"cut":"today"},{"valid_at":"2030-01-01"},
                {"family":"SYN:CHAIN_V1"},{"published_until":"now"}):
        with pytest.raises(ValueError):
            registry.query_registry(db,**bad)


def test_s9_db_triggers_block_updates_and_deletes_even_in_direct_sql(db):
    registry.seed_registry(db)
    with sqlite3.connect(db) as con:
        for sql in (
                "UPDATE distribution SET issuer='REAL:FAKE' WHERE public_id='S9:PUBLIC_01'",
                "UPDATE distribution SET source_sha256='0' WHERE public_id='S9:PUBLIC_01'",
                "DELETE FROM distribution WHERE public_id='S9:PUBLIC_05'",
                "UPDATE typed_fact SET source_local_key='SPOOF' WHERE fact_id='S9:C:ACTOR'",
                "DELETE FROM typed_edge WHERE edge_id='S9:E:C:ACTOR_ORG'"):
            with pytest.raises(sqlite3.DatabaseError,match="IMMUTABLE"):
                con.execute(sql)
    _assert_gate(registry.query_registry(db))


@pytest.mark.parametrize("table,trigger,id_column,id_value,column,value",[
    ("distribution","registry_distribution_immutable_update","public_id","S9:PUBLIC_03","source_bytes",b"SYNTHETIC ALTERED\n"),
    ("distribution","registry_distribution_immutable_update","public_id","S9:PUBLIC_03","source_sha256","0"*64),
    ("distribution","registry_distribution_immutable_update","public_id","S9:PUBLIC_03","issuer","REAL:UNATTESTED"),
    ("distribution","registry_distribution_immutable_update","public_id","S9:PUBLIC_03","first_public_known_at","2026-11-10T12:00:00Z"),
    ("distribution","registry_distribution_immutable_update","public_id","S9:PUBLIC_03","revision",3),
    ("distribution","registry_distribution_immutable_update","public_id","S9:PUBLIC_04","amendment_of","SYN:CHRONICLE_V1"),
    ("distribution","registry_distribution_immutable_update","public_id","S9:PUBLIC_04","quality_gate","FALSIFIED_CERTIFIED"),
    ("typed_fact","registry_fact_immutable_update","fact_id","S9:C:COMM_V2","source_local_key","IMPOSSIBLE_CROSSWALK"),
    ("typed_fact","registry_fact_immutable_update","fact_id","S9:C:COMM_V2","amendment_of","S9:H:ROLE_V1"),
    ("typed_edge","registry_edge_immutable_update","edge_id","S9:E:C:ACTOR_ORG","to_local","UNREGISTERED")
])
def test_s9_tamper_even_if_immutable_trigger_removed_never_passes_audit(
        db,table,trigger,id_column,id_value,column,value):
    registry.seed_registry(db)
    with sqlite3.connect(db) as con:
        original=con.execute("SELECT sql FROM sqlite_master WHERE name=?",(trigger,)).fetchone()[0]
        con.execute(f"DROP TRIGGER {trigger}")
        con.execute(f"UPDATE {table} SET {column}=? WHERE {id_column}=?",(value,id_value))
        con.execute(original)
        con.commit()
    with pytest.raises(registry.RegistryIntegrityError):
        registry.query_registry(db)


def test_s9_missing_immutability_trigger_detected_fail_closed(db):
    registry.seed_registry(db)
    with sqlite3.connect(db) as con:
        con.execute("DROP TRIGGER registry_distribution_immutable_update")
        con.commit()
    with pytest.raises(registry.RegistryIntegrityError,match="SCHEMA_DDL_HASH_DIVERGENCE"):
        registry.query_registry(db)


def test_s9_same_name_but_neutered_immutability_trigger_detected(db):
    registry.seed_registry(db)
    with sqlite3.connect(db) as con:
        con.execute("DROP TRIGGER registry_distribution_immutable_update")
        con.execute("""CREATE TRIGGER registry_distribution_immutable_update
            BEFORE UPDATE ON distribution BEGIN SELECT 1; END""")
        con.commit()
    with pytest.raises(registry.RegistryIntegrityError,match="SCHEMA_DDL_HASH_DIVERGENCE"):
        registry.query_registry(db)


def test_s9_unchanged_schema_version_but_weakened_table_ddl_fails_closed(db):
    registry.seed_registry(db)
    with sqlite3.connect(db) as con:
        con.execute("ALTER TABLE distribution ADD COLUMN unapproved_payload BLOB")
        assert con.execute("PRAGMA user_version").fetchone()[0]==4
        con.commit()
    with pytest.raises(registry.RegistryIntegrityError,match="SCHEMA_DDL_HASH_DIVERGENCE"):
        registry.query_registry(db)


def test_s9_db_does_not_permit_promoting_real_rights_or_publisher_attestation(db):
    registry.seed_registry(db)
    with sqlite3.connect(db) as con:
        trigger="registry_distribution_immutable_update"
        sql=con.execute("SELECT sql FROM sqlite_master WHERE name=?",(trigger,)).fetchone()[0]
        con.execute(f"DROP TRIGGER {trigger}")
        for query in (
            "UPDATE distribution SET rights_for_purpose_admitted=1",
            "UPDATE distribution SET issuer_authenticated_real=1",
            "UPDATE distribution SET first_public_at_real='2026-01-01T00:00:00Z'",
            "UPDATE distribution SET independent_denominator=99999",
        ):
            with pytest.raises(sqlite3.IntegrityError):
                con.execute(query)
        con.execute(sql)
        con.commit()
    _assert_gate(registry.query_registry(db))


def test_s9_http_loopback_restart_export_and_existing_python_node_s7(local_registry_http):
    get,path=local_registry_http
    status,cache,late=get("/api/scientific-registry?cut=late&valid_at=2026-09-15")
    assert (status,cache)==(200,"no-store")
    _assert_gate(late)
    assert path.is_file()
    status,_,early=get("/api/scientific-registry?cut=early&valid_at=2026-09-15")
    assert status==200 and early["registry"]["visible_distribution_count"]==2
    status,_,filtered=get("/api/scientific-registry?cut=late&published_until=2026-09-19T12%3A00%3A00Z")
    assert status==200 and filtered["registry"]["visible_distribution_count"]==2
    status,_,again=get("/api/scientific-registry?cut=late&valid_at=2026-09-15")
    assert status==200 and again==late
    status,_,oracle=get("/api/scientific-integration-lab?cut=late")
    assert status==200 and oracle["R5"]=="STOP_R5"
    assert len(oracle["warehouse"]["b0_b3_witness_sets"]["sets_by_knowledge_cut"]["late"]["sets"])==20
    assert oracle["warehouse"]["partial_identification_oracle"]["change_bounds"]["lower"]=="-11/52"


@pytest.mark.parametrize("cut",["early","late"])
def test_s9_persisted_bitemporal_graph_cross_contract_vs_actual_python_node_oracles(db,cut):
    """Do not allow new SQLite graph to drift from independently replayed S8."""
    from politics_fantasy.scientific_integration_lab import report
    oracle=report(cut=cut)
    assert oracle["R5"]=="STOP_R5"
    assert oracle["warehouse"]["typed_institutional_chain"]["schema"]==(
        "pfl.synthetic_typed_institutional_chain_oracle.v1")
    assert oracle["warehouse"]["bitemporal_actor_event_equivalence"]["schema"]==(
        "pfl.synthetic_bitemporal_actor_event_oracle.v1")
    for valid in ("2026-09-11","2026-09-15"):
        persisted=registry.query_registry(db,cut=cut,valid_at=valid)
        chain=persisted["snapshot"]["graph"]["chain"]["nodes"]
        expected=oracle["warehouse"]["typed_institutional_chain"]["views_by_valid_day"][valid]
        for kind,field in (("ACTOR","actor_visible"),("ORGANIZATION","organization_visible"),
                           ("COMMUNICATION","logical_communications"),
                           ("DECISION","logical_decisions"),("PROCESS","process_episode_visible")):
            assert sum(x["kind"]==kind for x in chain)==expected[field]
        revisions=next(x["documentary_revision_count"] for x in chain
                       if x["kind"]=="COMMUNICATION")
        assert revisions==expected["communication_documentary_revisions_known"]
        assert persisted["snapshot"]["episodes"]["explicit_approval_documented"]==expected["logical_decisions"]
    for valid in ("2026-09-15","2026-10-10"):
        persisted=registry.query_registry(db,cut=cut,valid_at=valid)
        chron=persisted["snapshot"]["graph"]["chronicle"]["nodes"]
        expected=oracle["warehouse"]["bitemporal_actor_event_equivalence"]["views_by_valid_day"][valid]
        assert sum(x["kind"]=="ROLE" for x in chron)==expected["role_assertions_visible_at_valid_day"]
        events=[x for x in chron if x["kind"]=="EVENT"]
        assert len(events)==expected["logical_events_after_typed_amendment"]==1
        assert events[0]["documentary_revision_count"]==expected["event_documentary_revisions_known"]
    assert oracle["explorer"]["catalog"]["visible_distribution_count"]==(
        registry.query_registry(db,cut=cut)["registry"]["visible_distribution_count"])


@pytest.mark.parametrize("route,method,expected",[
    ("/api/scientific-registry?cut=wrong","GET",400),
    ("/api/scientific-registry?cut=early&published_until=2026-10-30T12%3A00%3A00Z","GET",400),
    ("/api/scientific-registry?cut=late&cut=early","GET",400),
    ("/api/scientific-registry?source_id=SYN%3ACHAIN_V1","GET",400),
    ("/api/scientific-registry?valid_at=%27%3BDROP%20TABLE%20distribution","GET",400),
    ("/api/scientific-registry?family=STAGE","GET",400),
    ("/api/scientific-registry","POST",404),
])
def test_s9_http_closed_query_or_ingest_without_post(local_registry_http,route,method,expected):
    get,_=local_registry_http
    status,cache,payload=get(route,method=method)
    assert status==expected and cache=="no-store"
    assert "error" in payload


def test_s9_http_corrupted_database_fails_closed_503_not_scientific_conflict(
        local_registry_http):
    get,path=local_registry_http
    assert get("/api/scientific-registry")[0]==200
    with sqlite3.connect(path) as con:
        trigger="registry_fact_immutable_update"
        sql=con.execute("SELECT sql FROM sqlite_master WHERE name=?",(trigger,)).fetchone()[0]
        con.execute(f"DROP TRIGGER {trigger}")
        con.execute("UPDATE typed_fact SET amendment_of='S9:C:ACTOR' WHERE fact_id='S9:C:COMM_V2'")
        con.execute(sql)
        con.commit()
    status,cache,payload=get("/api/scientific-registry?cut=early")
    assert (status,cache,payload)==(503,"no-store",{"error":"SYNTHETIC_REGISTRY_UNAVAILABLE"})
    # An independently executing Node scientific lab remains separate; the
    # corruption does not become an empirical witness or fabricated S7 result.
    status,_,oracle=get("/api/scientific-integration-lab?cut=late")
    assert status==200 and oracle["scientific_AB_cycles"]==0
