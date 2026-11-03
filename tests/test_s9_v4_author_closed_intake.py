"""Differential S9 v4 sandbox intake: intentionally authored, never real data.

No fabricated PREPATCH failures; each test creates its own SQLite under
tmp_path and never writes protected or original sources. No external network.
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

import pytest

from politics_fantasy import scientific_registry as reg
from politics_fantasy.server import handler_factory


@pytest.fixture
def path(tmp_path:Path):
    return tmp_path/"scientific_registry_synthetic.sqlite3"


def _guard(resp:dict):
    assert resp["registry"]["schema_version"]==4
    assert resp["registry"]["migration_history"]==[1,2,3,4]
    assert resp["registry"]["recorded_distribution_count"]==6
    assert resp["registry"]["internal_uncatalogued_fixture_receipts"]==1
    assert resp["R5"]=="STOP_R5"
    assert resp["real_source_ingestion_allowed"] is False
    assert resp["independent_denominator"] is None
    assert resp["scientific_ab_cycles"]==0
    assert resp["release_gates_passed"]==0
    intake=resp["snapshot"]["synthetic_intake"]
    assert intake["schema"]=="pfl.synthetic_intake_overlay.v1"
    assert intake["history_event_count"]==intake["intake_count"]*2
    assert intake["registered_count"]==intake["intake_count"]
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
    canonical=resp["snapshot_receipt"]["canonical_json"]
    digest=hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert digest==resp["snapshot_receipt"]["sha256"]==resp["snapshot_receipt_sha256"]
    assert json.loads(canonical)["snapshot"]["synthetic_intake"]==intake
    public=json.dumps(resp,ensure_ascii=False)
    for internal in ("AUTHOR_ALPHA:FILE_1","AUTHOR_BETA:FILE_1",
                     "SYN:S9_AUTHOR_ALPHA","SYN:S9_AUTHOR_BETA",
                     "REAL:UNVERIFIED_FIXTURE","SYNTHETIC S9 AUTHOR-CLOSED INTAKE",
                     "A:LOCAL_ACTOR","B:LOCAL_PROCESS"):
        assert internal not in public,internal
    for entry in intake["entries"]:
        assert entry["rights_for_public_display"] is False
        assert entry["empirical_admitted"] is False
        assert entry["canonical_source_rows_imported"]==0
        assert entry["real_first_public_at"] is None
        assert entry["real_issuer_authenticated"] is False
        check={k:v for k,v in entry.items() if k!="public_descriptor_sha256"}
        assert hashlib.sha256(reg._json(check).encode()).hexdigest()==entry["public_descriptor_sha256"]


def _original_state(db:Path):
    with sqlite3.connect(db) as connection:
        return {name:connection.execute(f"SELECT * FROM {name} ORDER BY 1").fetchall()
                for name in ("distribution","typed_fact","typed_edge","assessment_event")}


def test_s9_v4_no_seeded_overlay_two_sequential_real_cli_enrolls(path):
    root=Path(__file__).resolve().parents[1]/"src"
    env={**os.environ,"PYTHONPATH":str(root)}

    def cli(key:str):
        result=subprocess.run([sys.executable,"-m","politics_fantasy.scientific_registry",
                               "--db",str(path),"--enroll",key],
                              cwd=root.parent,env=env,check=True,
                              capture_output=True,text=True,timeout=15)
        return json.loads(result.stdout)

    first=reg.query_registry(path)
    assert first["snapshot"]["synthetic_intake"]["intake_count"]==0
    assert _original_state(path)["distribution"]
    baseline=_original_state(path)
    a=cli("sandbox_alpha_v1")
    assert a["status"]=="SANDBOX_VALIDATED"
    assert a["intake_id"]=="S9:INTAKE_01"
    assert a["event_count_appended"]==2
    after_a=reg.query_registry(path)
    assert after_a["snapshot"]["synthetic_intake"]["intake_count"]==1
    assert after_a["snapshot"]["synthetic_intake"]["logical_source_count"]==1
    b=cli("sandbox_beta_v1")
    assert b["status"]=="SANDBOX_VALIDATED"
    assert b["intake_id"]=="S9:INTAKE_02"
    assert b["event_count_appended"]==2
    after_b=reg.query_registry(path,valid_at="2026-10-10")
    overlay=after_b["snapshot"]["synthetic_intake"]
    assert (overlay["intake_count"],overlay["history_event_count"],
            overlay["logical_source_count"],overlay["documentary_revision_count"])==(2,4,2,2)
    assert overlay["graph"]["node_count"]==6
    assert overlay["graph"]["edge_count"]==4
    assert _original_state(path)==baseline
    assert cli("sandbox_alpha_v1")["idempotent_replay"] is True
    assert cli("sandbox_alpha_v1")["event_count_appended"]==0
    assert reg.query_registry(path,valid_at="2026-10-10")==after_b
    _guard(after_b)


def test_s9_v4_revision_requires_prior_and_counts_only_one_logical_source(path):
    reg.seed_registry(path)
    before=_original_state(path)
    with pytest.raises(ValueError,match="SANDBOX_REVISION_PREREQUISITE_REQUIRED"):
        reg.enroll_synthetic_fixture(path,"sandbox_alpha_v2")
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT COUNT(*) FROM synthetic_intake_event").fetchone()[0]==0
    reg.enroll_synthetic_fixture(path,"sandbox_alpha_v1")
    reg.enroll_synthetic_fixture(path,"sandbox_alpha_v2")
    v11=reg.query_registry(path,valid_at="2026-09-11")
    v15=reg.query_registry(path,valid_at="2026-09-15")
    for sample in (v11,v15):
        _guard(sample)
        overlay=sample["snapshot"]["synthetic_intake"]
        assert overlay["logical_source_count"]==1
        assert overlay["documentary_revision_count"]==2
        assert overlay["logical_decisions_count"]==0
        assert overlay["intake_count"]==2
        assert overlay["graph"]["node_count"]==3
        assert overlay["graph"]["edge_count"]==2
    nodes11=v11["snapshot"]["synthetic_intake"]["graph"]["nodes"]
    nodes15=v15["snapshot"]["synthetic_intake"]["graph"]["nodes"]
    assert all(node["documentary_revision_count"]==1 for node in nodes11)
    assert all(node["documentary_revision_count"]==2 for node in nodes15)
    assert {n["id"] for n in nodes11}=={n["id"] for n in nodes15}
    v2=[x for x in v15["snapshot"]["synthetic_intake"]["entries"]
        if x["intake_id"]=="S9:INTAKE_03"]
    assert len(v2)==1 and v2[0]["amendment_of"]=="S9:INTAKE_01"
    assert _original_state(path)==before


def test_s9_v4_registered_then_rejected_in_closed_author_fixture(path):
    result=reg.enroll_synthetic_fixture(path,"sandbox_bad_issuer")
    assert result["status"]=="SANDBOX_REJECTED"
    assert result["reason_code"]=="ISSUER_NOT_ALLOWLISTED"
    assert result["event_count_appended"]==2
    p=reg.query_registry(path)
    _guard(p)
    view=p["snapshot"]["synthetic_intake"]
    assert (view["validated_count"],view["rejected_count"],
            view["logical_source_count"],view["graph"]["node_count"])==(0,1,0,0)
    assert [x["status"] for x in view["entries"][0]["history"]]==[
        "SANDBOX_REGISTERED","SANDBOX_REJECTED"]
    assert result["rights_for_public_display"] is False
    assert result["real_source_admitted"] is False
    assert reg.enroll_synthetic_fixture(path,"sandbox_bad_issuer")["event_count_appended"]==0


def test_s9_v4_early_and_publication_cuts_never_look_ahead(path):
    reg.enroll_synthetic_fixture(path,"sandbox_alpha_v1")
    early=reg.query_registry(path,cut="early")
    prior=reg.query_registry(path,cut="late",published_until="2026-10-30T12:00:00Z")
    late=reg.query_registry(path,cut="late")
    for item in (early,prior,late):
        _guard(item)
    assert early["snapshot"]["synthetic_intake"]["intake_count"]==0
    assert prior["snapshot"]["synthetic_intake"]["intake_count"]==0
    assert late["snapshot"]["synthetic_intake"]["intake_count"]==1
    assert early["snapshot_receipt_sha256"]!=late["snapshot_receipt_sha256"]
    assert prior["snapshot_receipt_sha256"]!=late["snapshot_receipt_sha256"]
    chain=reg.query_registry(path,cut="late",family="CHAIN")
    assert chain["snapshot"]["synthetic_intake"]["intake_count"]==0


def test_s9_v4_spoof_and_unsupported_fixture_rejected_before_writing(path):
    assert not path.exists()
    with pytest.raises(ValueError,match="UNSUPPORTED_AUTHOR_CLOSED_SYNTHETIC_FIXTURE"):
        reg.enroll_synthetic_fixture(path,"evil_external.json")
    assert not path.exists()
    fixture=reg._authored_intake_fixture("sandbox_alpha_v1")
    for override in (
            {**fixture,"source_bytes":b"SYNTHETIC S9 UNAUTHORIZED"},
            {**fixture,"issuer":"REAL:SPIKE"},
            {**fixture,"revision":2},
            {**fixture,"source_local_id":"REAL:PRIVATE_ID"},
            {**fixture,"typed_manifest":{**fixture["typed_manifest"],"nodes":[]}},
            {**fixture,"source_first_public_at_fixture":"2020-01-01T00:00:00Z"},
            {**fixture,"source_bytes":"NOT_BYTES"},
    ):
        with pytest.raises(reg.RegistryIntegrityError,match="SANDBOX_AUTHOR_CLOSED_WIRE"):
            reg.enroll_synthetic_fixture(path,"sandbox_alpha_v1",wire=override)
        assert not path.exists()


def test_s9_v4_concurrent_enroll_same_id_and_immutable_events(path):
    with ThreadPoolExecutor(max_workers=5) as executor:
        outcomes=list(executor.map(lambda _:reg.enroll_synthetic_fixture(
            path,"sandbox_beta_v1"),range(10)))
    assert sum(r["event_count_appended"] for r in outcomes)==2
    assert all(x["status"]=="SANDBOX_VALIDATED" for x in outcomes)
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM synthetic_intake_event").fetchone()[0]==2
        for sql in (
                "UPDATE synthetic_intake_event SET issuer_claim='REAL:FAKE'",
                "DELETE FROM synthetic_intake_event"):
            with pytest.raises(sqlite3.DatabaseError,match="IMMUTABLE_SYNTHETIC_INTAKE_EVENT"):
                connection.execute(sql)


def test_s9_v4_v3_to_v4_migration_retains_all_previous_exact_rows(path):
    with reg._connect(path) as db:
        db.execute("BEGIN IMMEDIATE")
        reg._migration_v1(db)
        reg._migration_v2(db)
        reg._migration_v3(db)
        reg._seed(db)
        assert db.execute("PRAGMA user_version").fetchone()[0]==3
        db.commit()
    prior=_original_state(path)
    reg.seed_registry(path)
    assert _original_state(path)==prior
    with sqlite3.connect(path) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0]==4
        assert db.execute("SELECT COUNT(*) FROM synthetic_intake_event").fetchone()[0]==0
        assert [r[0] for r in db.execute("SELECT version FROM schema_history ORDER BY version")]==[1,2,3,4]
    reg.enroll_synthetic_fixture(path,"sandbox_alpha_v1")
    assert _original_state(path)==prior
    _guard(reg.query_registry(path))


@pytest.mark.parametrize("prior_version",[1,2])
def test_s9_v4_v1_v2_to_v4_preserves_exact_sources_and_typed_rows(path,prior_version):
    with reg._connect(path) as db:
        db.execute("BEGIN IMMEDIATE")
        reg._migration_v1(db)
        if prior_version==2:
            reg._migration_v2(db)
        db.execute("INSERT INTO registry_meta VALUES(1,?,?,?,?)",(
            reg.FIXTURE_ID,reg._manifest_hash(),
            "2026-11-01T12:00:00Z","STOP_R5"))
        reg._insert_rows(db,"distribution",reg.SOURCES_COLUMNS,reg._closed_sources())
        if prior_version==2:
            reg._insert_rows(db,"typed_fact",reg.FACT_COLUMNS,reg._closed_facts())
            reg._insert_rows(db,"typed_edge",reg.EDGE_COLUMNS,reg._closed_edges())
        assert db.execute("PRAGMA user_version").fetchone()[0]==prior_version
        sources=[tuple(r) for r in db.execute("SELECT * FROM distribution ORDER BY 1")]
        typed=([tuple(r) for r in db.execute("SELECT * FROM typed_fact ORDER BY 1")]
               if prior_version==2 else None)
        db.commit()
    reg.seed_registry(path)
    with sqlite3.connect(path) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0]==4
        assert list(db.execute("SELECT * FROM distribution ORDER BY 1"))==sources
        if typed is not None:
            assert list(db.execute("SELECT * FROM typed_fact ORDER BY 1"))==typed
        assert db.execute("SELECT COUNT(*) FROM assessment_event").fetchone()[0]==16
        assert db.execute("SELECT COUNT(*) FROM synthetic_intake_event").fetchone()[0]==0
    _guard(reg.query_registry(path))


@pytest.mark.parametrize("column,value",[
    ("source_bytes",b"SYNTHETIC SOURCE TAMPERED"),
    ("source_sha256","0"*64),
    ("typed_manifest_bytes",b"{}"),
    ("typed_manifest_sha256","a"*64),
    ("receipt_bytes",b"{}"),
    ("receipt_sha256","f"*64),
    ("issuer_claim","REAL:INSTITUTION"),
    ("source_local_id","REAL:PRIVATE_ROW"),
    ("revision",2),
    ("first_public_known_at","2026-10-30T12:00:00Z"),
])
def test_s9_v4_tamper_overlay_even_with_removed_trigger_fails_closed(path,column,value):
    reg.enroll_synthetic_fixture(path,"sandbox_alpha_v1")
    with sqlite3.connect(path) as connection:
        trigger="registry_intake_immutable_update"
        sql=connection.execute("SELECT sql FROM sqlite_master WHERE name=?",(trigger,)).fetchone()[0]
        connection.execute(f"DROP TRIGGER {trigger}")
        connection.execute(f"UPDATE synthetic_intake_event SET {column}=? "
                           "WHERE event_id='S9:INTAKE_01:EVENT_2'",(value,))
        connection.execute(sql)
        connection.commit()
    with pytest.raises(reg.RegistryIntegrityError):
        reg.query_registry(path)


def test_s9_v4_prohibited_rights_and_schema_ddl_override_rejected(path):
    reg.enroll_synthetic_fixture(path,"sandbox_beta_v1")
    with sqlite3.connect(path) as connection:
        trigger="registry_intake_immutable_update"
        old=connection.execute("SELECT sql FROM sqlite_master WHERE name=?",(trigger,)).fetchone()[0]
        connection.execute(f"DROP TRIGGER {trigger}")
        for sql in (
            "UPDATE synthetic_intake_event SET rights_for_public_display=1",
            "UPDATE synthetic_intake_event SET issuer_authenticated_real=1",
            "UPDATE synthetic_intake_event SET first_public_at_real='2026-09-01T00:00:00Z'",
            "UPDATE synthetic_intake_event SET independent_denominator=10",
            "UPDATE synthetic_intake_event SET canonical_rows_imported=1",
        ):
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(sql)
        connection.execute(old)
        connection.commit()
    _guard(reg.query_registry(path))
    with sqlite3.connect(path) as connection:
        connection.execute("DROP TRIGGER registry_intake_immutable_update")
        connection.execute("""CREATE TRIGGER registry_intake_immutable_update
            BEFORE UPDATE ON synthetic_intake_event BEGIN SELECT 1; END""")
        connection.commit()
    with pytest.raises(reg.RegistryIntegrityError,match="DDL_HASH_DIVERGENCE"):
        reg.query_registry(path)


def test_s9_v4_http_200_400_503_overlay_corrupt_and_no_external_post(tmp_path:Path):
    game=tmp_path/"demo_game.sqlite3"
    path=reg.registry_path(game)
    server=ThreadingHTTPServer(("127.0.0.1",0),handler_factory(game,None,None))
    thread=Thread(target=server.serve_forever,daemon=True)
    thread.start()

    def fetch(route:str,method:str="GET"):
        connection=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=8)
        connection.request(method,route)
        response=connection.getresponse()
        status=response.status
        payload=json.loads(response.read())
        connection.close()
        return status,payload

    try:
        status,empty=fetch("/api/scientific-registry")
        assert status==200 and empty["snapshot"]["synthetic_intake"]["intake_count"]==0
        reg.enroll_synthetic_fixture(path,"sandbox_alpha_v1")
        status,late=fetch("/api/scientific-registry?cut=late&valid_at=2026-10-10")
        assert status==200
        _guard(late)
        assert late["snapshot"]["synthetic_intake"]["intake_count"]==1
        assert fetch("/api/scientific-registry?fixture_id=sandbox_alpha_v1")[0]==400
        assert fetch("/api/scientific-registry",method="POST")[0]==404
        with sqlite3.connect(path) as db:
            trigger="registry_intake_immutable_update"
            old=db.execute("SELECT sql FROM sqlite_master WHERE name=?",(trigger,)).fetchone()[0]
            db.execute(f"DROP TRIGGER {trigger}")
            db.execute("UPDATE synthetic_intake_event SET receipt_sha256='0' "
                       "WHERE event_id='S9:INTAKE_01:EVENT_2'")
            db.execute(old)
            db.commit()
        status,failed=fetch("/api/scientific-registry")
        assert status==503 and failed=={"error":"SYNTHETIC_REGISTRY_UNAVAILABLE"}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
