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
                    partial_identification: dict | None) -> dict:
    runner=Path(__file__).resolve().parents[2]/"scripts"/"scientific_integration_warehouse.mjs"
    request={"cut":cut,"scenario":scenario,"sha256":_sha(FAKE_PARITY),
             "assets":assets,"experiment":experiment,"timeline":timeline,
             "partial_identification":partial_identification}
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
        "observational_equivalence_experiment",
        "bitemporal_actor_event_equivalence",
        "partial_identification_oracle",
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
            or data.get("partial_identification_oracle") !=
               (None if cut == "early" else
                _partial_identification(partial_identification))):
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
    warehouse=_node_warehouse(cut=cut,scenario=scenario,assets=assets,
                              experiment=experiment,timeline=timeline,
                              partial_identification=partial_wire)
    if warehouse.get("bitemporal_actor_event_equivalence") != bitemporal:
        raise RuntimeError("CROSS_LANGUAGE_BITEMPORAL_CONTRACT_DIVERGENCE")
    if warehouse.get("partial_identification_oracle") != partial_oracle:
        raise RuntimeError("CROSS_LANGUAGE_S3_PARTIAL_IDENTIFICATION_DIVERGENCE")
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
