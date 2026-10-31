"""R19 / C14: unselected real procedures are never inspected by this lab."""
from dataclasses import replace
from fractions import Fraction

import pytest

from politics_fantasy.procedural_index_contract import GateError
from politics_fantasy.synthetic_regime_capture_sensitivity import (
    FictionalCaptureStratum, audit_regime_capture, compare_capture_hypotheses,
)

AS_OF = "2026-12-01T12:00:00Z"
CAPTURED = "2026-11-30T12:00:00Z"
REFORM = "2026-10-31"
F = Fraction


def stratum(regime,channel,count,share=F(1,2),**overrides):
    before=regime=="BEFORE_REFORM"
    args=dict(fixture_id=f"SYNTHETIC:{regime}:{channel}",regime=regime,
              channel=channel,first_day="2026-10-01" if before else "2026-10-31",
              last_day="2026-10-30" if before else "2026-11-29",
              locally_captured_at=CAPTURED,observed_published=count,
              assumed_min_capture_share=share,
              assumed_max_capture_share=share,
              legal_calendar_zone="Europe/Madrid")
    args.update(overrides)
    return FictionalCaptureStratum(**args)


def cells(pre=F(1,2),post=F(1,1)):
    return (stratum("BEFORE_REFORM","PAPER",8,pre),
            stratum("BEFORE_REFORM","ELECTRONIC",2,pre),
            stratum("AFTER_REFORM","PAPER",8,post),
            stratum("AFTER_REFORM","ELECTRONIC",12,post))


def audit(rows=None,**args):
    return audit_regime_capture(strata=rows or cells(),
                                reform_on=REFORM,as_of=AS_OF,
                                legal_calendar_zone="Europe/Madrid",**args)


def test_growing_published_count_can_mean_unchanged_true_intake():
    result=audit()
    assert result["periods"]["BEFORE_REFORM"]["visible_source_local_documents"]==10
    assert result["periods"]["AFTER_REFORM"]["visible_source_local_documents"]==20
    for regime in ("BEFORE_REFORM","AFTER_REFORM"):
        assert result["periods"][regime]["hypothetical_intake_lower"]==20
        assert result["periods"][regime]["hypothetical_intake_upper"]==20
    assert result["hypothetical_trend_sign"]=="EQUAL_UNDER_ASSUMPTIONS"
    assert not result["real_causal_mechanism_identified"]
    assert result["AB_scientific_cycles"]==0


def test_same_publications_three_rival_true_trends_due_to_capture_changes():
    equal=audit()
    growing=audit(cells(post=F(1,2)))
    falling=audit(cells(pre=F(1,4)))
    assert growing["hypothetical_trend_sign"]=="RISING_UNDER_ASSUMPTIONS"
    assert falling["hypothetical_trend_sign"]=="FALLING_UNDER_ASSUMPTIONS"
    assert equal["hypothetical_trend_sign"]=="EQUAL_UNDER_ASSUMPTIONS"
    assert compare_capture_hypotheses(left=equal,right=growing)[
        "fictional_registration_trend_not_identified_from_publications"]
    assert compare_capture_hypotheses(left=equal,right=falling)[
        "fictional_registration_trend_not_identified_from_publications"]


def test_partial_coverage_intervals_overlap_so_no_invented_trend_sign():
    rows=tuple(replace(r,assumed_min_capture_share=F(1,4),
                             assumed_max_capture_share=F(1,1)) for r in cells())
    report=audit(rows)
    assert report["hypothetical_trend_sign"]=="NOT_SIGN_IDENTIFIED_UNDER_ASSUMPTIONS"
    assert report["periods"]["BEFORE_REFORM"]["hypothetical_intake_lower"]==10
    assert report["periods"]["BEFORE_REFORM"]["hypothetical_intake_upper"]==40
    assert report["periods"]["AFTER_REFORM"]["hypothetical_intake_lower"]==20
    assert report["periods"]["AFTER_REFORM"]["hypothetical_intake_upper"]==80


def test_zero_lower_capture_bound_never_fabricates_upper_denominator():
    rows=tuple(replace(r,assumed_min_capture_share=F(0,1)) for r in cells())
    report=audit(rows)
    assert report["periods"]["BEFORE_REFORM"]["hypothetical_intake_upper"] is None
    assert report["periods"]["AFTER_REFORM"]["hypothetical_intake_upper"] is None
    assert report["hypothetical_trend_sign"]=="NOT_SIGN_IDENTIFIED_UNDER_ASSUMPTIONS"


def test_positive_capture_at_zero_fraction_is_inconsistent():
    with pytest.raises(GateError,match="POSITIVE_OBSERVATION_IMPOSSIBLE"):
        stratum("BEFORE_REFORM","PAPER",8,F(0))


def test_infeasible_integer_coverage_does_not_fake_a_sharp_bound():
    # M=1, 60%-66.7% share cannot be attained by any integer total N.
    r=stratum("BEFORE_REFORM","PAPER",1,F(3,5),
              assumed_max_capture_share=F(2,3))
    with pytest.raises(GateError,match="INFEASIBLE_INTEGER_COVERAGE_WINDOW"):
        r.partial_intake_bounds()


def test_forbidden_real_labels_and_first_public_promotion():
    with pytest.raises(GateError,match="FICTIONAL_CAPTURE_STRATA_ONLY"):
        stratum("BEFORE_REFORM","PAPER",8,fixture_id="CONGRESO_REAL_121")
    with pytest.raises(GateError,match="FICTIONAL_CAPTURE_STRATA_ONLY"):
        stratum("BEFORE_REFORM","PAPER",8,first_public_at="2026-10-30T00:00:00Z")
    with pytest.raises(GateError,match="FICTIONAL_CAPTURE_STRATA_ONLY"):
        stratum("BEFORE_REFORM","PAPER",8,independent_registry_total=100)


def test_floating_coverage_is_not_a_valid_exact_assumption():
    with pytest.raises(GateError,match="EXACT_SYNTHETIC_COVERAGE_SHARES_REQUIRED"):
        stratum("BEFORE_REFORM","PAPER",8,share=0.5)


def test_missing_channel_and_replayed_identity_do_not_form_complete_panel():
    old=cells()
    with pytest.raises(GateError,match="REPLAYED_SYNTHETIC_STRATUM_ID"):
        audit((old[0],old[0],old[2],old[3]))
    with pytest.raises(GateError,match="MISSING_OR_DUPLICATE_SYNTHETIC_CHANNEL"):
        audit((old[0],replace(old[1],channel="PAPER"),old[2],old[3]))


def test_time_travel_hidden_capture_not_admissible_as_historical_snapshot():
    later=replace(cells()[0],locally_captured_at="2026-12-05T10:00:00Z")
    with pytest.raises(GateError,match="FUTURE_STRATUM_CAPTURE_ASOF_LOOKAHEAD"):
        audit((later,*cells()[1:]))


def test_legal_day_end_not_yet_completed_at_capture():
    with pytest.raises(GateError,match="REGIME_WINDOW_NOT_COMPLETE_AT_CAPTURE"):
        stratum("AFTER_REFORM","PAPER",8,
                locally_captured_at="2026-11-29T23:59:59+01:00")


def test_timezone_mismatch_is_not_coerced_into_common_regime():
    wrong=replace(cells()[2],legal_calendar_zone="Atlantic/Canary")
    with pytest.raises(GateError,match="MIXED_REGIME_LEGAL_CALENDARS"):
        audit((*cells()[:2],wrong,cells()[3]))


def test_windows_must_respect_legal_effective_date():
    invalid=replace(cells()[0],last_day="2026-10-31")
    with pytest.raises(GateError,match="REGIME_WINDOW_SPANS_COMPETENCE_CHANGE"):
        audit((invalid,*cells()[1:]))


def test_channels_must_cover_the_same_exposure_window():
    wrong=replace(cells()[1],first_day="2026-10-02")
    with pytest.raises(GateError,match="INCOMPATIBLE_CHANNEL_EXPOSURE_WINDOWS"):
        audit((cells()[0],wrong,*cells()[2:]))


def test_unequal_period_durations_cannot_be_interpreted_as_count_trends():
    rows=tuple(replace(r,last_day="2026-11-28")
               if r.regime=="AFTER_REFORM" else r for r in cells())
    with pytest.raises(GateError,match="UNEQUAL_REGIME_EXPOSURE_DAYS"):
        audit(rows)


def test_gap_before_reform_not_silently_ignored():
    rows=tuple(replace(r,last_day="2026-10-29")
               if r.regime=="BEFORE_REFORM" else r for r in cells())
    with pytest.raises(GateError,match="NONCONTIGUOUS_REGIME_EXPOSURE_WINDOWS"):
        audit(rows)


def test_comparison_of_different_asof_must_fail_closed():
    left=audit()
    altered=dict(audit(),as_of="2026-12-02T00:00:00Z")
    with pytest.raises(GateError,match="NONCOMPARABLE_HYPOTHETICAL_PERIODS"):
        compare_capture_hypotheses(left=left,right=altered)


def test_publication_projection_change_is_not_observational_equivalence():
    left=audit()
    changed=list(cells())
    changed[2]=replace(changed[2],observed_published=10)
    report=audit(tuple(changed))
    eq=compare_capture_hypotheses(left=left,right=report)
    assert not eq["same_visible_projection"]
    assert not eq["fictional_registration_trend_not_identified_from_publications"]


def test_comparator_rejects_forged_trend_without_bound_change():
    report=audit()
    mutated=dict(report,hypothetical_trend_sign="RISING_UNDER_ASSUMPTIONS")
    with pytest.raises(GateError,match="INCONSISTENT_SYNTHETIC_REPORT_TREND"):
        compare_capture_hypotheses(left=report,right=mutated)


def test_comparator_rejects_real_evidence_promotion_and_negative_bounds():
    report=audit()
    with pytest.raises(GateError,match="INVALID_SYNTHETIC_REPORT_PROVENANCE"):
        compare_capture_hypotheses(
            left=report,right=dict(report,real_registration_population_attested=True))
    falsified=dict(report,periods={
        **report["periods"],
        "BEFORE_REFORM":{
            **report["periods"]["BEFORE_REFORM"],
            "hypothetical_intake_lower":-1,
        },
    })
    with pytest.raises(GateError,match="INCONSISTENT_SYNTHETIC_REPORT_BOUNDS"):
        compare_capture_hypotheses(left=report,right=falsified)


def test_comparator_rejects_nested_pollution_or_wrong_types():
    report=audit()
    before=report["periods"]["BEFORE_REFORM"]
    polluted=dict(report,periods={
        **report["periods"], "BEFORE_REFORM":dict(before,individual_case="REAL")})
    with pytest.raises(GateError,match="INVALID_SYNTHETIC_REPORT_PERIODS"):
        compare_capture_hypotheses(left=report,right=polluted)
    malformed=dict(report,legal_calendar_zone=[])
    with pytest.raises(GateError,match="INVALID_SYNTHETIC_REPORT_PROVENANCE"):
        compare_capture_hypotheses(left=report,right=malformed)
