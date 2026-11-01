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


@pytest.mark.parametrize("future_kind", ["PENDING", "APPROVED", "VISIBLE_ADMITTED"])
def test_future_or_nonterminal_step_cannot_invalidate_visible_censor_witness(future_kind):
    """Future evidence must stay future; ADMITTED is not a terminal act.

    PREPATCH fixture uses the real auditor + real temporal ledger. No real cases.
    """
    from politics_fantasy.scientific_integration_lab import (
        _assets, _temporal, _procedural, _reconcile_followup, CUTS,
    )
    from politics_fantasy.procedural_stage_accounting import (
        PendingWitness, StageAct, audit_lab,
    )
    at = CUTS["late"]
    _, snapshot, receipts = _temporal(_assets(), at=at)
    baseline_procedure, episodes = _procedural(at)
    baseline = _reconcile_followup(
        snapshot=snapshot, episodes=episodes,
        procedural=baseline_procedure, receipts=receipts)
    assert baseline["explicit_censor_witnesses"] == 1
    episode = episodes[3]  # exact server-owned SYNTHETIC:ENTRY4
    if future_kind == "PENDING":
        future = PendingWitness(
            pending_on="2026-11-03", observed_at="2026-11-04T12:00:00Z",
            document_sha_claim=episode.entry_sha_claim,
            legal_calendar_zone="Europe/Madrid")
        mutated_episode = replace(episode, pending=(future,))
    elif future_kind == "APPROVED":
        future = StageAct(
            stage="APPROVED", occurred_on="2026-11-03",
            documented_on="2026-11-04", observed_at="2026-11-05T12:00:00Z",
            document_sha_claim=episode.entry_sha_claim,
            legal_calendar_zone="Europe/Madrid")
        mutated_episode = replace(episode, acts=(future,))
    else:
        future = StageAct(
            stage="ADMITTED", occurred_on="2026-09-11",
            documented_on="2026-09-12", observed_at="2026-09-20T12:00:00Z",
            document_sha_claim=episode.entry_sha_claim,
            legal_calendar_zone="Europe/Madrid")
        mutated_episode = replace(episode, acts=(future,))
    changed = episodes[:3] + (mutated_episode,) + episodes[4:]
    replay = audit_lab(frame=episode.frame, episodes=changed, as_of=at)
    assert replay == baseline_procedure  # original stage contract is bitemporal
    # The integration wrapper MUST preserve that invariant too.
    assert _reconcile_followup(
        snapshot=snapshot, episodes=changed,
        procedural=replay, receipts=receipts) == baseline


@pytest.mark.parametrize("known_kind", ["PENDING", "REJECTED"])
def test_observed_pending_or_terminal_step_cannot_be_censored(known_kind):
    """Control: the temporal gate may not simply ignore ALL stage evidence."""
    from politics_fantasy.scientific_integration_lab import (
        _assets, _temporal, _procedural, _reconcile_followup, CUTS,
    )
    from politics_fantasy.procedural_stage_accounting import (
        PendingWitness, StageAct, audit_lab,
    )
    at = CUTS["late"]
    _, snapshot, receipts = _temporal(_assets(), at=at)
    _, episodes = _procedural(at)
    ep = episodes[3]
    if known_kind == "PENDING":
        note = PendingWitness(
            pending_on="2026-09-12", observed_at="2026-10-31T12:00:00Z",
            document_sha_claim=ep.entry_sha_claim,
            legal_calendar_zone="Europe/Madrid")
        changed_ep = replace(ep, pending=(note,))
    else:
        note = StageAct(
            stage="REJECTED", occurred_on="2026-09-11",
            documented_on="2026-09-12", observed_at="2026-10-31T12:00:00Z",
            document_sha_claim=ep.entry_sha_claim,
            legal_calendar_zone="Europe/Madrid")
        changed_ep = replace(ep, acts=(note,))
    modified = episodes[:3] + (changed_ep,) + episodes[4:]
    replay = audit_lab(frame=ep.frame, episodes=modified, as_of=at)
    assert replay["unknown_followup"] == 0
    with pytest.raises(RuntimeError, match="CENSOR_WITNESS_EPISODE_LINK_INVALID"):
        _reconcile_followup(
            snapshot=snapshot, episodes=modified,
            procedural=replay, receipts=receipts)


def test_reconcile_rejects_genuinely_valid_procedural_output_from_wrong_cut():
    """PREPATCH: mixed temporal cut and stage cut silently produced a hybrid."""
    from politics_fantasy.scientific_integration_lab import (
        _assets, _temporal, _procedural, _reconcile_followup, CUTS,
    )
    _, late_snapshot, receipts = _temporal(_assets(), at=CUTS["late"])
    early_procedural, early_episodes = _procedural(CUTS["early"])
    late_procedural, late_episodes = _procedural(CUTS["late"])
    assert early_procedural["unknown_followup"] == 4
    assert late_procedural["unknown_followup"] == 1
    # Two correct contracts from DIFFERENT knowledge cuts must fail the join.
    with pytest.raises(RuntimeError, match="FOLLOWUP_CUT_MISMATCH"):
        _reconcile_followup(snapshot=late_snapshot, episodes=early_episodes,
                            procedural=early_procedural, receipts=receipts)
    matched = _reconcile_followup(snapshot=late_snapshot, episodes=late_episodes,
                                  procedural=late_procedural, receipts=receipts)
    assert matched["explicit_censor_witnesses"] == 1
    assert matched["unknown_without_censor_witness"] == 0


def test_reconcile_cannot_accept_procedural_counts_not_derived_from_episodes():
    from politics_fantasy.scientific_integration_lab import (
        _assets, _temporal, _procedural, _reconcile_followup, CUTS,
    )
    _, snapshot, receipts = _temporal(_assets(), at=CUTS["late"])
    procedural, episodes = _procedural(CUTS["late"])
    forged = dict(procedural, observed_pending_at_last_witness=0)
    with pytest.raises(RuntimeError, match="FOLLOWUP_CUT_MISMATCH"):
        _reconcile_followup(snapshot=snapshot, episodes=episodes,
                            procedural=forged, receipts=receipts)


def test_pp04_http_consumer_must_preserve_both_source_local_documentary_populations():
    """Falsifier: the actual dual parser counts NO INCLUIDAS but HTTP drops it.

    A boolean about 4.22.1 alone does not expose the other UNPLANNED entries.
    Neither count is an independently authenticated entry denominator.
    """
    early=report(cut="early")
    late=report(cut="late")
    assert early["pp04"] is None
    assert late["pp04"]["planned_count"] == 2
    assert late["pp04"]["line_parser_unplanned_entries_source_local"] == 2
    assert late["pp04"]["approved_count"] == 1
    assert late["pp04"]["pending_unsplit_count"] == 1
    assert late["pp04"]["not_included_4221_excluded"] is True
    assert late["pp04"]["count_is_source_internal_only"] is True
    assert late["pp04"]["item_crosswalk_verified"] is False
    assert late["independent_all_received_denominator"] is None


def test_pp04_documentary_populations_reach_actual_local_http_without_lookahead(tmp_path):
    server=ThreadingHTTPServer(("127.0.0.1",0),handler_factory(
        tmp_path/"synthetic-demo.sqlite",None,None))
    thread=Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        def get(cut):
            conn=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=5)
            conn.request("GET","/api/scientific-integration-lab?cut="+cut)
            res=conn.getresponse()
            status=res.status;cache=res.getheader("Cache-Control")
            payload=json.loads(res.read());conn.close()
            return status,cache,payload
        early=get("early")
        late=get("late")
        assert early[0]==late[0]==200
        assert early[1]==late[1]=="no-store"
        assert early[2]["pp04"] is None
        assert late[2]["pp04"]["planned_count"]==2
        assert late[2]["pp04"]["line_parser_unplanned_entries_source_local"]==2
        assert late[2]["pp04"]["not_included_4221_excluded"] is True
        assert late[2]["pp04"]["item_crosswalk_verified"] is False
        assert late[2]["independent_all_received_denominator"] is None
        assert late[2]["R5"]=="STOP_R5"
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5)


def test_http_rejects_internal_cross_cut_divergence_instead_of_returning_200(tmp_path, monkeypatch):
    """An incoherent Python consumer must cause HTTP 503, not a mixed JSON."""
    from politics_fantasy import scientific_integration_lab as lab
    actual = lab._procedural
    monkeypatch.setattr(lab, "_procedural", lambda at: actual(lab.CUTS["early"]))
    server=ThreadingHTTPServer(("127.0.0.1",0),handler_factory(
        tmp_path/"synthetic-demo.sqlite",None,None))
    thread=Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        conn=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=5)
        conn.request("GET","/api/scientific-integration-lab?cut=late")
        res=conn.getresponse()
        body=json.loads(res.read())
        assert res.status==503
        assert res.getheader("Cache-Control")=="no-store"
        assert body=={"error":"SYNTHETIC_BRIDGE_UNAVAILABLE"}
        conn.close()
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5)


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


def _controlled_observational_equivalence_node(experiment, cut="late"):
    """The actual Node CLI bridge, with no originals or outside network."""
    from politics_fantasy.scientific_integration_lab import (
        _assets, _sha, FAKE_PARITY, _bitemporal_fixture,
        _partial_identification_fixture,
    )
    node=Path(__file__).resolve().parents[1]/"scripts"/"scientific_integration_warehouse.mjs"
    return subprocess.run(["node",str(node)],input=json.dumps({
        "cut":cut,"scenario":"baseline","sha256":_sha(FAKE_PARITY),
        "assets":_assets(),"experiment":experiment,
        "timeline":_bitemporal_fixture(),
        "partial_identification":(
            _partial_identification_fixture() if cut=="late" else None),
    }),text=True,capture_output=True,timeout=5)


def test_controlled_observational_equivalence_two_dgps_one_public_projection():
    """New E2E capability, not a formerly failing empirical defect."""
    early=report(cut="early")
    late=report(cut="late")
    assert early["capture_models"] is None
    assert early["warehouse"]["observational_equivalence_experiment"] is None
    assert late["capture_models"]["same_visible_projection"] is True
    assert late["capture_models"]["different_hypothetical_trend_sign"] is True
    oracle=late["warehouse"]["observational_equivalence_experiment"]
    assert oracle["schema"]=="pfl.synthetic_observational_equivalence_oracle.v1"
    assert oracle["status"]=="OBSERVATIONALLY_EQUIVALENT_NOT_IDENTIFIED"
    assert oracle["same_published_by_channel"] is True
    assert oracle["different_synthetic_trajectories"] is True
    assert oracle["hypothetical_change_by_mechanism"]=={
        "CAPTURE_EXPANSION":"ZERO_CHANGE_UNDER_ASSUMPTIONS",
        "STABLE_CAPTURE":"POSITIVE_CHANGE_UNDER_ASSUMPTIONS"}
    assert oracle["synthetic_published_totals"]=={"before":10,"after":20}
    assert oracle["synthetic_intake_under_assumptions"]=={
        "CAPTURE_EXPANSION":{"before":20,"after":20},
        "STABLE_CAPTURE":{"before":20,"after":40}}
    assert oracle["empirical_estimand_admitted"] is False
    assert oracle["real_causal_effect_identified"] is False
    assert oracle["independent_registry_witness"] is False
    assert oracle["first_public_at"] is None
    assert oracle["rights_independently_verified"] is False
    assert oracle["source_identity_crosswalk_verified"] is False
    assert late["independent_all_received_denominator"] is None
    assert late["rights"]["reuse_admitted"] is False
    assert late["R5"]=="STOP_R5"


@pytest.mark.parametrize("falsifier,expected_error", [
    ("same_aggregate_different_channel","RIVAL_PROJECTION_CHANNEL_MISMATCH"),
    ("source_id_collision","RIVAL_IDENTITY_OR_CAPTURE_ASOF_MISMATCH"),
    ("capture_after_asof","RIVAL_IDENTITY_OR_CAPTURE_ASOF_MISMATCH"),
    ("exposure_window_shift","RIVAL_EXPOSURE_WINDOW_MISMATCH"),
    ("latent_report_drift","RIVAL_LATENT_SCENARIO_NOT_MATCHING_ASSUMPTIONS"),
    ("rights_claim","UNTRUSTED_OR_FUTURE_RIVAL_WITNESS"),
    ("first_public_claim","UNTRUSTED_OR_FUTURE_RIVAL_WITNESS"),
    ("trajectory_class_falsified","RIVAL_MECHANISM_OR_TREND_MISMATCH"),
])
def test_controlled_observational_equivalence_rejects_adversarial_wire(
        falsifier, expected_error):
    if shutil.which("node") is None:
        pytest.skip("Node not installed")
    from politics_fantasy.scientific_integration_lab import _capture_rivals, CUTS
    _,wire=_capture_rivals(CUTS["late"])
    wire=json.loads(json.dumps(wire))
    if falsifier=="same_aggregate_different_channel":
        # BEFORE total is still 10; a total-only oracle would miss the swap.
        cells=wire["hypotheses"]["STABLE_CAPTURE"]["visible_by_channel"]["BEFORE_REFORM"]
        cells["PAPER"]-=1;cells["ELECTRONIC"]+=1
    elif falsifier=="source_id_collision":
        wire["synthetic_fixture_ids_by_channel"]["BEFORE_REFORM"]["PAPER"]="SYNTHETIC:PAN24"
    elif falsifier=="capture_after_asof":
        wire["capture_at_by_channel"]["AFTER_REFORM"]["PAPER"]="2026-11-02T12:00:00Z"
    elif falsifier=="exposure_window_shift":
        wire["exposure_window_by_regime"]["AFTER_REFORM"]["last_day"]="2026-10-29"
    elif falsifier=="latent_report_drift":
        wire["hypotheses"]["CAPTURE_EXPANSION"]["hypothetical_intake_by_regime"][
            "AFTER_REFORM"]=40
    elif falsifier=="rights_claim":
        wire["reuse_rights_independently_verified"]=True
    elif falsifier=="first_public_claim":
        wire["first_public_at"]="2026-09-01T00:00:00Z"
    else:
        wire["hypotheses"]["STABLE_CAPTURE"]["hypothetical_trend_sign"]="EQUAL_UNDER_ASSUMPTIONS"
    result=_controlled_observational_equivalence_node(wire)
    assert result.returncode != 0
    assert expected_error in result.stderr
    assert result.stdout == ""


def test_controlled_observational_equivalence_blocks_early_lookahead():
    if shutil.which("node") is None:
        pytest.skip("Node not installed")
    from politics_fantasy.scientific_integration_lab import _capture_rivals, CUTS
    _,wire=_capture_rivals(CUTS["late"])
    result=_controlled_observational_equivalence_node(wire,cut="early")
    assert result.returncode != 0
    assert "FUTURE_RIVAL_PROJECTION_AT_EARLY_CUT" in result.stderr


def test_controlled_observational_equivalence_reaches_http_and_fails_closed(
        tmp_path, monkeypatch):
    from politics_fantasy import scientific_integration_lab as lab
    server=ThreadingHTTPServer(("127.0.0.1",0),handler_factory(
        tmp_path/"synthetic-demo.sqlite",None,None))
    thread=Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        def get(cut):
            conn=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=5)
            conn.request("GET","/api/scientific-integration-lab?cut="+cut)
            res=conn.getresponse()
            status=res.status;cache=res.getheader("Cache-Control")
            body=json.loads(res.read());conn.close()
            return status,cache,body
        early=get("early")
        late=get("late")
        assert early[0]==late[0]==200
        assert early[1]==late[1]=="no-store"
        assert early[2]["warehouse"]["observational_equivalence_experiment"] is None
        assert late[2]["warehouse"]["observational_equivalence_experiment"][
            "status"]=="OBSERVATIONALLY_EQUIVALENT_NOT_IDENTIFIED"
        assert late[2]["warehouse"]["observational_equivalence_experiment"][
            "hypothetical_change_by_mechanism"]=={
                "CAPTURE_EXPANSION":"ZERO_CHANGE_UNDER_ASSUMPTIONS",
                "STABLE_CAPTURE":"POSITIVE_CHANGE_UNDER_ASSUMPTIONS"}
        assert late[2]["independent_all_received_denominator"] is None
        assert late[2]["R5"]=="STOP_R5"
        actual=lab._capture_rivals
        def mismatched_projection(at):
            comparison,wire=actual(at)
            wire=json.loads(json.dumps(wire))
            wire["hypotheses"]["STABLE_CAPTURE"]["visible_by_channel"][
                "BEFORE_REFORM"]["PAPER"]-=1
            wire["hypotheses"]["STABLE_CAPTURE"]["visible_by_channel"][
                "BEFORE_REFORM"]["ELECTRONIC"]+=1
            return comparison,wire
        monkeypatch.setattr(lab,"_capture_rivals",mismatched_projection)
        broken=get("late")
        assert broken[0]==503
        assert broken[1]=="no-store"
        assert broken[2]=={"error":"SYNTHETIC_BRIDGE_UNAVAILABLE"}
        # A drifted Node stdout must also be rejected after a genuine Node
        # execution, even when its source SHA, scenario and all counts agree.
        monkeypatch.setattr(lab,"_capture_rivals",actual)
        genuine_run=lab.subprocess.run
        def divergent_node_response(*args,**kwargs):
            result=genuine_run(*args,**kwargs)
            assert result.returncode==0
            payload=json.loads(result.stdout)
            oracle=payload["observational_equivalence_experiment"]
            oracle["hypothetical_change_by_mechanism"][
                "CAPTURE_EXPANSION"]="NEGATIVE_CHANGE_UNDER_ASSUMPTIONS"
            return subprocess.CompletedProcess(args[0],0,
                stdout=json.dumps(payload),stderr=result.stderr)
        monkeypatch.setattr(lab.subprocess,"run",divergent_node_response)
        ipc_drift=get("late")
        assert ipc_drift[0]==503
        assert ipc_drift[1]=="no-store"
        assert ipc_drift[2]=={"error":"SYNTHETIC_BRIDGE_UNAVAILABLE"}
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5)


def _bitemporal_actor_event_node(wire,cut="late"):
    """Invoke the existing actual JS warehouse CLI with Python fixture bytes."""
    from politics_fantasy.scientific_integration_lab import (
        _assets,_capture_rivals,_sha,FAKE_PARITY,CUTS,
        _partial_identification_fixture,
    )
    runner=Path(__file__).resolve().parents[1]/"scripts"/"scientific_integration_warehouse.mjs"
    experiment=_capture_rivals(CUTS["late"])[1] if cut=="late" else None
    return subprocess.run(["node",str(runner)],input=json.dumps({
        "cut":cut,"scenario":"baseline","sha256":_sha(FAKE_PARITY),
        "assets":_assets(),"experiment":experiment,"timeline":wire,
        "partial_identification":(
            _partial_identification_fixture() if cut=="late" else None),
    }),text=True,capture_output=True,timeout=5)


def test_bitemporal_actor_event_same_fixture_python_node_two_knowledge_cuts():
    """New capability, NOT a PREPATCH bug: identical source bytes and typed revisions."""
    from politics_fantasy.scientific_integration_lab import (
        _bitemporal_fixture,_bitemporal_actor_event,CUTS,_sha,
    )
    wire=_bitemporal_fixture()
    assert [s["sha256"] for s in wire["sources"]]==[
        _sha(s["text"]) for s in wire["sources"]]
    assert wire["events"][1]["amendment_of"]==wire["events"][0]["id"]
    assert wire["events"][0]["typed_key"]==wire["events"][1]["typed_key"]
    for cut in ("early","late"):
        python_result,_=_bitemporal_actor_event(at=CUTS[cut],wire=wire)
        node_result=_bitemporal_actor_event_node(wire,cut=cut)
        assert node_result.returncode==0,node_result.stderr
        node=json.loads(node_result.stdout)["bitemporal_actor_event_equivalence"]
        assert node==python_result
        api=report(cut=cut)
        assert api["warehouse"]["bitemporal_actor_event_equivalence"]==python_result
        assert api["R5"]=="STOP_R5"
        assert api["independent_all_received_denominator"] is None
        for key,expected in (("first_public_at_real",None),
                             ("rights_independently_verified",False),
                             ("source_crosswalk_certified",False),
                             ("independent_denominator",None),
                             ("real_actor_identity_verified",False),
                             ("empirical_event_count_admitted",False)):
            assert python_result[key] is expected


def test_bitemporal_actor_event_anti_lookahead_revision_and_validity_independent():
    early=report(cut="early")["warehouse"]["bitemporal_actor_event_equivalence"]
    late=report(cut="late")["warehouse"]["bitemporal_actor_event_equivalence"]
    assert (early["visible_source_receipts"],late["visible_source_receipts"])==(1,2)
    before,after="2026-09-15","2026-10-10"
    assert [early["views_by_valid_day"][d]["role_assertions_visible_at_valid_day"] for d in (before,after)]==[1,0]
    assert [late["views_by_valid_day"][d]["role_assertions_visible_at_valid_day"] for d in (before,after)]==[1,1]
    assert early["views_by_valid_day"][after]["role_observation_state"]=="NOT_OBSERVED"
    assert late["views_by_valid_day"][after]["role_observation_state"]=="OBSERVED"
    assert [early["views_by_valid_day"][d]["selected_revision"] for d in (before,after)]==["v1","v1"]
    assert [late["views_by_valid_day"][d]["selected_revision"] for d in (before,after)]==["v2","v2"]
    assert [early["views_by_valid_day"][d]["event_documentary_revisions_known"] for d in (before,after)]==[1,1]
    assert [late["views_by_valid_day"][d]["event_documentary_revisions_known"] for d in (before,after)]==[2,2]
    assert all(early["views_by_valid_day"][d]["actor_source_local_identity_count"]==1 and
               late["views_by_valid_day"][d]["actor_source_local_identity_count"]==1 and
               early["views_by_valid_day"][d]["logical_events_after_typed_amendment"]==1 and
               late["views_by_valid_day"][d]["logical_events_after_typed_amendment"]==1
               for d in (before,after))


@pytest.mark.parametrize("tamper,error",[
    ("sha_spoof","BITEMPORAL_SOURCE_BYTES_OR_SHA_MISMATCH"),
    ("issuer_spoof","BITEMPORAL_UNATTESTED_IDENTITY_OR_GATE"),
    ("source_id_spoof","BITEMPORAL_SOURCE_BYTES_OR_SHA_MISMATCH"),
    ("capture_in_future","BITEMPORAL_SOURCE_BYTES_OR_SHA_MISMATCH"),
    ("first_public_missing","BITEMPORAL_SOURCE_BYTES_OR_SHA_MISMATCH"),
    ("typed_key_missing","BITEMPORAL_TYPED_AMENDMENT_CROSSWALK_MISMATCH"),
    ("amendment_missing","BITEMPORAL_TYPED_AMENDMENT_CROSSWALK_MISMATCH"),
    ("fake_crosswalk_certified","BITEMPORAL_UNATTESTED_IDENTITY_OR_GATE"),
])
def test_bitemporal_actor_event_rejects_spoof_in_actual_node_and_python(tamper,error):
    from politics_fantasy.scientific_integration_lab import (
        _bitemporal_fixture,_bitemporal_actor_event,CUTS,
    )
    wire=json.loads(json.dumps(_bitemporal_fixture()))
    if tamper=="sha_spoof":
        wire["sources"][1]["sha256"]="0"*64
    elif tamper=="issuer_spoof":
        wire["issuer"]="SYN:OTHER_ISSUER"
    elif tamper=="source_id_spoof":
        wire["sources"][1]["source_id"]="SYN:WRONG_SOURCE"
    elif tamper=="capture_in_future":
        wire["sources"][1]["captured_at"]="2026-11-03T12:00:00Z"
    elif tamper=="first_public_missing":
        wire["sources"][1]["first_public_at"]=None
    elif tamper=="typed_key_missing":
        del wire["events"][1]["typed_key"]
    elif tamper=="amendment_missing":
        wire["events"][1]["amendment_of"]=None
    else:
        wire["source_crosswalk_certified"]=True
    with pytest.raises(RuntimeError,match=error):
        _bitemporal_actor_event(at=CUTS["late"],wire=wire)
    if shutil.which("node") is None:
        pytest.skip("Node not installed")
    observed=_bitemporal_actor_event_node(wire)
    assert observed.returncode!=0
    assert error in observed.stderr
    assert observed.stdout==""


def test_bitemporal_actor_event_http_aggregates_redacted_and_ipc_503(tmp_path,monkeypatch):
    """Real server -> Python TemporalLedger -> genuine Node -> redacted HTTP."""
    from politics_fantasy import scientific_integration_lab as lab
    server=ThreadingHTTPServer(("127.0.0.1",0),handler_factory(
        tmp_path/"synthetic-demo.sqlite",None,None))
    thread=Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        def request(cut):
            conn=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=5)
            conn.request("GET","/api/scientific-integration-lab?cut="+cut)
            res=conn.getresponse()
            status,cache=res.status,res.getheader("Cache-Control")
            body=json.loads(res.read());conn.close()
            return status,cache,body
        for cut in ("early","late"):
            status,cache,payload=request(cut)
            assert (status,cache)==(200,"no-store")
            summary=payload["warehouse"]["bitemporal_actor_event_equivalence"]
            assert summary["visible_source_receipts"]==(1 if cut=="early" else 2)
            assert summary["first_public_at_real"] is None
            assert summary["independent_denominator"] is None
            assert payload["R5"]=="STOP_R5"
            raw=json.dumps(payload)
            assert "SYN:CHRONICLE" not in raw
            assert "SYNTHETIC BITEMPORAL FIXTURE" not in raw
            for source in lab._bitemporal_fixture()["sources"]:
                assert source["sha256"] not in raw
        # Falsifier 1: real Node executes, but IPC stdout silently inflates
        # active roles for a given historical validity day. HTTP must be 503.
        genuine=lab.subprocess.run
        def mutated_node(*args,**kwargs):
            proc=genuine(*args,**kwargs)
            assert proc.returncode==0
            rows=json.loads(proc.stdout)
            rows["bitemporal_actor_event_equivalence"]["views_by_valid_day"][
                "2026-10-10"]["role_assertions_visible_at_valid_day"]=2
            return subprocess.CompletedProcess(args[0],0,
                stdout=json.dumps(rows),stderr=proc.stderr)
        monkeypatch.setattr(lab.subprocess,"run",mutated_node)
        assert request("late")==(
            503,"no-store",{"error":"SYNTHETIC_BRIDGE_UNAVAILABLE"})
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5)


def _s3_real_node(wire, *, cut="late"):
    """Actual existing Node program, not a mocked rational implementation."""
    from politics_fantasy.scientific_integration_lab import (
        _assets, _capture_rivals, _bitemporal_fixture, _sha, FAKE_PARITY, CUTS,
    )
    runner=Path(__file__).resolve().parents[1]/"scripts"/"scientific_integration_warehouse.mjs"
    experiment=_capture_rivals(CUTS["late"])[1] if cut=="late" else None
    return subprocess.run(["node",str(runner)],input=json.dumps({
        "cut":cut,"scenario":"baseline","sha256":_sha(FAKE_PARITY),
        "assets":_assets(),"experiment":experiment,
        "timeline":_bitemporal_fixture(),"partial_identification":wire,
    }),text=True,capture_output=True,timeout=5)


def test_s3_new_exact_partial_identification_python_node_and_http_projection():
    """S3 is a new noncausal, conditional sensitivity capability, not a bug fix."""
    from politics_fantasy.scientific_integration_lab import (
        _partial_identification, _partial_identification_fixture,
    )
    wire=_partial_identification_fixture()
    py=_partial_identification(wire)
    assert py["observed_positive_share"]=={"before":"3/5","after":"7/10"}
    assert py["selection_ratio_positive_to_negative"]=={"lower":"1/2","upper":"2/1"}
    assert py["prevalence_bounds"]=={
        "before":{"lower":"3/7","upper":"3/4"},
        "after":{"lower":"7/13","upper":"14/17"}}
    assert py["change_bounds"]=={"lower":"-11/52","upper":"47/119"}
    assert py["without_ratio_restriction"]=={
        "nontrivial_bounds_available":False,
        "trivial_change_closure":{"lower":"-1/1","upper":"1/1"}}
    assert py["documented_censor_witnesses"]=={"before":0,"after":0}
    assert py["observed_negative_is_administrative_failure"] is False
    assert py["first_public_at_real"] is None
    assert py["independent_registry_total"] is None
    assert py["rights_independently_verified"] is False
    assert py["causal_effect_identified"] is False
    assert py["empirical_estimand_admitted"] is False
    late=report(cut="late")
    early=report(cut="early")
    assert late["warehouse"]["partial_identification_oracle"]==py
    assert early["warehouse"]["partial_identification_oracle"] is None
    assert early["independent_all_received_denominator"] is None
    assert late["R5"]=="STOP_R5" and late["scientific_AB_cycles"]==0
    if shutil.which("node") is not None:
        p=_s3_real_node(wire)
        assert p.returncode==0,p.stderr
        assert json.loads(p.stdout)["partial_identification_oracle"]==py


def test_s3_observation_order_and_field_order_invariant_in_both_languages():
    from politics_fantasy.scientific_integration_lab import (
        _partial_identification, _partial_identification_fixture,
    )
    baseline=_partial_identification_fixture()
    reordered=json.loads(json.dumps(baseline))
    reordered["observations"]={k:dict(reversed(list(v.items()))) for k,v in
                               reversed(list(reordered["observations"].items()))}
    reordered={k:reordered[k] for k in reversed(list(reordered))}
    assert _partial_identification(reordered)==_partial_identification(baseline)
    if shutil.which("node") is not None:
        node=_s3_real_node(reordered)
        assert node.returncode==0,node.stderr
        assert json.loads(node.stdout)["partial_identification_oracle"]==(
            _partial_identification(baseline))


@pytest.mark.parametrize("change,error",[
    ("swap_ratio","S3_RATIO_RANGE_SPOOF_OR_SWAP"),
    ("spoof_ratio","S3_RATIO_RANGE_SPOOF_OR_SWAP"),
    ("denominator_spoof","S3_UNTRUSTED_REAL_SOURCE_OR_KNOWLEDGE_CUT"),
    ("rights_spoof","S3_UNTRUSTED_REAL_SOURCE_OR_KNOWLEDGE_CUT"),
    ("first_public_spoof","S3_UNTRUSTED_REAL_SOURCE_OR_KNOWLEDGE_CUT"),
    ("causal_claim","S3_UNTRUSTED_REAL_SOURCE_OR_KNOWLEDGE_CUT"),
    ("admin_negative_claim","S3_UNTRUSTED_REAL_SOURCE_OR_KNOWLEDGE_CUT"),
    ("observation_count_spoof","S3_BINARY_FRAME_MISMATCH"),
    ("censor_as_negative","S3_BINARY_FRAME_MISMATCH"),
])
def test_s3_new_wire_spoofs_fail_closed_python_and_independent_node(change,error):
    from politics_fantasy.scientific_integration_lab import (
        _partial_identification, _partial_identification_fixture,
    )
    wire=_partial_identification_fixture()
    if change=="swap_ratio":
        wire["selection_ratio_positive_to_negative"]={"lower":"2/1","upper":"1/2"}
    elif change=="spoof_ratio":
        wire["selection_ratio_positive_to_negative"]["upper"]="3/1"
    elif change=="denominator_spoof":
        wire["independent_registry_total"]=20
    elif change=="rights_spoof":
        wire["rights_independently_verified"]=True
    elif change=="first_public_spoof":
        wire["first_public_at_real"]="2026-09-01T12:00:00Z"
    elif change=="causal_claim":
        wire["causal_effect_claimed"]=True
    elif change=="admin_negative_claim":
        wire["administrative_negative_claimed"]=True
    elif change=="observation_count_spoof":
        wire["observations"]["before"]["observed_negative"]=5
    else:
        # A zero documented censor witness cannot be reclassified as a
        # counted negative administrative event or a known censored case.
        wire["observations"]["before"]["documented_censor_witnesses"]=4
    with pytest.raises(RuntimeError,match=error):
        _partial_identification(wire)
    if shutil.which("node") is not None:
        node=_s3_real_node(wire)
        assert node.returncode!=0
        assert error in node.stderr
        assert node.stdout==""


def test_s3_partial_identification_early_lookahead_is_rejected_by_node():
    from politics_fantasy.scientific_integration_lab import _partial_identification_fixture
    assert report(cut="early")["warehouse"]["partial_identification_oracle"] is None
    if shutil.which("node") is not None:
        injected=_s3_real_node(_partial_identification_fixture(),cut="early")
        assert injected.returncode!=0
        assert "S3_FUTURE_PARTIAL_IDENTIFICATION_AT_EARLY_CUT" in injected.stderr
        assert injected.stdout==""
        safe=_s3_real_node(None,cut="early")
        assert safe.returncode==0,safe.stderr
        assert json.loads(safe.stdout)["partial_identification_oracle"] is None


def test_s3_ratio_math_drift_from_real_node_forces_http_503(tmp_path,monkeypatch):
    """Compute real Node output, mutate ONLY its rational answer, then HTTP 503."""
    from politics_fantasy import scientific_integration_lab as lab
    server=ThreadingHTTPServer(("127.0.0.1",0),handler_factory(
        tmp_path/"synthetic-demo.sqlite",None,None))
    thread=Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        def request(cut):
            conn=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=5)
            conn.request("GET","/api/scientific-integration-lab?cut="+cut)
            reply=conn.getresponse()
            status,cache=reply.status,reply.getheader("Cache-Control")
            body=json.loads(reply.read());conn.close()
            return status,cache,body
        early=request("early")
        late=request("late")
        assert (early[0],early[1])==(200,"no-store")
        assert early[2]["warehouse"]["partial_identification_oracle"] is None
        assert (late[0],late[1])==(200,"no-store")
        oracle=late[2]["warehouse"]["partial_identification_oracle"]
        assert oracle["change_bounds"]=={"lower":"-11/52","upper":"47/119"}
        serialized=json.dumps(late[2]).lower()
        assert "synthetic_binary" not in serialized  # No row-level binary data.
        assert "observed_negative_is_administrative_failure\": false" in serialized
        assert late[2]["independent_all_received_denominator"] is None
        assert late[2]["R5"]=="STOP_R5"
        actual=lab.subprocess.run
        def drifted_rational_stdout(*args,**kwargs):
            result=actual(*args,**kwargs)
            assert result.returncode==0,result.stderr
            body=json.loads(result.stdout)
            body["partial_identification_oracle"]["change_bounds"]["lower"]="-10/52"
            return subprocess.CompletedProcess(args[0],0,
                stdout=json.dumps(body),stderr=result.stderr)
        monkeypatch.setattr(lab.subprocess,"run",drifted_rational_stdout)
        assert request("late")==(
            503,"no-store",{"error":"SYNTHETIC_BRIDGE_UNAVAILABLE"})
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5)


@pytest.mark.parametrize("corrupted_field,wrong_value", [
    ("censor_count", False),
    ("rights_boolean", 0),
])
def test_s3_node_ipc_boolean_integer_type_confusion_must_fail_closed_prepatch(
        tmp_path, monkeypatch, corrupted_field, wrong_value):
    """New genuine Node→HTTP falsifier: JSON 0 and false are distinct types.

    Python dict equality treats bool as int, so an untrusted Node oracle can
    otherwise pass its exact-value comparison while breaking the wire schema.
    These are two variants of ONE IPC type-confusion defect, not two new bugs.
    """
    from politics_fantasy import scientific_integration_lab as lab
    real_node = lab.subprocess.run

    def alter_stdout_after_real_node(*args, **kwargs):
        result = real_node(*args, **kwargs)
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        s3 = payload["partial_identification_oracle"]
        assert s3 is not None
        if corrupted_field == "censor_count":
            assert s3["documented_censor_witnesses"]["before"] == 0
            s3["documented_censor_witnesses"]["before"] = wrong_value
        else:
            assert s3["rights_independently_verified"] is False
            s3["rights_independently_verified"] = wrong_value
        return subprocess.CompletedProcess(args[0], 0,
                                           stdout=json.dumps(payload),
                                           stderr=result.stderr)

    monkeypatch.setattr(lab.subprocess, "run", alter_stdout_after_real_node)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_factory(
        tmp_path / "synthetic-demo.sqlite", None, None))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
        conn.request("GET", "/api/scientific-integration-lab?cut=late")
        response = conn.getresponse()
        status = response.status
        cache = response.getheader("Cache-Control")
        body = json.loads(response.read())
        conn.close()
        assert (status, cache, body) == (
            503, "no-store", {"error": "SYNTHETIC_BRIDGE_UNAVAILABLE"})
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)


@pytest.mark.parametrize("field,invalid", [
    ("negative_as_boolean", True),
    ("pending_as_float", 2.0),
])
def test_followup_structurally_equal_but_json_type_invalid_must_fail_prepatch(
        field, invalid):
    """New material PREPATCH falsifier, distinct from the fixed S3 IPC bug.

    Both source contracts are valid until the procedural aggregate is altered:
    Python's `dict ==` incorrectly regards True as 1 and 2.0 as 2.
    """
    from politics_fantasy.scientific_integration_lab import (
        _assets, _temporal, _procedural, _reconcile_followup, CUTS,
    )
    _,snapshot,receipts=_temporal(_assets(),at=CUTS["late"])
    procedural,episodes=_procedural(CUTS["late"])
    forged=json.loads(json.dumps(procedural))
    if field=="negative_as_boolean":
        assert forged["terminal_by_cause"]["INADMITTED"]==1
        forged["terminal_by_cause"]["INADMITTED"]=invalid
    else:
        assert forged["observed_pending_at_last_witness"]==2
        forged["observed_pending_at_last_witness"]=invalid
    with pytest.raises(RuntimeError,match="FOLLOWUP_CUT_MISMATCH"):
        _reconcile_followup(snapshot=snapshot,episodes=episodes,
                            procedural=forged,receipts=receipts)


@pytest.mark.parametrize("field,invalid", [
    ("negative_as_boolean", True),
    ("pending_as_float", 2.0),
])
def test_followup_type_drift_must_fail_closed_actual_http_prepatch(
        tmp_path,monkeypatch,field,invalid):
    """Actual local HTTP consumer and real Node, no client-submitted originals."""
    from politics_fantasy import scientific_integration_lab as lab
    actual=lab._procedural
    def falsified_procedure(at):
        result,episodes=actual(at)
        result=json.loads(json.dumps(result))
        if field=="negative_as_boolean":
            result["terminal_by_cause"]["INADMITTED"]=invalid
        else:
            result["observed_pending_at_last_witness"]=invalid
        return result,episodes
    monkeypatch.setattr(lab,"_procedural",falsified_procedure)
    server=ThreadingHTTPServer(("127.0.0.1",0),handler_factory(
        tmp_path/"synthetic-demo.sqlite",None,None))
    thread=Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        conn=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=5)
        conn.request("GET","/api/scientific-integration-lab?cut=late")
        response=conn.getresponse()
        status,cache=response.status,response.getheader("Cache-Control")
        payload=json.loads(response.read());conn.close()
        assert (status,cache,payload)==(
            503,"no-store",{"error":"SYNTHETIC_BRIDGE_UNAVAILABLE"})
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5)


def _typed_institutional_chain_real_node(wire,cut="late"):
    """The unchanged Node executable, with all *other* established fixtures."""
    from politics_fantasy.scientific_integration_lab import (
        _assets,_capture_rivals,_bitemporal_fixture,
        _partial_identification_fixture,_sha,FAKE_PARITY,CUTS,
    )
    runner=Path(__file__).resolve().parents[1]/"scripts"/"scientific_integration_warehouse.mjs"
    return subprocess.run(["node",str(runner)],input=json.dumps({
        "cut":cut,"scenario":"baseline","sha256":_sha(FAKE_PARITY),
        "assets":_assets(),"experiment":(
            _capture_rivals(CUTS["late"])[1] if cut=="late" else None),
        "timeline":_bitemporal_fixture(),
        "partial_identification":(
            _partial_identification_fixture() if cut=="late" else None),
        "chain":wire,
    }),text=True,capture_output=True,timeout=5)


def test_typed_institutional_chain_is_new_noncycle_five_family_replay():
    """New capability, not a prepatch defect: exactly one authored case."""
    from politics_fantasy.scientific_integration_lab import (
        _typed_institutional_chain,_typed_institutional_chain_fixture,
        CUTS,_sha,
    )
    wire=_typed_institutional_chain_fixture()
    assert [s["sha256"] for s in wire["sources"]]==[
        _sha(s["text"]) for s in wire["sources"]]
    assert wire["typed_keys"]["actor"]!=wire["typed_keys"]["organization"]
    assert wire["typed_keys"]["communication"]!=wire["typed_keys"]["decision"]
    assert wire["typed_keys"]["process"] not in (
        wire["typed_keys"]["communication"],wire["typed_keys"]["decision"])
    assert wire["communications"][1]["amendment_of"]==wire["communications"][0]["id"]
    assert wire["decision"]["amendment_of"] is None
    assert wire["process"]["entry_sha256"]==wire["sources"][0]["sha256"]
    assert wire["process"]["approval"]["source_sha256"]==wire["sources"][1]["sha256"]
    for cut in ("early","late"):
        py,_=_typed_institutional_chain(at=CUTS[cut],wire=wire)
        assert py["schema"]=="pfl.synthetic_typed_institutional_chain_oracle.v1"
        assert py["visible_source_receipts"]==(1 if cut=="early" else 2)
        assert py["same_fixture_source_sha_checked"] is True
        assert py["typed_cross_family_links_checked"] is True
        for flag in ("source_asset_rights_admitted","public_display_purpose_admitted",
                     "real_actor_identity_verified","real_decision_outcome_attested",
                     "real_censoring_attested","empirical_estimand_admitted"):
            assert py[flag] is False
        assert py["first_public_at_real"] is None
        assert py["independent_denominator"] is None
        if shutil.which("node") is not None:
            node=_typed_institutional_chain_real_node(wire,cut)
            assert node.returncode==0,node.stderr
            assert json.loads(node.stdout)["typed_institutional_chain"]==py
        api=report(cut=cut)
        assert api["warehouse"]["typed_institutional_chain"]==py
        assert api["scientific_AB_cycles"]==0
        assert api["independent_all_received_denominator"] is None
        assert api["R5"]=="STOP_R5"


def test_typed_institutional_chain_knowledge_and_valid_day_do_not_collide():
    early=report(cut="early")["warehouse"]["typed_institutional_chain"]
    late=report(cut="late")["warehouse"]["typed_institutional_chain"]
    pre="2026-09-11";post="2026-09-15"
    assert early["views_by_valid_day"][pre]["logical_decisions"]==0
    assert early["views_by_valid_day"][post]["logical_decisions"]==0
    assert late["views_by_valid_day"][pre]["logical_decisions"]==0
    assert late["views_by_valid_day"][post]["logical_decisions"]==1
    assert early["views_by_valid_day"][post]["process_state"]=="PENDING_AS_OF_EVIDENCE"
    assert late["views_by_valid_day"][post]["process_state"]=="APPROVED_AS_OF_EVIDENCE"
    assert late["views_by_valid_day"][pre]["process_state"]=="UNKNOWN_FOLLOWUP"
    for result in (early,late):
        for day in (pre,post):
            view=result["views_by_valid_day"][day]
            assert (view["actor_visible"],view["organization_visible"],
                    view["process_episode_visible"],view["logical_communications"])==(1,1,1,1)
            assert view["negative_decisions"]==view["censor_witnesses"]==0
            assert view["communication_documentary_revisions_known"]==(
                1 if result is early else 2)
    assert all(late["views_by_valid_day"][day]["logical_communications"]==1
               for day in (pre,post))  # Two revisions are not two events.
    assert early["views_by_valid_day"][post]["pending_not_negative"]==1
    assert late["views_by_valid_day"][post]["pending_not_negative"]==0


@pytest.mark.parametrize("tamper,error",[
    ("source_sha_spoof","CHAIN_SOURCE_RECEIPT_MISMATCH"),
    ("source_id_spoof","CHAIN_SOURCE_RECEIPT_MISMATCH"),
    ("capture_lookahead","CHAIN_SOURCE_RECEIPT_MISMATCH"),
    ("semantic_communication_as_decision","CHAIN_TYPED_SOURCE_LINK_MISMATCH"),
    ("decision_as_communication","CHAIN_TYPED_SOURCE_LINK_MISMATCH"),
    ("communication_as_second_decision","CHAIN_TYPED_SOURCE_LINK_MISMATCH"),
    ("process_approval_wrong_sha","CHAIN_TYPED_SOURCE_LINK_MISMATCH"),
    ("process_wrong_typed_key","CHAIN_TYPED_SOURCE_LINK_MISMATCH"),
    ("rights_spoof","CHAIN_RIGHTS_FRAME_OR_ISSUER_PROMOTION"),
    ("denominator_spoof","CHAIN_RIGHTS_FRAME_OR_ISSUER_PROMOTION"),
    ("first_public_real_spoof","CHAIN_RIGHTS_FRAME_OR_ISSUER_PROMOTION"),
])
def test_typed_institutional_chain_fake_source_or_role_rejected_both_engines(tamper,error):
    from politics_fantasy.scientific_integration_lab import (
        _typed_institutional_chain,_typed_institutional_chain_fixture,CUTS,
    )
    wire=json.loads(json.dumps(_typed_institutional_chain_fixture()))
    if tamper=="source_sha_spoof":
        wire["sources"][1]["sha256"]="0"*64
    elif tamper=="source_id_spoof":
        wire["sources"][1]["source_id"]="SYN:OTHER_V2"
    elif tamper=="capture_lookahead":
        wire["sources"][1]["captured_at"]="2026-11-03T12:00:00Z"
    elif tamper=="semantic_communication_as_decision":
        wire["communications"][0]["kind"]="DECISION"
    elif tamper=="decision_as_communication":
        wire["decision"]["kind"]="COMMUNICATION"
    elif tamper=="communication_as_second_decision":
        wire["communications"][1]["process_key"]=wire["typed_keys"]["decision"]
    elif tamper=="process_approval_wrong_sha":
        wire["process"]["approval"]["source_sha256"]="f"*64
    elif tamper=="process_wrong_typed_key":
        wire["process"]["typed_key"]=wire["typed_keys"]["decision"]
    elif tamper=="rights_spoof":
        wire["rights_by_asset_purpose_admitted"]=True
    elif tamper=="denominator_spoof":
        wire["independent_denominator"]=1
    else:
        wire["first_public_at_real"]="2026-09-01T00:00:00Z"
    with pytest.raises(RuntimeError,match=error):
        _typed_institutional_chain(at=CUTS["late"],wire=wire)
    if shutil.which("node") is not None:
        node=_typed_institutional_chain_real_node(wire)
        assert node.returncode!=0
        assert error in node.stderr
        assert node.stdout==""


def test_typed_institutional_chain_real_http_redacts_and_503_on_node_drift(
        tmp_path,monkeypatch):
    """Actual loopback server, real Node computation, synthetic-only IPC drift."""
    from politics_fantasy import scientific_integration_lab as lab
    server=ThreadingHTTPServer(("127.0.0.1",0),handler_factory(
        tmp_path/"synthetic-demo.sqlite",None,None))
    thread=Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        def get(cut):
            conn=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=5)
            conn.request("GET","/api/scientific-integration-lab?cut="+cut)
            response=conn.getresponse()
            status,cache=response.status,response.getheader("Cache-Control")
            body=json.loads(response.read());conn.close()
            return status,cache,body
        for cut in ("early","late"):
            status,cache,payload=get(cut)
            assert (status,cache)==(200,"no-store")
            chain=payload["warehouse"]["typed_institutional_chain"]
            assert chain["source_asset_rights_admitted"] is False
            assert chain["first_public_at_real"] is None
            assert chain["independent_denominator"] is None
            assert payload["pp04"] is None if cut=="early" else payload["pp04"]["not_included_4221_excluded"] is True
            raw=json.dumps(payload)
            for source in lab._typed_institutional_chain_fixture()["sources"]:
                assert source["sha256"] not in raw
                assert source["text"] not in raw
                assert source["source_id"] not in raw
            assert "SYNTHETIC:CHAIN_EPISODE1" not in raw
            assert "SYN:CHAIN_COMM" not in raw
            assert "SYN:CHAIN_DEC" not in raw
        genuine=lab.subprocess.run
        def corrupt_node_after_actual_run(*args,**kwargs):
            produced=genuine(*args,**kwargs)
            assert produced.returncode==0,produced.stderr
            response=json.loads(produced.stdout)
            response["typed_institutional_chain"]["views_by_valid_day"][
                "2026-09-15"]["logical_decisions"]=2
            return subprocess.CompletedProcess(args[0],0,
                stdout=json.dumps(response),stderr=produced.stderr)
        monkeypatch.setattr(lab.subprocess,"run",corrupt_node_after_actual_run)
        assert get("late")==(
            503,"no-store",{"error":"SYNTHETIC_BRIDGE_UNAVAILABLE"})
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5)
