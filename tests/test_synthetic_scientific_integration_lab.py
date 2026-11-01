"""Preregistered oracles for the *new* synthetic Python/Node/HTTP consumer.

All numbers, dates, actors and evidence text in the implementation are fictitious.
This test is neither historical corroboration nor an R5 release test.
"""
from __future__ import annotations

import http.client
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import subprocess
import sys
from threading import Thread
from dataclasses import replace

import pytest

from politics_fantasy.scientific_integration_lab import report
from politics_fantasy.server import handler_factory


@pytest.mark.parametrize("cut,expected_roles,expected_state", [
    ("early", 1, "v1"), ("late", 2, "v2"),
])
def test_real_contracts_join_only_at_declared_knowledge_cut(cut, expected_roles, expected_state):
    result = report(cut=cut)
    assert result["schema"] == "pfl.synthetic_scientific_integration_lab.v1"
    assert result["evidence_class"] == "SYNTHETIC_LAB_ONLY"
    assert result["warehouse"]["roles_visible_as_of"] == expected_roles
    assert result["temporal"]["revision_visible"] == expected_state
    assert result["warehouse"]["synthetic_sha256_parity"] is True
    assert result["rights"]["reuse_admitted"] is False
    assert result["independent_all_received_denominator"] is None
    assert result["real_corpus_ingestion_allowed"] is False
    assert result["R5"] == "STOP_R5"
    assert result["scientific_AB_cycles"] == 0


def test_before_capture_cannot_leak_pp04_or_rival_models_or_terminal_decisions():
    early = report(cut="early")
    late = report(cut="late")
    assert early["pp04"] is None
    assert early["capture_models"] is None
    assert early["procedure"]["terminal_by_cause"]["INADMITTED"] == 0
    assert early["procedure"]["terminal_by_cause"]["APPROVED"] == 0
    assert early["procedure"]["unknown_followup"] > late["procedure"]["unknown_followup"]
    assert late["pp04"]["planned_count"] == 2
    assert late["pp04"]["approved_count"] == 1
    assert late["pp04"]["pending_unsplit_count"] == 1
    assert late["pp04"]["not_included_4221_excluded"] is True
    assert late["pp04"]["item_crosswalk_verified"] is False
    assert late["procedure"]["terminal_by_cause"]["INADMITTED"] == 1
    assert late["procedure"]["observed_pending_at_last_witness"] == 2
    assert late["procedure"]["unknown_followup"] == 1
    assert late["right_censoring_independently_attested"] is False


def test_invented_followup_end_witness_is_temporal_not_rejection_or_zero():
    old, new=report(cut="early"),report(cut="late")
    assert old["temporal"]["synthetic_followup_end_witnesses"]==0
    assert new["temporal"]["synthetic_followup_end_witnesses"]==1
    assert new["procedure"]["unknown_followup"]==1
    assert new["right_censoring_independently_attested"] is False
    assert new["independent_all_received_denominator"] is None


def test_join_stage_episode_and_temporal_followup_by_exact_id_at_asof():
    """New E2E falsifier: two valid outputs were not actually reconciled."""
    early=report(cut="early")
    late=report(cut="late")
    assert early["followup_reconciliation"] == {
        "schema":"pfl.synthetic_followup_reconciliation.v1",
        "explicit_censor_witnesses":0,"unknown_without_censor_witness":4,
        "pending_not_censoring":1,"negative_outcomes_not_censoring":0,
        "temporal_witness_fixture_receipt_checked":False,
        "stage_documents_authenticated":False,"real_censoring_attested":False,
    }
    assert late["followup_reconciliation"] == {
        "schema":"pfl.synthetic_followup_reconciliation.v1",
        "explicit_censor_witnesses":1,"unknown_without_censor_witness":0,
        "pending_not_censoring":2,"negative_outcomes_not_censoring":1,
        "temporal_witness_fixture_receipt_checked":True,
        "stage_documents_authenticated":False,"real_censoring_attested":False,
    }
    assert late["procedure"]["unknown_followup"]==1  # original contract immutable
    assert late["right_censoring_independently_attested"] is False


def test_fake_censor_witness_cannot_join_pending_case_or_wrong_digest():
    from politics_fantasy.scientific_integration_lab import (
        _assets,_temporal,_procedural,_reconcile_followup,CUTS,
    )
    from politics_fantasy.temporal_evidence import SourceRef
    at=CUTS["late"]
    temporal,snapshot,receipts=_temporal(_assets(),at=at)
    stage,episodes=_procedural(at)
    real_event=next(r for r in snapshot.records
                    if r.predicate=="OBSERVATION_WINDOW_ENDED_WITHOUT_DECISION")
    wrong_episode=replace(real_event,
        source_record_id="FOLLOWUP_END_FOR_ENTRY5",
        subject=SourceRef("SYNTHETIC_PROCESS","PROCESS","ENTRY5"))
    with pytest.raises(RuntimeError,match="CENSOR_WITNESS_EPISODE_LINK_INVALID"):
        _reconcile_followup(snapshot=replace(snapshot,records=tuple(
            wrong_episode if r==real_event else r for r in snapshot.records)),
            episodes=episodes,procedural=stage,receipts=receipts)
    wrong_sha=replace(real_event,source_sha256="0"*64)
    with pytest.raises(RuntimeError,match="CENSOR_SOURCE_RECEIPT_BINDING_MISMATCH"):
        _reconcile_followup(snapshot=replace(snapshot,records=tuple(
            wrong_sha if r==real_event else r for r in snapshot.records)),
            episodes=episodes,procedural=stage,receipts=receipts)


def test_early_http_aggregate_must_not_reveal_later_asset_hashes_or_ids():
    """Falsifier: knowing *of* tomorrow's bytes is knowledge-time leakage."""
    early = report(cut="early")
    late = report(cut="late")
    serialized = json.dumps(early,sort_keys=True)
    assert early["source_assets"] == []
    assert early["rights"]["per_asset"] == {}
    assert "assets_verified_by_bytes" not in early["warehouse"]
    assert early["warehouse"].get("assets_bound_to_fixed_fixture") in (None, False)
    for asset in late["source_assets"]:
        assert asset["id"] not in serialized
        assert asset["sha256"] not in serialized


def test_direct_node_bridge_rejects_self_labeled_arbitrary_document_bytes():
    """Self-supplied 'SYNTHETIC DOCUMENT FIXTURE' is not a trusted allowlist."""
    if shutil.which("node") is None:
        pytest.skip("Node not installed")
    from politics_fantasy.scientific_integration_lab import _assets, _sha, FAKE_PARITY
    node=Path(__file__).resolve().parents[1]/"scripts"/"scientific_integration_warehouse.mjs"
    assets=_assets()
    assets[0]["text"]="SYNTHETIC DOCUMENT FIXTURE\nUNREVIEWED ARBITRARY BYTES\n"
    assets[0]["sha256"]=_sha(assets[0]["text"])
    proc=subprocess.run(["node",str(node)],input=json.dumps({
        "cut":"late","scenario":"baseline","sha256":_sha(FAKE_PARITY),
        "assets":assets,
    }),text=True,capture_output=True,timeout=5)
    assert proc.returncode!=0
    assert "UNREGISTERED_SYNTHETIC_FIXTURE" in proc.stderr


def test_pp04_asset_identity_is_exact_across_python_rights_temporal_and_js():
    """A namespace transformation is not a source-issued identity crosswalk."""
    r=report(cut="late")
    expected=[a["id"] for a in r["source_assets"]]
    assert r["temporal"]["pp04_source_ids_seen"]==expected
    assert set(r["rights"]["per_asset"])==set(expected)
    assert r["warehouse"]["assets_bound_to_fixed_fixture"] is True


def test_rivals_and_units_not_promoted_by_editorial_concordance():
    late = report(cut="late")
    assert late["denominator_comparison"]["frame_compatible"] is False
    assert late["denominator_comparison"]["independent_denominator_certified"] is False
    assert late["denominator_comparison"]["eligible_risk_population"] is None
    assert late["capture_models"]["same_visible_projection"] is True
    assert late["capture_models"]["different_hypothetical_trend_sign"] is True
    assert late["capture_models"]["real_reform_effect_identified"] is False
    assert late["institutional_graph"]["legal_identity_authenticated"] is False


def test_raw_rights_spoof_blocked_in_both_languages():
    result = report(cut="late", scenario="rights_spoof")
    assert result["warehouse"]["spoofed_raw_source_visible_as_of"] is False
    assert result["warehouse"]["rights_independent_attestation_available"] is False
    assert result["warehouse"]["real_people_scoring_enabled"] is False
    assert result["rights"]["reuse_admitted"] is False
    assert result["R5"] == "STOP_R5"


def test_spoofed_raw_does_not_create_false_alarm_at_early_asof():
    """An early cut has one allowed SYN source, not two; compare exact IDs."""
    early = report(cut="early", scenario="rights_spoof")
    assert early["warehouse"]["source_count_visible_as_of"] == 1
    assert early["warehouse"]["spoofed_raw_source_visible_as_of"] is False
    assert early["warehouse"]["raw_rights_blocker"] is True
    assert early["R5"] == "STOP_R5"


def test_no_private_keys_can_pass_node_warehouse_boundary():
    result = report(cut="late", scenario="privacy_probe")
    assert result["warehouse"]["recursive_private_key_rejected"] is True
    assert "email" not in json.dumps(result).lower()


def test_reject_unknown_scenario_and_untrusted_horizon():
    with pytest.raises(ValueError, match="INVALID_SYNTHETIC_LAB_CUT"):
        report(cut="2026-11-01T12:00:00Z")
    with pytest.raises(ValueError, match="INVALID_SYNTHETIC_LAB_SCENARIO"):
        report(scenario="real_asset_ingest")


def test_node_recomputes_fixed_fixture_digest_and_rejects_tamper():
    if shutil.which("node") is None:
        pytest.skip("Node not installed")
    node = Path(__file__).resolve().parents[1] / "scripts" / "scientific_integration_warehouse.mjs"
    result = subprocess.run(["node", str(node)], input=json.dumps({
        "cut": "late", "scenario": "baseline", "sha256": "0" * 64,
        "assets": [],
    }), capture_output=True, text=True, timeout=5)
    assert result.returncode != 0
    assert "SYNTHETIC_SHA_MISMATCH" in result.stderr


def test_real_http_consumer_local_host_cache_and_query_gates(tmp_path):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_factory(
        tmp_path / "synthetic-demo.sqlite", None, None))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        def request(path, host=None):
            conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            headers = {"Host": host} if host else {}
            conn.request("GET", path, headers=headers)
            reply = conn.getresponse()
            status = reply.status
            cache = reply.getheader("Cache-Control")
            body = json.loads(reply.read())
            conn.close()
            return status, cache, body

        ok, cache, body = request("/api/scientific-integration-lab?cut=early")
        assert ok == 200 and cache == "no-store"
        assert body["warehouse"]["roles_visible_as_of"] == 1
        assert body["followup_reconciliation"]["explicit_censor_witnesses"] == 0
        assert body["followup_reconciliation"]["real_censoring_attested"] is False
        assert "SYNTHETIC:ENTRY4" not in json.dumps(body)
        for path in ("/api/scientific-integration-lab?cut=early&cut=late",
                     "/api/scientific-integration-lab?url=https%3A%2F%2Fexample.invalid",
                     "/api/scientific-integration-lab?scenario=real_asset_ingest"):
            assert request(path)[0] == 400
        assert request("/api/scientific-integration-lab", "outside.invalid")[0] == 403
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_bridge_failure_is_http_503_never_synthetic_success(tmp_path, monkeypatch):
    from politics_fantasy import scientific_integration_lab
    def broken_node(*args, **kwargs):
        raise OSError("simulated unavailable runtime")
    monkeypatch.setattr(scientific_integration_lab.subprocess,"run",broken_node)
    server=ThreadingHTTPServer(("127.0.0.1",0),handler_factory(
        tmp_path/"synthetic-demo.sqlite",None,None))
    thread=Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        conn=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=5)
        conn.request("GET","/api/scientific-integration-lab?cut=late")
        response=conn.getresponse()
        result=json.loads(response.read())
        assert response.status==503
        assert response.getheader("Cache-Control")=="no-store"
        assert result=={"error":"SYNTHETIC_BRIDGE_UNAVAILABLE"}
        conn.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_offline_integration_is_deterministic_and_aggregate_only():
    left=report(cut="early")
    right=report(cut="early")
    assert json.dumps(left,sort_keys=True)==json.dumps(right,sort_keys=True)
    output=json.dumps(report(cut="late"),sort_keys=True).lower()
    for unsafe in ("source_block_private","title_candidate","objective_line_text",
                   "personal_email","private_address","real_outcome_rows"):
        assert unsafe not in output
    assert "scientific_estimator_admitted\": false" in output


def test_actual_offline_cli_consumer_no_original_paths_or_scoring():
    script=Path(__file__).resolve().parents[1]/"scripts"/"run_scientific_integration_lab.py"
    output=subprocess.run([sys.executable,str(script),"--cut","early"],
                          text=True,capture_output=True,timeout=8)
    assert output.returncode==0
    result=json.loads(output.stdout)
    assert result["pp04"] is None
    assert result["R5"]=="STOP_R5"
    assert result["warehouse"]["roles_visible_as_of"]==1
    assert result["real_people_scoring_enabled"] is False


def test_node_ipc_rejects_forged_positive_scientific_authority(monkeypatch):
    """A drifted Node child may not inject positive real evidence into HTTP."""
    from politics_fantasy import scientific_integration_lab as lab
    original=lab._node_warehouse
    # Keep production subprocess pathway but replace stdout with a
    # syntactically valid schema claiming an impossible real denominator.
    def forked_child(args, **kwargs):
        assets=lab._assets()
        fake={
            "schema":"pfl.synthetic_warehouse_bridge.v1",
            "synthetic_sha256_parity":True,
            "assets_verified_by_bytes":[{"id":a["id"],"sha256":a["sha256"]} for a in assets],
            "roles_visible_as_of":2,"roles_at_valid_day_and_cut":2,
            "decisions_visible_as_of":2,"source_count_visible_as_of":2,
            "spoofed_raw_source_visible_as_of":False,
            "recursive_private_key_rejected":False,
            "rights_independent_attestation_available":False,
            "real_people_scoring_enabled":False,
            "raw_rights_blocker":False,
            "real_denominator":5,
            "first_public_at_real":"2026-09-01T00:00:00Z",
            "publisher_authenticated":False,
            "source_identity_crosswalk_certified":True,
        }
        return subprocess.CompletedProcess(args,0,stdout=json.dumps(fake),stderr="")
    monkeypatch.setattr(lab.subprocess,"run",forked_child)
    with pytest.raises(RuntimeError,match="CROSS_LANGUAGE_CONTRACT_DIVERGENCE"):
        lab.report(cut="late")
