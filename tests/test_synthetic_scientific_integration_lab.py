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
    from politics_fantasy.scientific_integration_lab import _assets, _sha, FAKE_PARITY
    node=Path(__file__).resolve().parents[1]/"scripts"/"scientific_integration_warehouse.mjs"
    return subprocess.run(["node",str(node)],input=json.dumps({
        "cut":cut,"scenario":"baseline","sha256":_sha(FAKE_PARITY),
        "assets":_assets(),"experiment":experiment,
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
    assert oracle["opposed_synthetic_trend_signs"] is True
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
    ("opposite_trend_falsified","RIVAL_MECHANISM_OR_TREND_MISMATCH"),
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
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5)
