"""One executable PP04→rights→SHA→time→process→rivals→Node→HTTP lab.

ALL records, actors, issuers, dates and documents in this file are invented.
No original access, URL fetching, file ingestion, user input, person scoring,
empirical estimand or R5 admission exists here. Report only safe aggregates.

This is deliberately a server-owned fixture, NOT an adapter for uploaded data:
the contracts do not yet authenticate real publishers, vintage publication,
rights by purpose, a complete at-risk registry, or original case crosswalks.
"""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess

from .denominator_lineage_contract import (
    PopulationTarget, SourceTotalClaim, compare_total_claims,
)
from .pan_iaen_cross_parser_audit import audit_pp04_dual_parsers
from .procedural_stage_accounting import (
    EntryEpisode, StageAct, PendingWitness, TERMINAL, audit_lab, safe,
)
from .procedural_index_contract import utc, day, legal_civil_date
from .r5_asset_rights_gate import assess_distribution_rights
from .synthetic_institutional_demo import report as institutional_report
from .synthetic_regime_capture_sensitivity import (
    FictionalCaptureStratum, audit_regime_capture, compare_capture_hypotheses,
)
from .temporal_evidence import FileReceipt, SourceRef, Snapshot, TemporalLedger, TemporalRecord


CUTS = {
    "early": "2026-10-15T12:00:00Z",
    "late": "2026-11-01T12:00:00Z",
}
SCENARIOS = frozenset({"baseline", "rights_spoof", "privacy_probe"})
SYNTHETIC_FOLLOWUP_CROSSWALK = {
    # Exact, server-owned demonstration of a 1:1 documentary link. In a
    # real corpus this requires independently authenticated official IDs.
    ("SYNTHETIC_PROCESS", "PROCESS", "ENTRY4", "FOLLOWUP_END_FOR_ENTRY4"):
        "SYNTHETIC:ENTRY4",
}
EARLY_CAPTURE = "2026-09-20T12:00:00Z"
LATE_CAPTURE = "2026-10-31T12:00:00Z"
LATE_PUBLIC = "2026-10-30T12:00:00Z"  # INVENTED first publication
FAKE_PARITY = b"PFL_SYNTHETIC_SCIENTIFIC_INTEGRATION_V1\n"

PAN_TEXT = (
    "SYNTHETIC DOCUMENT FIXTURE\n"
    "REAL DECRETO A\nObjetivo: alfa\nMinisterio: A\n"
    "LEY B\nObjetivo: beta\nMinisterio: B\n"
)
IAEN_TEXT = (
    "SYNTHETIC DOCUMENT FIXTURE\n"
    "4.1.- DEPARTAMENTO A\n"
    "4.1.1.- INICIATIVAS NORMATIVAS INCLUIDAS EN EL PLAN ANUAL\n"
    "I. Aprobadas\n- Real Decreto alfa.\n"
    "II. Pendientes de aprobación\n- Ley beta.\n"
    "4.1.2.- NORMAS NO INCLUIDAS EN EL PLAN ANUAL\n"
    "- Real Decreto externo.\n"
    "4.22.- DEPARTAMENTO VIVIENDA\n"
    "4.22.1.- NORMAS NO INCLUIDAS EN EL PLAN ANUAL\n"
    "- Real Decreto externo 2.\n"
    "5. REALES DECRETOS-LEYES\n"
)


def _sha(text: str | bytes) -> str:
    body = text.encode("utf-8") if isinstance(text, str) else text
    return hashlib.sha256(body).hexdigest()


def _assets() -> list[dict]:
    return [
        {"id": "SYNTHETIC:PAN24", "text": PAN_TEXT, "sha256": _sha(PAN_TEXT)},
        {"id": "SYNTHETIC:IAEN24", "text": IAEN_TEXT, "sha256": _sha(IAEN_TEXT)},
    ]


def _rights(assets: list[dict], *, at: str) -> dict:
    results = {}
    for asset in assets:
        rights = {"kind": "PUBLISHER_ASSET_SPECIFIC",
                  "distribution_id": asset["id"],
                  "asset_sha256": asset["sha256"],
                  "covered_purposes": ["LOCAL_ACADEMIC_READ"],
                  "notice_published_at": LATE_PUBLIC,
                  "terms_mode": "PUBLISHER_OPEN_NOTICE",
                  "terms_reviewed_by_human": True,
                  "rights_reviewed_by_human": True}
        # Even the best-looking analyst-asserted record has NO independent
        # legal/publisher attestation. Public display is not local reading.
        verdict = assess_distribution_rights({
            "distribution_id": asset["id"],
            "asset_url": "https://example.invalid/synthetic-asset-absent",
            "asset_sha256": asset["sha256"],
            "requested_purpose": "PUBLIC_AGGREGATE_DISPLAY",
            "historical_as_of": at,
            "first_public_at": LATE_PUBLIC,
            "rights": rights,
        })
        if verdict["reuse_admitted"] or verdict["empirical_r5_open"]:
            raise RuntimeError("UNTRUSTED_ASSET_RIGHTS_PROMOTED")
        results[asset["id"]] = {
            "status": verdict["status"], "reasons": verdict["reasons"],
            "asset_sha256": asset["sha256"],
            "distribution_id": asset["id"],
            "reuse_admitted": False,
        }
    return {"reuse_admitted": False, "real_originals_approved": False,
            "purpose": "PUBLIC_AGGREGATE_DISPLAY", "per_asset": results,
            "independent_attestation": False}


def _temporal(assets: list[dict], *, at: str
              ) -> tuple[dict, Snapshot, dict[tuple[str,str], FileReceipt]]:
    ledger = TemporalLedger()
    receipts = {}
    for asset in assets:
        # The original source namespace is valid in TemporalLedger. Rewriting
        # punctuation would manufacture an unauthenticated source-id crosswalk.
        source_id = asset["id"]
        # SHA of the SAME exact synthetic bytes compared by the two PP04
        # parsers and again by Node. This is a local binding, not authenticity.
        receipt=FileReceipt(source_id, asset["sha256"],
            len(asset["text"].encode("utf-8")), LATE_CAPTURE,
            "SYNTHETIC", "SYNTHETIC")
        ledger.register_source(receipt)
        receipts[(receipt.source_id,receipt.sha256)] = receipt
        ledger.add(TemporalRecord(
            kind="ENTITY", source_id=source_id,
            source_record_id="DOCUMENTARY_FRAME", revision="v1",
            source_sha256=asset["sha256"],
            subject=SourceRef(source_id, "DOC", "FRAME"),
            predicate="SOURCE_LOCAL_DOCUMENTARY_POPULATION", object=None,
            valid_from="2026-09-01T00:00:00Z", valid_to=None,
            first_public_at=LATE_PUBLIC, recorded_at=LATE_CAPTURE,
            observation_state="OBSERVED", value="DOCUMENTED_ONLY"))
    subject = SourceRef("SYNTHETIC_PROCESS", "INSTITUTION", "ORG_A")
    for revision, captured, published in (
        ("v1", EARLY_CAPTURE, "2026-09-19T12:00:00Z"),
        ("v2", LATE_CAPTURE, LATE_PUBLIC),
    ):
        body = f"SYNTHETIC_PROCESS_{revision}\n".encode("utf-8")
        digest = _sha(body)
        receipt=FileReceipt("SYNTHETIC_PROCESS",digest,
            len(body),captured,"SYNTHETIC","SYNTHETIC")
        ledger.register_source(receipt)
        receipts[(receipt.source_id,receipt.sha256)] = receipt
        ledger.add(TemporalRecord(kind="ENTITY",source_id="SYNTHETIC_PROCESS",
            source_record_id="INSTITUTIONAL_STATUS",revision=revision,
            source_sha256=digest,subject=subject,predicate="ADMINISTRATIVE_REVISION",
            object=None,valid_from="2026-09-01T00:00:00Z",valid_to=None,
            first_public_at=published,recorded_at=captured,
            observation_state="OBSERVED",value=revision))
        if revision == "v2":
            # An explicitly INVENTED follow-up-end witness belongs to the
            # procedural process, not to a demonstrated outcome. It may
            # distinguish censoring from missingness in a synthetic example,
            # but cannot replace proof of the real observation mechanism.
            ledger.add(TemporalRecord(
                kind="EVENT",source_id="SYNTHETIC_PROCESS",
                source_record_id="FOLLOWUP_END_FOR_ENTRY4",revision="v1",
                source_sha256=digest,
                subject=SourceRef("SYNTHETIC_PROCESS","PROCESS","ENTRY4"),
                predicate="OBSERVATION_WINDOW_ENDED_WITHOUT_DECISION",
                object=None,valid_from="2026-09-15T00:00:00Z",valid_to=None,
                first_public_at=LATE_PUBLIC,recorded_at=LATE_CAPTURE,
                observation_state="OBSERVED",value="CENSORED_IN_SYNTHETIC_FIXTURE"))
    snapshot=ledger.snapshot(as_of=at,valid_at=at)
    # Multiple typed records from one process source are NOT multiple
    # revisions of one logical assertion. Select by exact typed record key.
    versions=[r.revision for r in snapshot.records
              if r.kind=="ENTITY" and r.source_id=="SYNTHETIC_PROCESS"
              and r.source_record_id=="INSTITUTIONAL_STATUS"]
    if len(versions)!=1:
        raise RuntimeError("TEMPORAL_REVISION_AMBIGUOUS")
    visible_asset_ids=[r.source_id for r in snapshot.records
                       if r.predicate=="SOURCE_LOCAL_DOCUMENTARY_POPULATION"]
    if (len(set(visible_asset_ids)) != len(visible_asset_ids)
            or set(visible_asset_ids)-{asset["id"] for asset in assets}):
        raise RuntimeError("PP04_SOURCE_IDENTITY_MISMATCH")
    ordered_asset_ids=[asset["id"] for asset in assets
                       if asset["id"] in visible_asset_ids]
    return {"revision_visible": versions[0],
            "pp04_asset_receipts_visible":sum(
                r.predicate=="SOURCE_LOCAL_DOCUMENTARY_POPULATION"
                for r in snapshot.records),
            "pp04_source_ids_seen":ordered_asset_ids,
            "synthetic_followup_end_witnesses":sum(
                r.predicate=="OBSERVATION_WINDOW_ENDED_WITHOUT_DECISION"
                for r in snapshot.records),
            "unknown_publication_blocked":snapshot.blocked_unknown_publication,
            "unadjudicated_real_blocked":snapshot.blocked_unadjudicated_source,
            "scientific_grade":snapshot.scientific_grade,
            "real_person_scoring":snapshot.real_person_scoring}, snapshot, receipts


def _population_target(*, unit: str) -> PopulationTarget:
    return PopulationTarget(
        institution="SYNTHETIC_INSTITUTION", family="SYNTHETIC_COMPLAINTS",
        legislature_or_regime="SYNTHETIC_REGIME",entry_rule="ALL_RECEIVED_REGISTRATION",
        unit=unit,window_first_day="2026-09-01",window_last_day="2026-09-10",
        jurisdiction="SYNTHETIC_MADRID",channel_scope="SYNTHETIC_ALL_CHANNELS",
        legal_calendar_zone="Europe/Madrid")


def _procedural(at: str) -> tuple[dict, tuple[EntryEpisode, ...]]:
    frame = _population_target(unit="REGISTRY_INITIAL_WRITING")
    sha = _sha(b"SYNTHETIC_STAGE_DOCUMENT\n")
    def ep(n: int, channel: str, *, acts: tuple = (), pending: tuple = ()):
        return EntryEpisode(
            episode_id=f"SYNTHETIC:ENTRY{n}",frame=frame,
            entry_on=f"2026-09-0{n}",entry_observed_at=EARLY_CAPTURE,
            entry_sha_claim=sha,channel=channel,acts=acts,pending=pending)
    def act(kind: str):
        return StageAct(stage=kind,occurred_on="2026-09-11",
                        documented_on="2026-09-12",observed_at=LATE_CAPTURE,
                        document_sha_claim=sha,legal_calendar_zone="Europe/Madrid")
    def pend(captured: str):
        return PendingWitness(pending_on="2026-09-12",observed_at=captured,
            document_sha_claim=sha,legal_calendar_zone="Europe/Madrid")
    episodes=(ep(1,"PAPER",acts=(act("APPROVED"),)),
              ep(2,"ELECTRONIC",acts=(act("INADMITTED"),)),
              ep(3,"PAPER",pending=(pend(EARLY_CAPTURE),)),
              ep(4,"ELECTRONIC"),
              ep(5,"PAPER",pending=(pend(LATE_CAPTURE),)))
    return audit_lab(frame=frame,episodes=episodes,as_of=at), episodes


def _reconcile_followup(*, snapshot: Snapshot,
                        episodes: tuple[EntryEpisode, ...],
                        procedural: dict,
                        receipts: dict[tuple[str,str],FileReceipt]) -> dict:
    """Join only exact fixture episode IDs to RECEIPT-BOUND temporal events.

    A termination of observation is NOT an unsuccessful administrative
    decision. TemporalLedger has already checked source+SHA+capture for each
    visible event; audit_lab independently preserves its original unknowns.
    This additional derived view never changes that source-local audit.
    """
    if not isinstance(snapshot, Snapshot) or not isinstance(procedural, dict):
        raise RuntimeError("SYNTHETIC_FOLLOWUP_CONTRACT_REQUIRED")
    t=utc(snapshot.as_of)
    frame_ids = {e.episode_id for e in episodes}
    if len(frame_ids) != len(episodes) or not frame_ids:
        raise RuntimeError("DUPLICATE_OR_EMPTY_SYNTHETIC_EPISODE_FRAME")
    # A source-local stage report deliberately does not expose as_of. The
    # assembly boundary must therefore REPLAY the original contract against
    # the ledger's own knowledge horizon, rather than combining unrelated
    # individually-valid aggregates (e.g. late censor + early pending/unknown).
    reconstructed = audit_lab(frame=episodes[0].frame, episodes=episodes,
                              as_of=snapshot.as_of)
    if reconstructed != procedural:
        raise RuntimeError("FOLLOWUP_CUT_MISMATCH")
    claims = [r for r in snapshot.records
              if r.predicate == "OBSERVATION_WINDOW_ENDED_WITHOUT_DECISION"]
    seen = set()
    for claim in claims:
        receipt=receipts.get((claim.source_id,claim.source_sha256))
        if (not isinstance(receipt,FileReceipt)
                or receipt.origin!="SYNTHETIC"
                or receipt.rights_state!="SYNTHETIC"):
            raise RuntimeError("CENSOR_SOURCE_RECEIPT_BINDING_MISMATCH")
        if (claim.kind != "EVENT" or claim.source_id != "SYNTHETIC_PROCESS"
                or claim.subject.authority != "SYNTHETIC_PROCESS"
                or claim.subject.family != "PROCESS"
                or claim.observation_state != "OBSERVED"
                or claim.value != "CENSORED_IN_SYNTHETIC_FIXTURE"
                or claim.first_public_at is None):
            raise RuntimeError("UNATTESTED_OR_UNBOUND_SYNTHETIC_CENSOR_CLAIM")
        # No heuristic stripping of prefixes or coincident ID suffixes.
        episode_id = SYNTHETIC_FOLLOWUP_CROSSWALK.get((
            claim.subject.authority,claim.subject.family,
            claim.subject.local_id,claim.source_record_id))
        episode = next((e for e in episodes if e.episode_id == episode_id), None)
        # `audit_lab` filters by the exact observation-time cutoff. Applying
        # a timeless `if episode.acts or episode.pending` here caused future
        # documents to invalidate an earlier, already visible censor witness.
        # Mere ADMITTED/HEARD steps are also NOT terminal decisions.
        observed_terminal = episode is not None and any(
            a.stage in TERMINAL and safe(a.observed_at) <= t
            for a in episode.acts)
        observed_pending = episode is not None and any(
            safe(p.observed_at) <= t and
            day(p.pending_on) <= legal_civil_date(
                snapshot.as_of, episode.frame.legal_calendar_zone)
            for p in episode.pending)
        if (episode_id in seen or episode is None
                or claim.valid_from[:10] < episode.entry_on
                or observed_terminal or observed_pending):
            raise RuntimeError("CENSOR_WITNESS_EPISODE_LINK_INVALID")
        seen.add(episode_id)
    unknown = procedural.get("unknown_followup")
    if (type(unknown) is not int or unknown < len(seen)
            or procedural.get("all_received_denominator") is not None):
        raise RuntimeError("INCOMPATIBLE_OR_PROMOTED_PROCEDURAL_COUNTS")
    negatives = procedural.get("terminal_by_cause") or {}
    return {
        "schema": "pfl.synthetic_followup_reconciliation.v1",
        "explicit_censor_witnesses": len(seen),
        "unknown_without_censor_witness": unknown - len(seen),
        "pending_not_censoring": procedural["observed_pending_at_last_witness"],
        "negative_outcomes_not_censoring": negatives.get("INADMITTED", 0),
        # Only the temporal event's *fictional* FileReceipt was checked by
        # TemporalLedger. The stage acts contain mere SHA claims: do not
        # describe them as independently authenticated evidence.
        "temporal_witness_fixture_receipt_checked": bool(seen),
        "stage_documents_authenticated": False,
        "real_censoring_attested": False,
    }


def _denominator(at: str) -> dict:
    # Neither claim derives from PP04: its planned items are NOT intake
    # records. This deliberately demonstrates non-comparable administrative
    # units, not an unsuccessful attempt to join its two equal 2/2 counts.
    first = SourceTotalClaim(
        source_id="SYNTHETIC:REGISTRY",target=_population_target(
            unit="REGISTRY_INITIAL_WRITING"),reported_count=5,
        reporting_issuer="SYNTHETIC_ISSUER_A",backend_lineage="SYNTHETIC_DB_A",
        claim_basis="REGISTRY_PUBLISHED_TOTAL",
        locally_documented_safe_by=EARLY_CAPTURE)
    second = SourceTotalClaim(
        source_id="SYNTHETIC:INDEX",target=_population_target(
            unit="PUBLISHED_EXPEDIENTE"),reported_count=5,
        reporting_issuer="SYNTHETIC_ISSUER_B",backend_lineage="SYNTHETIC_DB_B",
        claim_basis="EDITORIAL_PAGE_COUNT",
        locally_documented_safe_by=LATE_CAPTURE)
    return compare_total_claims(first=first,second=second,
        query_as_of=at,locally_known_safe_by=EARLY_CAPTURE)


def _capture_rivals(at: str) -> dict:
    def cells(pre: Fraction,post: Fraction):
        def cell(regime,channel,count):
            before=regime=="BEFORE_REFORM"
            return FictionalCaptureStratum(
                fixture_id=f"SYNTHETIC:{regime}:{channel}",
                regime=regime,channel=channel,
                first_day="2026-09-01" if before else "2026-10-01",
                last_day="2026-09-30" if before else "2026-10-30",
                locally_captured_at=LATE_CAPTURE,observed_published=count,
                assumed_min_capture_share=pre if before else post,
                assumed_max_capture_share=pre if before else post,
                legal_calendar_zone="Europe/Madrid")
        return (cell("BEFORE_REFORM","PAPER",8),
                cell("BEFORE_REFORM","ELECTRONIC",2),
                cell("AFTER_REFORM","PAPER",8),
                cell("AFTER_REFORM","ELECTRONIC",12))
    params={"reform_on":"2026-10-01","as_of":at,
            "legal_calendar_zone":"Europe/Madrid"}
    equal=audit_regime_capture(strata=cells(Fraction(1,2),Fraction(1,1)),**params)
    rising=audit_regime_capture(strata=cells(Fraction(1,2),Fraction(1,2)),**params)
    return compare_capture_hypotheses(left=equal,right=rising)


def _node_warehouse(*, cut: str, scenario: str, assets: list[dict]) -> dict:
    runner=Path(__file__).resolve().parents[2]/"scripts"/"scientific_integration_warehouse.mjs"
    request={"cut":cut,"scenario":scenario,"sha256":_sha(FAKE_PARITY),"assets":assets}
    try:
        proc=subprocess.run(["node",str(runner)],input=json.dumps(request),
            text=True,capture_output=True,timeout=5,check=False)
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise RuntimeError("SYNTHETIC_NODE_BRIDGE_UNAVAILABLE") from exc
    if proc.returncode!=0 or len(proc.stdout)>5000:
        raise RuntimeError("SYNTHETIC_NODE_BRIDGE_REJECTED")
    try:
        data=json.loads(proc.stdout)
    except ValueError as exc:
        raise RuntimeError("INVALID_SYNTHETIC_BRIDGE_JSON") from exc
    # Closed schema across a real process boundary. Neither a Node upgrade
    # nor a compromised CLI must create new `true` release attestations,
    # arbitrary census numbers, first-public dates or unrecognized fields.
    expected_keys = {
        "schema", "synthetic_sha256_parity", "assets_verified_by_bytes",
        "roles_visible_as_of", "roles_at_valid_day_and_cut",
        "decisions_visible_as_of", "source_count_visible_as_of",
        "spoofed_raw_source_visible_as_of", "recursive_private_key_rejected",
        "rights_independent_attestation_available", "real_people_scoring_enabled",
        "raw_rights_blocker", "real_denominator", "first_public_at_real",
        "publisher_authenticated", "source_identity_crosswalk_certified",
    }
    expected_visible = 1 if cut == "early" else 2
    if (not isinstance(data,dict)
            or set(data) != expected_keys
            or data.get("schema")!="pfl.synthetic_warehouse_bridge.v1"
            or data.get("synthetic_sha256_parity") is not True
            or data.get("real_people_scoring_enabled") is not False
            or data.get("rights_independent_attestation_available") is not False
            or data.get("publisher_authenticated") is not False
            or data.get("real_denominator") is not None
            or data.get("first_public_at_real") is not None
            or data.get("source_identity_crosswalk_certified") is not False
            or data.get("spoofed_raw_source_visible_as_of") is not False
            or data.get("recursive_private_key_rejected") is not (scenario == "privacy_probe")
            or data.get("raw_rights_blocker") is not (scenario == "rights_spoof")
            or any(type(data.get(k)) is not int or data[k] != expected_visible
                   for k in ("roles_visible_as_of", "roles_at_valid_day_and_cut",
                             "decisions_visible_as_of", "source_count_visible_as_of"))
            or data.get("assets_verified_by_bytes")!=[
                {"id":a["id"],"sha256":a["sha256"]} for a in assets]):
        raise RuntimeError("CROSS_LANGUAGE_CONTRACT_DIVERGENCE")
    # SHA/identity details are checked SERVER-SIDE but must not be exposed at
    # an earlier knowledge cut. The bridge is never a second source witness.
    data.pop("assets_verified_by_bytes")
    if cut == "late":
        data["assets_bound_to_fixed_fixture"] = True
    return data


def report(*,cut: str = "late",scenario: str = "baseline") -> dict:
    """Consume actual contracts; no input for originals is ever accepted."""
    if type(cut) is not str or cut not in CUTS:
        raise ValueError("INVALID_SYNTHETIC_LAB_CUT")
    if type(scenario) is not str or scenario not in SCENARIOS:
        raise ValueError("INVALID_SYNTHETIC_LAB_SCENARIO")
    at=CUTS[cut]
    assets=_assets()
    rights=(_rights(assets,at=at) if cut=="late" else {
        "reuse_admitted":False,"real_originals_approved":False,
        "purpose":"PUBLIC_AGGREGATE_DISPLAY","per_asset":{},
        "independent_attestation":False})
    temporal, temporal_snapshot, receipts=_temporal(assets,at=at)
    procedure, episodes=_procedural(at)
    followup=_reconcile_followup(snapshot=temporal_snapshot,
                                 episodes=episodes,procedural=procedure,
                                 receipts=receipts)
    denominator=_denominator(at)
    warehouse=_node_warehouse(cut=cut,scenario=scenario,assets=assets)
    if temporal["pp04_asset_receipts_visible"]==2:
        parsed=audit_pp04_dual_parsers(
            (PAN_TEXT,),(IAEN_TEXT,),expected_plan_count=2,
            expected_planned_count=2,expected_approved_count=1,
            expected_planned_sections=(1,),expected_unplanned_count=2)
        # The internal parser count does not create a registry denominator.
        pp04={k:parsed[k] for k in (
            "planned_count","approved_count","pending_unsplit_count",
            "not_included_4221_excluded","item_crosswalk_verified",
            "count_is_source_internal_only","two_parsers_are_independent_sources")}
    else:
        pp04=None
    rivals=_capture_rivals(at) if cut=="late" else None
    lineage=institutional_report(as_of=at,cut_on="2023-12-31")
    if (denominator.get("independent_denominator_certified") is not False
            or lineage.get("legal_identity_authenticated") is not False):
        raise RuntimeError("SCIENTIFIC_CONTRACT_PROMOTION_BLOCKED")
    return {
        "schema":"pfl.synthetic_scientific_integration_lab.v1",
        "evidence_class":"SYNTHETIC_LAB_ONLY","cut":cut,"as_of":at,
        "scenario":scenario,"pp04":pp04,"rights":rights,
        "source_assets":([
            {"id":a["id"],"sha256":a["sha256"]} for a in assets
        ] if cut=="late" else []),
        "temporal":temporal,"procedure":procedure,
        "followup_reconciliation":followup,
        "denominator_comparison":denominator,"capture_models":rivals,
        "institutional_graph":{
            "legal_identity_authenticated":lineage["legal_identity_authenticated"],
            "source_reuse_rights_verified":lineage["source_reuse_rights_verified"],
            "historical_first_public_at":lineage["historical_first_public_at"],
            "complete_explicit_lineage_links":lineage["complete_explicit_lineage_links"]},
        "warehouse":warehouse,"independent_all_received_denominator":None,
        "right_censoring_independently_attested":False,
        "real_corpus_ingestion_allowed":False,"real_people_scoring_enabled":False,
        "scientific_estimator_admitted":False,"scientific_AB_cycles":0,
        "release_gates_passed":0,"R5":"STOP_R5",
    }
