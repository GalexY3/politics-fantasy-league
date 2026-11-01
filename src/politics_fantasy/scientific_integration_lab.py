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
BITEMPORAL_VALID_DAYS = ("2026-09-15", "2026-10-10")
BITEMPORAL_BYTES = (
    "SYNTHETIC BITEMPORAL FIXTURE\nISSUER:SYN:CHRONICLE\n"
    "EDITION:V1\nACTOR:A\nEVENT:E1\n",
    "SYNTHETIC BITEMPORAL FIXTURE\nISSUER:SYN:CHRONICLE\n"
    "EDITION:V2\nACTOR:A\nEVENT:E1_REVISED\n",
)
CHAIN_BYTES = (
    "SYNTHETIC TYPED CHAIN\nISSUER:SYN:CHAIN\nEDITION:V1\nACTOR:A\n"
    "ORGANIZATION:O\nCOMMUNICATION:C1\nPROCESS:P1_PENDING\n",
    "SYNTHETIC TYPED CHAIN\nISSUER:SYN:CHAIN\nEDITION:V2\nACTOR:A\n"
    "ORGANIZATION:O\nCOMMUNICATION:C1_REVISED\nDECISION:D1_APPROVED\n"
    "PROCESS:P1_APPROVED\n",
)
CHAIN_VALID_DAYS = ("2026-09-11", "2026-09-15")

# S3 mathematics, reconstructed from the user-supplied exact rational oracle.
# These are observed binary *fixture categories*, not administrative decisions.
S3_BINARY = {"before": (6, 4), "after": (7, 3)}
S3_RATIO_RANGE = (Fraction(1, 2), Fraction(2, 1))

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


def _partial_identification_fixture() -> dict:
    """Immutable, aggregate-only S3 wire; no real intake or case identities."""
    return {
        "schema": "pfl.synthetic_partial_identification_wire.v1",
        "as_of": CUTS["late"],
        "population": "SYNTHETIC_OBSERVED_BINARY_ONLY",
        "observations": {
            period: {"observed_positive": positive,
                     "observed_negative": negative,
                     "documented_censor_witnesses": 0}
            for period, (positive, negative) in S3_BINARY.items()
        },
        "selection_ratio_positive_to_negative": {
            "lower": "1/2", "upper": "2/1",
        },
        "independent_registry_total": None,
        "first_public_at_real": None,
        "rights_independently_verified": False,
        "causal_effect_claimed": False,
        "administrative_negative_claimed": False,
    }


def _rational(value: Fraction) -> str:
    """Canonical exact fraction, including denominator one and negative signs."""
    return f"{value.numerator}/{value.denominator}"


def _partial_identification(wire: dict) -> dict:
    """S3 selection sensitivity; intervals are conditional, never causal.

    Let q=P(Y=1 | observed), r=Pr(observed | Y=1)/Pr(observed | Y=0).
    Population prevalence p=q/(q+r(1-q)), decreasing in r. Without a
    restriction on r>0 the closure for a prevalence is [0,1], and the
    prevalence *change* has only the trivial closure [-1,1].
    """
    reference = _partial_identification_fixture()
    if (type(wire) is not dict or set(wire) != set(reference)
            or wire["schema"] != reference["schema"]
            or wire["as_of"] != CUTS["late"]
            or wire["population"] != reference["population"]
            or any(wire[k] is not reference[k] for k in (
                "independent_registry_total", "first_public_at_real",
                "rights_independently_verified", "causal_effect_claimed",
                "administrative_negative_claimed"))):
        raise RuntimeError("S3_UNTRUSTED_REAL_SOURCE_OR_KNOWLEDGE_CUT")
    rows = wire["observations"]
    if (type(rows) is not dict or set(rows) != set(S3_BINARY)):
        raise RuntimeError("S3_BINARY_FRAME_MISMATCH")
    for period, (positive, negative) in S3_BINARY.items():
        row = rows[period]
        if (type(row) is not dict or set(row) != {
                "observed_positive", "observed_negative",
                "documented_censor_witnesses"} or
                type(row["observed_positive"]) is not int or
                type(row["observed_negative"]) is not int or
                type(row["documented_censor_witnesses"]) is not int or
                (row["observed_positive"], row["observed_negative"],
                 row["documented_censor_witnesses"]) != (positive, negative, 0)):
            raise RuntimeError("S3_BINARY_FRAME_MISMATCH")
    ratio = wire["selection_ratio_positive_to_negative"]
    if (type(ratio) is not dict or set(ratio) != {"lower", "upper"} or
            ratio != {"lower": "1/2", "upper": "2/1"}):
        raise RuntimeError("S3_RATIO_RANGE_SPOOF_OR_SWAP")
    lower_r, upper_r = S3_RATIO_RANGE
    if not 0 < lower_r <= upper_r:
        raise RuntimeError("S3_RATIO_RANGE_SPOOF_OR_SWAP")
    shares = {}
    bounds = {}
    for period, (positive, negative) in S3_BINARY.items():
        q = Fraction(positive, positive + negative)
        p_at_upper = q / (q + upper_r * (1 - q))
        p_at_lower = q / (q + lower_r * (1 - q))
        shares[period] = _rational(q)
        bounds[period] = (p_at_upper, p_at_lower)
    change_lower = bounds["after"][0] - bounds["before"][1]
    change_upper = bounds["after"][1] - bounds["before"][0]
    return {
        "schema": "pfl.synthetic_partial_identification_oracle.v1",
        "status": "ASSUMPTION_CONDITIONAL_NONCAUSAL_BOUNDS",
        "observed_positive_share": shares,
        "selection_ratio_positive_to_negative": {
            "lower": _rational(lower_r), "upper": _rational(upper_r)},
        "prevalence_bounds": {
            period: {"lower": _rational(lo), "upper": _rational(hi)}
            for period, (lo, hi) in bounds.items()},
        "change_bounds": {"lower": _rational(change_lower),
                          "upper": _rational(change_upper)},
        "without_ratio_restriction": {
            "nontrivial_bounds_available": False,
            "trivial_change_closure": {"lower": "-1/1", "upper": "1/1"}},
        "documented_censor_witnesses": {"before": 0, "after": 0},
        "observed_negative_is_administrative_failure": False,
        "independent_registry_total": None,
        "first_public_at_real": None,
        "rights_independently_verified": False,
        "causal_effect_identified": False,
        "empirical_estimand_admitted": False,
    }


def _assets() -> list[dict]:
    return [
        {"id": "SYNTHETIC:PAN24", "text": PAN_TEXT, "sha256": _sha(PAN_TEXT)},
        {"id": "SYNTHETIC:IAEN24", "text": IAEN_TEXT, "sha256": _sha(IAEN_TEXT)},
    ]


def _bitemporal_fixture() -> dict:
    """Two *invented* issuer editions; no joins to PP04 or real actors.

    Amendment identity is declared as fixture metadata, not inferred from
    name or a matching SHA. Each edition has its OWN immutable bytes/receipt.
    """
    sources=[{
        "source_id":f"SYN:CHRONICLE_V{i}", "text":body,
        "sha256":_sha(body), "captured_at":captured,
        "first_public_at":published,
    } for i,(body,captured,published) in enumerate(zip(
        BITEMPORAL_BYTES,(EARLY_CAPTURE,LATE_CAPTURE),
        ("2026-09-19T12:00:00Z",LATE_PUBLIC)),start=1)]
    return {
        "schema":"pfl.synthetic_bitemporal_actor_event_wire.v1",
        "issuer":"SYN:CHRONICLE", "sources":sources,
        "actor_id":"SYN:CHRONICLE_ACTOR",
        "institution_id":"SYN:CHRONICLE_OFFICE",
        "roles":[
            {"id":"SYN:CHRONICLE_ROLE_V1","source_id":sources[0]["source_id"],
             "revision":"v1","valid_from":"2026-09-01",
             "valid_to":"2026-10-01","amendment_of":None},
            {"id":"SYN:CHRONICLE_ROLE_V2","source_id":sources[1]["source_id"],
             "revision":"v2","valid_from":"2026-10-01",
             "valid_to":None,"amendment_of":"SYN:CHRONICLE_ROLE_V1"},
        ],
        "events":[
            {"id":"SYN:CHRONICLE_EVENT_V1","source_id":sources[0]["source_id"],
             "revision":"v1","occurred_on":"2026-09-10",
             "typed_key":["SYN:CHRONICLE","INITIATIVE","FILE_1"],
             "amendment_of":None},
            {"id":"SYN:CHRONICLE_EVENT_V2","source_id":sources[1]["source_id"],
             "revision":"v2","occurred_on":"2026-09-10",
             "typed_key":["SYN:CHRONICLE","INITIATIVE","FILE_1"],
             "amendment_of":"SYN:CHRONICLE_EVENT_V1"},
        ],
        "first_public_at_real":None,"source_crosswalk_certified":False,
        "independent_denominator":None,"rights_independently_verified":False,
    }


def _bitemporal_actor_event(*, at: str, wire: dict | None = None) -> tuple[dict,dict]:
    """The actual TemporalLedger validates both editions and typed referents.

    This is an explicitly authored SYNTHETIC amendment chain across two
    documentary editions, not a certified cross-source identity crosswalk.
    TemporalLedger supplies the bitemporal visibility and SHA-bound receipts;
    this adapter alone resolves the declared chain of event corrections.
    """
    if type(at) is not str or at not in CUTS.values():
        raise RuntimeError("BITEMPORAL_UNDECLARED_KNOWLEDGE_CUT")
    fixture=_bitemporal_fixture() if wire is None else wire
    if (not isinstance(fixture,dict) or
            set(fixture)!=set(_bitemporal_fixture()) or
            fixture["issuer"]!="SYN:CHRONICLE" or
            fixture["actor_id"]!="SYN:CHRONICLE_ACTOR" or
            fixture["institution_id"]!="SYN:CHRONICLE_OFFICE" or
            any(fixture[k] is not v for k,v in (
                ("first_public_at_real",None),
                ("source_crosswalk_certified",False),
                ("independent_denominator",None),
                ("rights_independently_verified",False)))):
        raise RuntimeError("BITEMPORAL_UNATTESTED_IDENTITY_OR_GATE")
    sources=fixture["sources"]
    roles=fixture["roles"]
    events=fixture["events"]
    if (not isinstance(sources,list) or len(sources)!=2
            or not isinstance(roles,list) or len(roles)!=2
            or not isinstance(events,list) or len(events)!=2):
        raise RuntimeError("BITEMPORAL_TWO_REVISIONS_REQUIRED")
    expected=_bitemporal_fixture()
    # An exact fixed-fixture protocol is safer than accepting self-labelled
    # synthetic bytes and arbitrary issuer-local IDs at a process boundary.
    for index,(source,canonical) in enumerate(zip(sources,expected["sources"])):
        if (not isinstance(source,dict) or set(source)!=set(canonical)
                or any(source[k]!=canonical[k] for k in (
                    "source_id","text","captured_at","first_public_at"))
                or source["sha256"]!=_sha(source["text"])
                or source["sha256"]!=canonical["sha256"]):
            raise RuntimeError("BITEMPORAL_SOURCE_BYTES_OR_SHA_MISMATCH")
    if (roles!=expected["roles"] or events!=expected["events"]):
        raise RuntimeError("BITEMPORAL_TYPED_AMENDMENT_CROSSWALK_MISMATCH")

    ledger=TemporalLedger()
    actor=SourceRef(sources[0]["source_id"],"ACTOR","A")
    office=SourceRef(sources[0]["source_id"],"INSTITUTION","O")
    for source in sources:
        receipt=FileReceipt(source["source_id"],source["sha256"],
            len(source["text"].encode("utf-8")),source["captured_at"],
            "SYNTHETIC","SYNTHETIC")
        ledger.register_source(receipt)
    initial=sources[0]
    for subject,record_id,predicate in (
        (actor,"ACTOR_A","SYNTHETIC_PUBLIC_ACTOR"),
        (office,"OFFICE_O","SYNTHETIC_PUBLIC_INSTITUTION")):
        ledger.add(TemporalRecord(kind="ENTITY",source_id=initial["source_id"],
            source_record_id=record_id,revision="v1",
            source_sha256=initial["sha256"],subject=subject,
            predicate=predicate,object=None,
            valid_from="2026-09-01T00:00:00Z",valid_to=None,
            first_public_at=initial["first_public_at"],
            recorded_at=initial["captured_at"],value="DOCUMENTED_SYNTHETIC"))
    for role in roles:
        source=next(s for s in sources if s["source_id"]==role["source_id"])
        ledger.add(TemporalRecord(kind="ROLE",source_id=role["source_id"],
            source_record_id=role["id"],revision=role["revision"],
            source_sha256=source["sha256"],subject=actor,
            predicate="SYNTHETIC_OFFICE",object=office,
            valid_from=role["valid_from"]+"T00:00:00Z",
            valid_to=(role["valid_to"]+"T00:00:00Z") if role["valid_to"] else None,
            first_public_at=source["first_public_at"],
            recorded_at=source["captured_at"],value=role["revision"]))
    for event in events:
        source=next(s for s in sources if s["source_id"]==event["source_id"])
        ledger.add(TemporalRecord(kind="EVENT",source_id=event["source_id"],
            source_record_id=event["id"],revision=event["revision"],
            source_sha256=source["sha256"],
            subject=SourceRef(event["source_id"],"EVENT","FILE_1"),
            predicate="SYNTHETIC_AMENDED_INITIATIVE",object=None,
            valid_from=event["occurred_on"]+"T00:00:00Z",valid_to=None,
            first_public_at=source["first_public_at"],
            recorded_at=source["captured_at"],value=event["revision"]))

    views={}
    for valid_day in BITEMPORAL_VALID_DAYS:
        snap=ledger.snapshot(as_of=at,valid_at=valid_day+"T12:00:00Z")
        known=[r.source_record_id for r in snap.records
               if r.kind=="EVENT" and r.predicate=="SYNTHETIC_AMENDED_INITIATIVE"]
        if not known or known not in ([events[0]["id"]],
                                      [events[0]["id"],events[1]["id"]]):
            raise RuntimeError("BITEMPORAL_REVISION_CHAIN_DIVERGENCE")
        views[valid_day]={
            "actor_source_local_identity_count":sum(
                r.kind=="ENTITY" and r.subject==actor for r in snap.records),
            "role_assertions_visible_at_valid_day":sum(
                r.kind=="ROLE" and r.subject==actor for r in snap.records),
            "role_observation_state":("OBSERVED" if any(
                r.kind=="ROLE" and r.subject==actor for r in snap.records)
                else "NOT_OBSERVED"),
            "event_documentary_revisions_known":len(known),
            "logical_events_after_typed_amendment":1,
            "selected_revision":"v2" if len(known)==2 else "v1",
        }
    return ({
        "schema":"pfl.synthetic_bitemporal_actor_event_oracle.v1",
        "views_by_valid_day":views,
        "visible_source_receipts":sum(
            utc(s["captured_at"])<=utc(at) and
            utc(s["first_public_at"])<=utc(at) for s in sources),
        "fixture_source_sha_checked":True,
        "typed_amendment_fixture_checked":True,
        "first_public_at_real":None,"rights_independently_verified":False,
        "source_crosswalk_certified":False,"independent_denominator":None,
        "real_actor_identity_verified":False,"empirical_event_count_admitted":False,
    },fixture)


def _typed_institutional_chain_fixture() -> dict:
    """One synthetic issuer, two byte editions, five *distinct* typed families.

    The explicit source-scoped identifiers are neither official IDs nor a
    person crosswalk. A communication amendment is not a second communication
    or an administrative decision; PROCESS is an EntryEpisode, not a Node event.
    """
    sources=[{
        "source_id":f"SYN:CHAIN_V{i}","text":body,"sha256":_sha(body),
        "captured_at":capture,"first_public_at":published,
    } for i,(body,capture,published) in enumerate(zip(CHAIN_BYTES,
        (EARLY_CAPTURE,LATE_CAPTURE),
        ("2026-09-19T12:00:00Z",LATE_PUBLIC)),start=1)]
    typed={"actor":["SYN:CHAIN","ACTOR","A"],
           "organization":["SYN:CHAIN","ORGANIZATION","O"],
           "communication":["SYN:CHAIN","COMMUNICATION","C1"],
           "decision":["SYN:CHAIN","DECISION","D1"],
           "process":["SYN:CHAIN","PROCESS","P1"]}
    return {
        "schema":"pfl.synthetic_typed_institutional_chain_wire.v1",
        "issuer":"SYN:CHAIN","sources":sources,"typed_keys":typed,
        "communications":[{
            "kind":"COMMUNICATION","id":f"SYN:CHAIN_COMM_V{i}",
            "source_id":source["source_id"],"source_sha256":source["sha256"],
            "revision":f"v{i}","occurred_on":"2026-09-10",
            "amendment_of":None if i==1 else "SYN:CHAIN_COMM_V1",
            "actor_key":typed["actor"],"organization_key":typed["organization"],
            "process_key":typed["process"],
        } for i,source in enumerate(sources,start=1)],
        "decision":{
            "kind":"DECISION","id":"SYN:CHAIN_DEC_V2",
            "source_id":sources[1]["source_id"],
            "source_sha256":sources[1]["sha256"],"revision":"v1",
            "occurred_on":"2026-09-14","amendment_of":None,
            "actor_key":typed["actor"],"organization_key":typed["organization"],
            "process_key":typed["process"],
        },
        "process":{
            "kind":"PROCESS_EPISODE","episode_id":"SYNTHETIC:CHAIN_EPISODE1",
            "typed_key":typed["process"],"entry_on":"2026-09-05",
            "entry_source_id":sources[0]["source_id"],
            "entry_sha256":sources[0]["sha256"],
            "entry_observed_at":EARLY_CAPTURE,
            "communication_key":typed["communication"],
            "decision_key":typed["decision"],
            "pending":{"on":"2026-09-12","observed_at":EARLY_CAPTURE,
                       "source_id":sources[0]["source_id"],
                       "source_sha256":sources[0]["sha256"]},
            "approval":{"stage":"APPROVED","on":"2026-09-14",
                        "documented_on":"2026-09-19",
                        "observed_at":LATE_CAPTURE,
                        "source_id":sources[1]["source_id"],
                        "source_sha256":sources[1]["sha256"]},
        },
        "rights_purpose":"PUBLIC_AGGREGATE_DISPLAY",
        "source_asset_covered_purpose":"LOCAL_ACADEMIC_READ",
        "rights_by_asset_purpose_admitted":False,
        "first_public_at_real":None,"independent_denominator":None,
        "official_identity_crosswalk_verified":False,
        "real_outcomes_attested":False,
    }


def _typed_institutional_chain(*, at: str,
                               wire: dict | None = None) -> tuple[dict,dict]:
    """Replay source+SHA+knowledge+valid-day through five invented categories.

    TemporalLedger authenticates internal *fixture* receipts and editions;
    audit_lab gives the independent procedural-stage interpretation. Both
    computations bind the same typed source-local process to the same bytes.
    """
    if at not in CUTS.values():
        raise RuntimeError("CHAIN_KNOWLEDGE_CUT_INVALID")
    expected=_typed_institutional_chain_fixture()
    w=expected if wire is None else wire
    flags=("rights_purpose","source_asset_covered_purpose",
           "rights_by_asset_purpose_admitted","first_public_at_real",
           "independent_denominator","official_identity_crosswalk_verified",
           "real_outcomes_attested")
    if (type(w) is not dict or set(w)!=set(expected) or
            any(type(w[k]) is not type(expected[k]) or w[k]!=expected[k]
                for k in ("schema","issuer",*flags))):
        raise RuntimeError("CHAIN_RIGHTS_FRAME_OR_ISSUER_PROMOTION")
    sources=w["sources"]
    if (type(sources) is not list or len(sources)!=2):
        raise RuntimeError("CHAIN_SOURCE_RECEIPT_MISMATCH")
    receipts={}
    ledger=TemporalLedger()
    for source,ref in zip(sources,expected["sources"]):
        if (type(source) is not dict or set(source)!=set(ref) or
                any(source[k]!=ref[k] for k in
                    ("source_id","text","captured_at","first_public_at")) or
                source["sha256"]!=_sha(source["text"]) or
                source["sha256"]!=ref["sha256"]):
            raise RuntimeError("CHAIN_SOURCE_RECEIPT_MISMATCH")
        receipt=FileReceipt(source["source_id"],source["sha256"],
            len(source["text"].encode()),source["captured_at"],
            "SYNTHETIC","SYNTHETIC")
        ledger.register_source(receipt)
        receipts[(receipt.source_id,receipt.sha256)]=receipt
        # Purpose/asset-bound rights: a local academic read claim cannot
        # admit the different purpose of public aggregate display.
        verdict=assess_distribution_rights({
            "distribution_id":receipt.source_id,"asset_sha256":receipt.sha256,
            "asset_url":"https://example.invalid/synthetic-typed-chain",
            "historical_as_of":at,"first_public_at":None,
            "requested_purpose":w["rights_purpose"],
            "rights":{"kind":"PUBLISHER_ASSET_SPECIFIC",
                "distribution_id":receipt.source_id,
                "asset_sha256":receipt.sha256,
                "covered_purposes":[w["source_asset_covered_purpose"]],
                "notice_published_at":source["first_public_at"],
                "terms_mode":"PUBLISHER_OPEN_NOTICE",
                "terms_reviewed_by_human":False,
                "rights_reviewed_by_human":False}})
        if verdict["reuse_admitted"] or verdict["empirical_r5_open"]:
            raise RuntimeError("CHAIN_RIGHTS_PROMOTED")
    if json.dumps({k:w[k] for k in ("typed_keys","communications","decision","process")},
                  sort_keys=True,separators=(",",":")) != json.dumps(
                 {k:expected[k] for k in ("typed_keys","communications","decision","process")},
                  sort_keys=True,separators=(",",":")):
        raise RuntimeError("CHAIN_TYPED_SOURCE_LINK_MISMATCH")
    actor=SourceRef(sources[0]["source_id"],"ACTOR","A")
    org=SourceRef(sources[0]["source_id"],"ORGANIZATION","O")
    process=SourceRef(sources[0]["source_id"],"PROCESS","P1")
    first=sources[0]
    for subject,kind in ((actor,"ACTOR"),(org,"ORGANIZATION"),
                         (process,"PROCESS")):
        ledger.add(TemporalRecord(kind="ENTITY",source_id=first["source_id"],
            source_record_id=kind,revision="v1",source_sha256=first["sha256"],
            subject=subject,predicate="SYNTHETIC_"+kind,object=None,
            valid_from="2026-09-05T00:00:00Z",valid_to=None,
            first_public_at=first["first_public_at"],
            recorded_at=first["captured_at"],value="DOCUMENTED_FIXTURE"))
    for event in [*w["communications"],w["decision"]]:
        source=next(s for s in sources if s["source_id"]==event["source_id"])
        if (event["source_id"],event["source_sha256"]) not in receipts:
            raise RuntimeError("CHAIN_SOURCE_RECEIPT_MISMATCH")
        ledger.add(TemporalRecord(kind="EVENT",source_id=source["source_id"],
            source_record_id=event["id"],revision=event["revision"],
            source_sha256=source["sha256"],
            subject=SourceRef(source["source_id"],event["kind"],
                              "C1" if event["kind"]=="COMMUNICATION" else "D1"),
            predicate="SYNTHETIC_"+event["kind"],object=None,
            valid_from=event["occurred_on"]+"T00:00:00Z",valid_to=None,
            first_public_at=source["first_public_at"],
            recorded_at=source["captured_at"],value=event["revision"]))
    p=w["process"]
    frame=_population_target(unit="REGISTRY_INITIAL_WRITING")
    episode=EntryEpisode(episode_id=p["episode_id"],frame=frame,
        entry_on=p["entry_on"],entry_observed_at=p["entry_observed_at"],
        entry_sha_claim=p["entry_sha256"],channel="PAPER",
        acts=(StageAct(stage=p["approval"]["stage"],
             occurred_on=p["approval"]["on"],
             documented_on=p["approval"]["documented_on"],
             observed_at=p["approval"]["observed_at"],
             document_sha_claim=p["approval"]["source_sha256"],
             legal_calendar_zone="Europe/Madrid"),),
        pending=(PendingWitness(pending_on=p["pending"]["on"],
             observed_at=p["pending"]["observed_at"],
             document_sha_claim=p["pending"]["source_sha256"],
             legal_calendar_zone="Europe/Madrid"),))
    if (p["entry_source_id"],p["entry_sha256"]) not in receipts or any(
            (p[k]["source_id"],p[k]["source_sha256"]) not in receipts
            for k in ("pending","approval")):
        raise RuntimeError("CHAIN_PROCESS_SOURCE_RECEIPT_MISMATCH")
    proc=audit_lab(frame=frame,episodes=(episode,),as_of=at)
    # The stage report has only an as_of clock. The valid-day projection is
    # deliberately additional; no future decision may enter an earlier day.
    views={}
    for valid_day in CHAIN_VALID_DAYS:
        snap=ledger.snapshot(as_of=at,valid_at=valid_day+"T12:00:00Z")
        comms=[r for r in snap.records if r.kind=="EVENT" and
               r.predicate=="SYNTHETIC_COMMUNICATION"]
        decisions=[r for r in snap.records if r.kind=="EVENT" and
                   r.predicate=="SYNTHETIC_DECISION"]
        expected_comm=1 if at==CUTS["early"] else 2
        expected_dec=int(at==CUTS["late"] and valid_day>="2026-09-14")
        if (len(comms)!=expected_comm or len(decisions)!=expected_dec or
                [r.source_record_id for r in comms] != [
                    e["id"] for e in w["communications"][:expected_comm]] or
                (decisions and decisions[0].source_record_id!=w["decision"]["id"])):
            raise RuntimeError("CHAIN_TYPED_TEMPORAL_DIVERGENCE")
        pending=int(not decisions and valid_day>=p["pending"]["on"])
        views[valid_day]={
            "actor_visible":int(any(r.kind=="ENTITY" and r.subject==actor
                                   for r in snap.records)),
            "organization_visible":int(any(r.kind=="ENTITY" and r.subject==org
                                          for r in snap.records)),
            "communication_documentary_revisions_known":len(comms),
            "logical_communications":int(bool(comms)),
            "decision_documentary_revisions_known":len(decisions),
            "logical_decisions":len(decisions),
            "process_episode_visible":int(any(r.kind=="ENTITY" and
                r.subject==process for r in snap.records)),
            "process_state":("APPROVED_AS_OF_EVIDENCE" if decisions else
                 "PENDING_AS_OF_EVIDENCE" if pending else "UNKNOWN_FOLLOWUP"),
            "pending_not_negative":pending,
            "negative_decisions":0,"censor_witnesses":0,
        }
    if (proc["all_received_denominator"] is not None or
            proc["terminal_by_cause"]["INADMITTED"]!=0 or
            proc["terminal_by_cause"]["REJECTED"]!=0 or
            proc["unknown_followup"] != (0 if at==CUTS["late"] else 0) or
            proc["terminal_by_cause"]["APPROVED"] != int(at==CUTS["late"])):
        raise RuntimeError("CHAIN_PROCEDURAL_CLASSIFICATION_DIVERGENCE")
    return ({
        "schema":"pfl.synthetic_typed_institutional_chain_oracle.v1",
        "views_by_valid_day":views,
        "visible_source_receipts":1 if at==CUTS["early"] else 2,
        "same_fixture_source_sha_checked":True,
        "typed_cross_family_links_checked":True,
        "source_asset_rights_admitted":False,
        "public_display_purpose_admitted":False,
        "first_public_at_real":None,"independent_denominator":None,
        "real_actor_identity_verified":False,
        "real_decision_outcome_attested":False,
        "real_censoring_attested":False,
        "empirical_estimand_admitted":False,
    },w)


def _b0_b3_fixture(chain: dict) -> dict:
    """Two explicitly hypothetical DGPs sharing the SAME published chain.

    Both hypotheses stipulate the SAME four hypothetical first-received
    episodes. B0 does not observe an E3 terminal decision by the late cut;
    B3 supposes a rejected E3 hidden from publication. In both, E2 is pending
    and E4 has ONLY a fictional censor witness. The published source is still
    the single typed P1 chain in both. Equal N cannot discriminate models.
    """
    ids=[source["source_id"] for source in chain["sources"]]
    hidden=[["SYN:CHAIN","PROCESS",f"HIDDEN{i}"] for i in (2,3,4)]
    return {
        "schema":"pfl.synthetic_b0_b3_full_observation_wire.v1",
        "chain_issuer":chain["issuer"],
        "published_receipts":[{"source_id":s["source_id"],
                                "sha256":s["sha256"]} for s in chain["sources"]],
        "typed_keys":chain["typed_keys"],
        "mechanisms":{
            "B0_CALENDAR":{
                "publication_mechanism":"FIXED_CALENDAR_NO_FILTER",
                "hypothetical_all_received":4,
                "hypothetical_unpublished_episodes":3,
                "hypothetical_hidden_process_keys":hidden,
                "hypothetical_e2_status":"PENDING_NOT_NEGATIVE",
                "hypothetical_e3_status":"NO_TERMINAL_AT_LATE_HEARING_FUTURE_2026_11_05",
                "hypothetical_e3_terminal_on":None,
                "hypothetical_e4_status":"RIGHT_CENSOR_WITNESS_NOT_REJECTION",
                "published_source_ids":ids,
                "hypothetical_release_trigger":"SCHEDULED_2026_10_30",
            },
            "B3_SELECTION_PUBLICATION":{
                "publication_mechanism":"SELECTED_AND_HELD_QUEUE",
                "hypothetical_all_received":4,
                "hypothetical_unpublished_episodes":3,
                "hypothetical_hidden_process_keys":hidden,
                "hypothetical_e2_status":"PENDING_NOT_NEGATIVE",
                "hypothetical_e3_status":"REJECTED_2026_10_10_WITHHELD_FROM_PUBLICATION",
                "hypothetical_e3_terminal_on":"2026-10-10",
                "hypothetical_e4_status":"RIGHT_CENSOR_WITNESS_NOT_REJECTION",
                "published_source_ids":ids,
                "hypothetical_release_trigger":"SELECTED_2026_10_20_FOR_2026_10_30",
            },
        },
        "discriminating_witnesses":{
            "independent_all_received_registry_available":False,
            "independent_e3_terminal_status_document_available":False,
            "publisher_selection_log_available":False,
            "historical_first_public_attested":False,
        },
        "real_independent_all_received":None,
        "real_first_public_at":None,
        "rights_by_distribution_and_purpose_admitted":False,
        "official_crosswalk_verified":False,
        "causal_effect_identified":False,
    }


def _b0_b3_published_rows(chain: dict, *, as_of: str,
                          valid_day: str, mechanism: dict) -> tuple:
    """Exact visible source+SHA+typed-key+revision+valid-day projection.

    This internal trace is never emitted in HTTP. It is intentionally richer
    than a count: a swapped source SHA, revised communication ID or family
    would change the equality oracle even if all marginal counts agreed.
    """
    sources={s["source_id"]:s for s in chain["sources"]}
    types=chain["typed_keys"]
    facts=[]
    def add(family: str, typed_key: list, source_id: str,
            revision: str, valid_on: str, semantic: str):
        if source_id not in mechanism["published_source_ids"]:
            return
        source=sources[source_id]
        if (utc(source["captured_at"])<=utc(as_of)
                and utc(source["first_public_at"])<=utc(as_of)
                and valid_on<=valid_day):
            facts.append((family,tuple(typed_key),source_id,source["sha256"],
                          revision,valid_on,semantic))
    first=chain["sources"][0]["source_id"]
    p=chain["process"]
    add("ACTOR",types["actor"],first,"v1",p["entry_on"],"ENTITY")
    add("ORGANIZATION",types["organization"],first,"v1",p["entry_on"],"ENTITY")
    add("PROCESS",types["process"],p["entry_source_id"],"entry",
        p["entry_on"],"ENTRY_NOT_DENOMINATOR")
    add("PROCESS",types["process"],p["pending"]["source_id"],"pending",
        p["pending"]["on"],"PENDING_NOT_REJECTED")
    add("PROCESS",types["process"],p["approval"]["source_id"],"approved",
        p["approval"]["on"],"APPROVED_FIXTURE_ONLY")
    for c in chain["communications"]:
        add("COMMUNICATION",types["communication"],c["source_id"],
            c["revision"],c["occurred_on"],"EMITTED_NOT_DECISION")
    d=chain["decision"]
    add("DECISION",types["decision"],d["source_id"],d["revision"],
        d["occurred_on"],"SEPARATE_INSTITUTIONAL_DECISION")
    # B3 has a hypothetical, *unpublished* latent process. It has NO
    # authenticated source+SHA and therefore NEVER enters a published trace.
    return tuple(sorted(facts))


def _b0_b3_equivalence(*, chain: dict, at: str,
                       s3_oracle: dict | None,
                       wire: dict | None = None) -> tuple[dict,dict]:
    """Full five-family observable equivalence, witness design not inference."""
    if at not in CUTS.values():
        raise RuntimeError("B0_B3_KNOWLEDGE_CUT_INVALID")
    expected=_b0_b3_fixture(chain)
    w=expected if wire is None else wire
    gates=("real_independent_all_received","real_first_public_at",
           "rights_by_distribution_and_purpose_admitted",
           "official_crosswalk_verified","causal_effect_identified")
    if (type(w) is not dict or set(w)!=set(expected)
            or any(type(w[k]) is not type(expected[k]) or w[k]!=expected[k]
                   for k in ("schema","chain_issuer",*gates))):
        raise RuntimeError("B0_B3_REAL_AUTHORITY_PROMOTION")
    if (json.dumps({k:w[k] for k in ("published_receipts","typed_keys")},
                   sort_keys=True,separators=(",",":"))!=
            json.dumps({k:expected[k] for k in ("published_receipts","typed_keys")},
                       sort_keys=True,separators=(",",":"))):
        raise RuntimeError("B0_B3_SOURCE_SHA_OR_TYPED_SCOPE_MISMATCH")
    if (json.dumps({k:w[k] for k in ("mechanisms","discriminating_witnesses")},
                   sort_keys=True,separators=(",",":"))!=
            json.dumps({k:expected[k] for k in ("mechanisms","discriminating_witnesses")},
                       sort_keys=True,separators=(",",":"))):
        raise RuntimeError("B0_B3_HYPOTHESIS_OR_WITNESS_SPOOF")
    observations={}
    for cut_name,cut_at in CUTS.items():
        # Deliberately replay both historical cuts, not just the query cut.
        if utc(cut_at)>utc(at):
            continue
        chain_projection,_=_typed_institutional_chain(at=cut_at,wire=chain)
        daily={}
        for valid_day in CHAIN_VALID_DAYS:
            left=_b0_b3_published_rows(chain,as_of=cut_at,valid_day=valid_day,
                                       mechanism=w["mechanisms"]["B0_CALENDAR"])
            right=_b0_b3_published_rows(chain,as_of=cut_at,valid_day=valid_day,
                                        mechanism=w["mechanisms"]["B3_SELECTION_PUBLICATION"])
            if left!=right or not left:
                raise RuntimeError("B0_B3_PUBLISHED_TYPED_PROJECTION_DIVERGENCE")
            counts={name:sum(row[0]==name for row in left) for name in
                    ("ACTOR","ORGANIZATION","COMMUNICATION","DECISION","PROCESS")}
            view=chain_projection["views_by_valid_day"][valid_day]
            if (counts["ACTOR"]!=view["actor_visible"] or
                    counts["ORGANIZATION"]!=view["organization_visible"] or
                    counts["COMMUNICATION"]!=view["communication_documentary_revisions_known"] or
                    counts["DECISION"]!=view["decision_documentary_revisions_known"] or
                    counts["PROCESS"]!=(view["process_episode_visible"]+
                        int(valid_day>=chain["process"]["pending"]["on"])+
                        view["logical_decisions"])):
                raise RuntimeError("B0_B3_CHAIN_REPLAY_INCONSISTENT")
            daily[valid_day]={
                "full_typed_sha_revision_projection_equal":True,
                "published_records_by_family":counts,
                "logical_communications":view["logical_communications"],
                "logical_decisions":view["logical_decisions"],
                "process_state":view["process_state"],
            }
        observations[cut_name]={
            "source_editions_visible":chain_projection["visible_source_receipts"],
            "valid_days":daily,
        }
    if (s3_oracle is None)!=(at==CUTS["early"]):
        raise RuntimeError("B0_B3_S3_LOOKAHEAD_OR_MISSING_ORACLE")
    if (s3_oracle is not None and
            json.dumps(s3_oracle,sort_keys=True,separators=(",",":")) !=
            json.dumps(_partial_identification(_partial_identification_fixture()),
                       sort_keys=True,separators=(",",":"))):
        raise RuntimeError("B0_B3_S3_REFERENCE_DIVERGENCE")
    s3=None if s3_oracle is None else {
        "source":"INDEPENDENT_SYNTHETIC_BINARY_S3_NOT_CHAIN_OUTCOMES",
        "ratio_definition":"P_PUBLISHED_GIVEN_Y1_OVER_P_PUBLISHED_GIVEN_Y0",
        "odds_ratio":False,
        "ratio_range":s3_oracle["selection_ratio_positive_to_negative"],
        "noncausal_change_range":s3_oracle["change_bounds"],
        "chain_calibration_verified":False,
    }
    return ({
        "schema":"pfl.synthetic_b0_b3_observational_equivalence_oracle.v1",
        "status":"B0_B3_FULL_PUBLIC_PROJECTION_EQUIVALENT_NOT_IDENTIFIED",
        "observations_by_knowledge_cut":observations,
        "all_published_source_sha_and_typed_revisions_equal":True,
        "hypothetical_all_received_by_mechanism":{"B0_CALENDAR":4,
            "B3_SELECTION_PUBLICATION":4},
        "hypothetical_unpublished_processes":{"B0_CALENDAR":3,
            "B3_SELECTION_PUBLICATION":3},
        "hypothetical_publication_coverage":{"B0_CALENDAR":"1/4",
            "B3_SELECTION_PUBLICATION":"1/4"},
        "hypothetical_e3_status_by_mechanism":{
            "B0_CALENDAR":"NO_TERMINAL_AT_LATE_HEARING_FUTURE_2026_11_05",
            "B3_SELECTION_PUBLICATION":"REJECTED_2026_10_10_WITHHELD_FROM_PUBLICATION"},
        "hypothetical_e3_terminal_on_by_mechanism":{
            "B0_CALENDAR":None,"B3_SELECTION_PUBLICATION":"2026-10-10"},
        "hypothetical_e2_pending_both":True,
        "hypothetical_e4_right_censor_not_rejection_both":True,
        "hypothetical_release_causes":{"B0_CALENDAR":"SCHEDULED_2026_10_30",
            "B3_SELECTION_PUBLICATION":"SELECTED_2026_10_20_FOR_2026_10_30"},
        "discriminating_witness_requirements":{
            "independent_all_received_registry":{
                "available":False,"hypothetical_counts_match":True,
                "alone_discriminates_mechanisms":False},
            "independent_e3_terminal_status_document":{
                "available":False,"would_discriminate_at_late_cut":True},
            "authenticated_publication_selection_log":{
                "available":False,"would_distinguish_release_mechanisms":True},
            "independent_first_public_by_distribution":{
                "available":False,"alone_discriminates_mechanisms":False}},
        "s3_external_sensitivity":s3,
        "real_all_received_denominator":None,"real_first_public_at":None,
        "rights_for_public_aggregate_admitted":False,
        "real_historical_selection_witness":False,
        "official_crosswalk_verified":False,
        "empirical_causal_effect_identified":False,
        "scientific_cycles":0,
    },w)


def _b0_b3_witness_matrix_fixture(chain: dict) -> dict:
    """Fixed, invented counterfactual witnesses; never real admission evidence.

    Publication and capture are distinct clocks. Source receipts are the
    existing chain editions for the two-vintage experiment, otherwise a
    separate synthetic document with its exact byte digest. Even an internally
    linked witness cannot certify publisher rights or independent provenance.
    """
    e2=["SYN:CHAIN","PROCESS","HIDDEN2"]
    e3=["SYN:CHAIN","PROCESS","HIDDEN3"]
    e4=["SYN:CHAIN","PROCESS","HIDDEN4"]
    early_public="2026-09-19T12:00:00Z"
    late_public="2026-10-30T12:00:00Z"
    later="2026-11-03T12:00:00Z"
    definitions=(
        ("NONE","NONE",None,None,None,None,False,False),
        ("ALL_RECEIVED_N4","INDEPENDENT_ALL_RECEIVED_N4",None,
         "2026-09-10",early_public,EARLY_CAPTURE,True,True),
        ("INCOMPLETE_UNLINKED","INCOMPLETE_UNLINKED",None,
         "2026-09-10",early_public,EARLY_CAPTURE,False,False),
        ("E3_REJECTED_OCT10","E3_REJECTED",e3,
         "2026-10-10",late_public,LATE_CAPTURE,True,True),
        ("E3_PENDING_EXHAUSTIVE_OCT31","E3_STILL_PENDING_EXHAUSTIVE",e3,
         "2026-10-31","2026-10-31T13:00:00Z",
         "2026-11-01T08:00:00Z",True,True),
        ("E2_PENDING","E2_PENDING",e2,
         "2026-09-12",early_public,EARLY_CAPTURE,True,False),
        ("E4_RIGHT_CENSOR","E4_RIGHT_CENSOR_NOT_REJECTED",e4,
         "2026-10-10",late_public,LATE_CAPTURE,True,False),
        ("TWO_VINTAGES_EXACT_SHA","TWO_VINTAGES_SAME_ASSET",None,
         "2026-10-30",late_public,LATE_CAPTURE,True,True),
        ("SELECTION_LOG_B3_VERIFIED_RULE","SELECTION_LOG_RULE_MATCHES_B3",e3,
         "2026-10-20",late_public,LATE_CAPTURE,True,True),
        ("WITNESS_AFTER_LATE_CUT","E3_REJECTED",e3,
         "2026-10-10","2026-11-03T10:00:00Z",later,True,True),
        ("RETROSPECTIVE_FIRST_PUBLIC","RETROSPECTIVE_SOURCE_FIRST_PUBLIC",None,
         "2026-09-19",early_public,LATE_CAPTURE,True,True),
    )
    rows=[]
    for case_id,kind,subject,valid_day,published,captured,linked,exhaustive in definitions:
        body=(f"SYNTHETIC DIFFERENTIAL WITNESS\nCASE:{case_id}\n"
              f"KIND:{kind}\n") if kind!="NONE" else None
        rows.append({
            "case":case_id,"kind":kind,"source_id":(
                "SYN:WITNESS_"+case_id if body else None),
            "issuer":"SYN:INDEPENDENT_WITNESS_LAB" if body else None,
            "bytes":body,"sha256":_sha(body) if body else None,
            "subject_key":subject,"valid_on":valid_day,
            "first_public_at":published,"captured_at":captured,
            "source_local_linked_in_fixture":linked,
            "claim_exhaustive_in_fixture":exhaustive,
            "published_asset_vintages":([{
                "distribution_id":"SYN:CHAIN_PUBLISHED_ASSET",
                "source_id":s["source_id"],"sha256":s["sha256"]}
                for s in chain["sources"]] if kind=="TWO_VINTAGES_SAME_ASSET"
                else []),
        })
    return {
        "schema":"pfl.synthetic_b0_b3_witness_matrix_wire.v1",
        "chain_issuer":chain["issuer"],
        "chain_distribution_receipts":[{"source_id":s["source_id"],
             "sha256":s["sha256"]} for s in chain["sources"]],
        "witnesses":rows,
        "requested_purpose":"PUBLIC_AGGREGATE_DISPLAY",
        "hypothetical_document_purpose":"LOCAL_ACADEMIC_READ",
        "rights_by_distribution_and_purpose_admitted":False,
        "real_independent_registry_total":None,
        "real_first_public_at":None,
        "real_official_crosswalk_verified":False,
        "real_witness_independence_verified":False,
        "causal_identified":False,
    }


def _b0_b3_witness_matrix(*, chain: dict, at: str,
                          b0_b3: dict,
                          wire: dict | None = None) -> tuple[dict,dict]:
    """What each hypothetical witness can, and cannot, distinguish by cut."""
    if at not in CUTS.values():
        raise RuntimeError("WITNESS_MATRIX_UNDECLARED_CUT")
    expected=_b0_b3_witness_matrix_fixture(chain)
    w=expected if wire is None else wire
    if (type(w) is not dict or set(w)!=set(expected) or
            any(type(w[k]) is not type(expected[k]) or w[k]!=expected[k]
                for k in expected if k not in (
                    "witnesses","chain_distribution_receipts"))):
        raise RuntimeError("WITNESS_MATRIX_REAL_RIGHTS_OR_SCOPE_SPOOF")
    if (json.dumps(w["chain_distribution_receipts"],sort_keys=True,
                   separators=(",",":"))!=json.dumps(
                   expected["chain_distribution_receipts"],sort_keys=True,
                   separators=(",",":"))):
        raise RuntimeError("WITNESS_MATRIX_CHAIN_SHA_MISMATCH")
    if type(w["witnesses"]) is not list or len(w["witnesses"])!=len(expected["witnesses"]):
        raise RuntimeError("WITNESS_MATRIX_CASES_MISSING")
    for row,canonical in zip(w["witnesses"],expected["witnesses"]):
        if (type(row) is not dict or set(row)!=set(canonical) or
                json.dumps(row,sort_keys=True,separators=(",",":"))!=
                json.dumps(canonical,sort_keys=True,separators=(",",":")) or
                (row["bytes"] is not None and
                 row["sha256"]!=_sha(row["bytes"]))):
            raise RuntimeError("WITNESS_MATRIX_BYTES_SHA_TYPE_OR_LINK_SPOOF")
        if row["bytes"] is not None:
            # A genuine SHA of invented bytes does NOT grant real rights.
            # Check this asset and its distinct requested purpose individually.
            receipt=FileReceipt(row["source_id"],row["sha256"],
                len(row["bytes"].encode("utf-8")),row["captured_at"],
                "SYNTHETIC","SYNTHETIC")
            if not receipt.query_admitted or utc(row["first_public_at"])>utc(
                    row["captured_at"]):
                raise RuntimeError("WITNESS_MATRIX_RECEIPT_TIME_INVALID")
            legal=assess_distribution_rights({
                "distribution_id":receipt.source_id,
                "asset_sha256":receipt.sha256,
                "asset_url":"https://example.invalid/fictional-witness-only",
                "historical_as_of":at,"first_public_at":None,
                "requested_purpose":w["requested_purpose"],
                "rights":{"kind":"PUBLISHER_ASSET_SPECIFIC",
                    "distribution_id":receipt.source_id,
                    "asset_sha256":receipt.sha256,
                    "covered_purposes":[w["hypothetical_document_purpose"]],
                    "notice_published_at":row["first_public_at"],
                    "terms_mode":"PUBLISHER_OPEN_NOTICE",
                    "terms_reviewed_by_human":False,
                    "rights_reviewed_by_human":False}})
            if legal["reuse_admitted"] or legal["empirical_r5_open"]:
                raise RuntimeError("WITNESS_MATRIX_UNTRUSTED_RIGHTS_PROMOTION")
    if (b0_b3.get("status")!=
            "B0_B3_FULL_PUBLIC_PROJECTION_EQUIVALENT_NOT_IDENTIFIED" or
            b0_b3.get("hypothetical_all_received_by_mechanism")!={
                "B0_CALENDAR":4,"B3_SELECTION_PUBLICATION":4}):
        raise RuntimeError("WITNESS_MATRIX_BASE_DGP_CHANGED")
    cases={}
    for name,query_cut in CUTS.items():
        if utc(query_cut)>utc(at):
            continue
        query_valid_day="2026-10-15" if name=="early" else "2026-10-31"
        evaluations=[]
        for case in w["witnesses"]:
            cid=case["case"]
            # An unlinked or incomplete witness cannot be rescued merely
            # because it was captured early or carries plausible SHA bytes.
            if cid=="NONE":
                admissibility="NONE"
            elif not case["source_local_linked_in_fixture"]:
                admissibility="INADMISSIBLE_INCOMPLETE_OR_UNLINKED"
            elif (utc(case["captured_at"])>utc(query_cut) or
                  utc(case["first_public_at"])>utc(query_cut)):
                admissibility="NOT_KNOWN_AT_CUT"
            elif case["valid_on"]>query_valid_day:
                admissibility="NOT_VALID_AT_QUERY_DAY"
            else:
                admissibility="ADMISSIBLE_HYPOTHETICAL_ONLY"
                if case["kind"]=="TWO_VINTAGES_SAME_ASSET":
                    if any(utc(s["captured_at"])>utc(query_cut) or
                           utc(s["first_public_at"])>utc(query_cut)
                           for s in chain["sources"]):
                        admissibility="NOT_KNOWN_AT_CUT"
            compatible=["B0_CALENDAR","B3_SELECTION_PUBLICATION"]
            falsified=[]
            if admissibility=="ADMISSIBLE_HYPOTHETICAL_ONLY":
                if cid in ("E3_REJECTED_OCT10","SELECTION_LOG_B3_VERIFIED_RULE"):
                    compatible=["B3_SELECTION_PUBLICATION"]
                    falsified=["B0_CALENDAR"]
                elif cid=="E3_PENDING_EXHAUSTIVE_OCT31":
                    compatible=["B0_CALENDAR"]
                    falsified=["B3_SELECTION_PUBLICATION"]
            evaluations.append({
                "case":cid,"witness_admissibility":admissibility,
                "compatible_mechanisms":compatible,
                "falsified":falsified,
                "identified_from_observation":bool(falsified),
                "identification_scope":"SYNTHETIC_COUNTERFACTUAL_ONLY",
                "causal_identified":False,
                "real_evidence_admitted":False,
                "retrospective_first_public_precedes_capture":bool(
                    cid=="RETROSPECTIVE_FIRST_PUBLIC" and
                    admissibility=="ADMISSIBLE_HYPOTHETICAL_ONLY"),
            })
        cases[name]={"as_of":query_cut,"valid_at":query_valid_day,
                     "evaluations":evaluations}
    s3=b0_b3["s3_external_sensitivity"]
    return ({
        "schema":"pfl.synthetic_b0_b3_witness_matrix_oracle.v1",
        "status":"HYPOTHETICAL_DISCRIMINATION_NOT_REAL_ADMISSION",
        "cases_by_knowledge_cut":cases,
        "all_received_same_four_not_discriminating":True,
        "exact_two_published_vintages_not_discriminating":True,
        "selection_log_requires_independent_rule_validation":True,
        "first_public_alone_not_discriminating":True,
        "pending_is_not_negative":True,"right_censor_is_not_rejection":True,
        "hidden_e3_rejection_is_not_observed_administrative_negative":True,
        "s3_exact_noncausal_reference":None if s3 is None else {
            "source":"INDEPENDENT_SYNTHETIC_BINARY_S3_NOT_CHAIN_OUTCOMES",
            "ratio_definition":"P_PUBLISHED_GIVEN_Y1_OVER_P_PUBLISHED_GIVEN_Y0",
            "ratio_range":s3["ratio_range"],
            "noncausal_change_range":s3["noncausal_change_range"],
            "odds_ratio":False,"chain_calibration_verified":False},
        "real_independent_all_received":None,
        "real_first_public_at":None,
        "rights_for_public_display_admitted":False,
        "real_crosswalk_verified":False,
        "real_witness_independence_verified":False,
        "causal_identified":False,"scientific_cycles":0,
    },w)


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
    # Exact JSON types matter at the procedure→temporal reconciliation seam.
    # Python equality would accept `1 == True` or `2 == 2.0`, silently
    # reclassifying a negative count as a boolean or pending as a float.
    if (json.dumps(reconstructed,sort_keys=True,separators=(",",":")) !=
            json.dumps(procedural,sort_keys=True,separators=(",",":"))):
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


def _capture_rivals(at: str) -> tuple[dict, dict]:
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
    comparison=compare_capture_hypotheses(left=equal,right=rising)
    if (comparison["same_visible_projection"] is not True
            or comparison["different_hypothetical_trend_sign"] is not True
            or comparison["real_reform_effect_identified"] is not False):
        raise RuntimeError("CONTROLLED_RIVAL_DESIGN_NOT_OBSERVATIONALLY_EQUIVALENT")
    # This is a bounded engineering challenge for a SECOND computation of the
    # SAME invented observation, not an independently observed source. The
    # identical synthetic fixture keys do not correspond to the PAN/IAEN
    # documentary assets, the institutional actors or a registry of entrants.
    hypotheses={
        label:{
            "visible_by_channel":{
                regime:result["periods"][regime]["visible_by_channel"]
                for regime in ("BEFORE_REFORM","AFTER_REFORM")},
            "hypothetical_intake_by_regime":{
                regime:result["periods"][regime]["hypothetical_intake_lower"]
                for regime in ("BEFORE_REFORM","AFTER_REFORM")},
            "hypothetical_trend_sign":result["hypothetical_trend_sign"],
        }
        for label,result in (("CAPTURE_EXPANSION",equal),
                             ("STABLE_CAPTURE",rising))
    }
    if any(result["periods"][regime]["hypothetical_intake_lower"] !=
           result["periods"][regime]["hypothetical_intake_upper"]
           for result in (equal,rising)
           for regime in ("BEFORE_REFORM","AFTER_REFORM")):
        raise RuntimeError("CONTROLLED_RIVAL_ASSUMPTION_NOT_EXACT")
    experiment={
        "schema":"pfl.synthetic_observational_equivalence_wire.v1",
        "as_of":at,
        "hypotheses":hypotheses,
        "synthetic_fixture_ids_by_channel":{
            regime:equal["periods"][regime]["synthetic_fixture_ids_by_channel"]
            for regime in ("BEFORE_REFORM","AFTER_REFORM")},
        "capture_at_by_channel":{
            regime:equal["periods"][regime]["capture_at_by_channel"]
            for regime in ("BEFORE_REFORM","AFTER_REFORM")},
        "exposure_window_by_regime":{
            regime:equal["periods"][regime]["exposure_window"]
            for regime in ("BEFORE_REFORM","AFTER_REFORM")},
        "first_public_at":None,
        "independent_registry_total":None,
        "source_identity_crosswalk_verified":False,
        "reuse_rights_independently_verified":False,
    }
    return comparison,experiment


def _node_warehouse(*, cut: str, scenario: str, assets: list[dict],
                    experiment: dict | None, timeline: dict,
                    partial_identification: dict | None, chain: dict,
                    b0_b3: dict, witness_matrix: dict) -> dict:
    runner=Path(__file__).resolve().parents[2]/"scripts"/"scientific_integration_warehouse.mjs"
    request={"cut":cut,"scenario":scenario,"sha256":_sha(FAKE_PARITY),
             "assets":assets,"experiment":experiment,"timeline":timeline,
             "partial_identification":partial_identification,"chain":chain,
             "b0_b3":b0_b3,"witness_matrix":witness_matrix}
    try:
        # Keep the *fixed* multi-contract fixture bounded without weakening
        # Node's independent source allowlists or the closed IPC schema.
        proc=subprocess.run(["node",str(runner)],input=json.dumps(
            request,separators=(",",":")),
            text=True,capture_output=True,timeout=5,check=False)
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise RuntimeError("SYNTHETIC_NODE_BRIDGE_UNAVAILABLE") from exc
    if proc.returncode!=0 or len(proc.stdout)>18000:
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
        "observational_equivalence_experiment",
        "bitemporal_actor_event_equivalence",
        "partial_identification_oracle",
        "typed_institutional_chain",
        "b0_b3_observational_equivalence",
        "b0_b3_witness_matrix",
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
                {"id":a["id"],"sha256":a["sha256"]} for a in assets]
            or data.get("observational_equivalence_experiment") !=
               (None if cut == "early" else {
                   "schema":"pfl.synthetic_observational_equivalence_oracle.v1",
                   "status":"OBSERVATIONALLY_EQUIVALENT_NOT_IDENTIFIED",
                   "same_published_by_channel":True,
                   "different_synthetic_trajectories":True,
                   "hypothetical_change_by_mechanism":{
                       "CAPTURE_EXPANSION":"ZERO_CHANGE_UNDER_ASSUMPTIONS",
                       "STABLE_CAPTURE":"POSITIVE_CHANGE_UNDER_ASSUMPTIONS"},
                   "synthetic_published_totals":{"before":10,"after":20},
                   "synthetic_intake_under_assumptions":{
                       "CAPTURE_EXPANSION":{"before":20,"after":20},
                       "STABLE_CAPTURE":{"before":20,"after":40}},
                   "independent_registry_witness":False,
                   "first_public_at":None,
                   "source_identity_crosswalk_verified":False,
                   "rights_independently_verified":False,
                   "real_causal_effect_identified":False,
                   "empirical_estimand_admitted":False,
               })
            # Python equality conflates JSON booleans with integers:
            # False == 0 and True == 1. Compare canonical JSON instead so
            # an IPC drift (censor count 0 -> false, rights false -> 0)
            # cannot escape into HTTP as a type-invalid scientific oracle.
            or json.dumps(data.get("partial_identification_oracle"),
                          sort_keys=True, separators=(",", ":")) !=
               json.dumps((None if cut == "early" else
                           _partial_identification(partial_identification)),
                          sort_keys=True, separators=(",", ":"))):
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
    rivals,experiment=_capture_rivals(at) if cut=="late" else (None,None)
    partial_wire=_partial_identification_fixture() if cut=="late" else None
    partial_oracle=_partial_identification(partial_wire) if cut=="late" else None
    bitemporal,timeline=_bitemporal_actor_event(at=at)
    typed_chain,chain_wire=_typed_institutional_chain(at=at)
    b0_b3_oracle,b0_b3_wire=_b0_b3_equivalence(
        chain=chain_wire,at=at,s3_oracle=partial_oracle)
    matrix_oracle,matrix_wire=_b0_b3_witness_matrix(
        chain=chain_wire,at=at,b0_b3=b0_b3_oracle)
    warehouse=_node_warehouse(cut=cut,scenario=scenario,assets=assets,
                              experiment=experiment,timeline=timeline,
                              partial_identification=partial_wire,chain=chain_wire,
                              b0_b3=b0_b3_wire,witness_matrix=matrix_wire)
    if warehouse.get("bitemporal_actor_event_equivalence") != bitemporal:
        raise RuntimeError("CROSS_LANGUAGE_BITEMPORAL_CONTRACT_DIVERGENCE")
    if warehouse.get("partial_identification_oracle") != partial_oracle:
        raise RuntimeError("CROSS_LANGUAGE_S3_PARTIAL_IDENTIFICATION_DIVERGENCE")
    if (json.dumps(warehouse.get("typed_institutional_chain"),
                   sort_keys=True,separators=(",",":")) !=
            json.dumps(typed_chain,sort_keys=True,separators=(",",":"))):
        raise RuntimeError("CROSS_LANGUAGE_TYPED_CHAIN_DIVERGENCE")
    if (json.dumps(warehouse.get("b0_b3_observational_equivalence"),
                   sort_keys=True,separators=(",",":")) !=
            json.dumps(b0_b3_oracle,sort_keys=True,separators=(",",":"))):
        raise RuntimeError("CROSS_LANGUAGE_B0_B3_HYPOTHESIS_DIVERGENCE")
    if (json.dumps(warehouse.get("b0_b3_witness_matrix"),
                   sort_keys=True,separators=(",",":")) !=
            json.dumps(matrix_oracle,sort_keys=True,separators=(",",":"))):
        raise RuntimeError("CROSS_LANGUAGE_WITNESS_MATRIX_DIVERGENCE")
    if temporal["pp04_asset_receipts_visible"]==2:
        parsed=audit_pp04_dual_parsers(
            (PAN_TEXT,),(IAEN_TEXT,),expected_plan_count=2,
            expected_planned_count=2,expected_approved_count=1,
            expected_planned_sections=(1,),expected_unplanned_count=2)
        # The internal parser count does not create a registry denominator.
        pp04={k:parsed[k] for k in (
            "planned_count","approved_count","pending_unsplit_count",
            # Preserve BOTH source-local documentary populations. The
            # unplanned count is NOT a negative/terminal case count and
            # cannot be promoted into an independent all-received frame.
            "line_parser_unplanned_entries_source_local",
            "not_included_4221_excluded","item_crosswalk_verified",
            "count_is_source_internal_only","two_parsers_are_independent_sources")}
    else:
        pp04=None
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
