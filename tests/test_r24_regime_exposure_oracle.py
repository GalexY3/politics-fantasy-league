"""R24 prepatch falsifiers: synthetic exposure and channel identity.

These are NOT reports about Spanish institutions. No real records or outcomes.
"""
from fractions import Fraction

import pytest

from politics_fantasy.procedural_index_contract import GateError
from politics_fantasy.synthetic_regime_capture_sensitivity import (
    FictionalCaptureStratum, audit_regime_capture, compare_capture_hypotheses,
)

REFORM = "2026-10-31"
AS_OF = "2026-12-02T12:00:00Z"
CAPTURE = "2026-11-30T12:00:00Z"
F = Fraction


def report(*, short=False, published=((8, 2), (8, 12)),
           before_share=F(1, 2), after_share=F(1, 1),
           capture=CAPTURE):
    before_first, after_last = (
        ("2026-10-30", "2026-10-31") if short
        else ("2026-10-01", "2026-11-29")
    )
    rows = []
    for regime, counts, first, last, share in (
        ("BEFORE_REFORM", published[0], before_first, "2026-10-30",
         before_share),
        ("AFTER_REFORM", published[1], "2026-10-31", after_last,
         after_share),
    ):
        for channel, count in zip(("PAPER", "ELECTRONIC"), counts):
            rows.append(FictionalCaptureStratum(
                fixture_id="SYNTHETIC:R24:" + regime + ":" + channel,
                regime=regime, channel=channel, first_day=first, last_day=last,
                locally_captured_at=capture, observed_published=count,
                assumed_min_capture_share=share, assumed_max_capture_share=share,
                legal_calendar_zone="Europe/Madrid",
            ))
    return audit_regime_capture(
        strata=tuple(rows), reform_on=REFORM, as_of=AS_OF,
        legal_calendar_zone="Europe/Madrid",
    )


def test_different_exposure_windows_must_not_be_called_same_projection():
    long_window = report()
    short_window = report(short=True, after_share=F(1, 2))
    # Both reports individually pass all R19 date tests, sums match, but a
    # one-day risk window is NOT the same evidence as a 30-day risk window.
    with pytest.raises(GateError, match="NONCOMPARABLE_EXPOSURE_WINDOWS"):
        compare_capture_hypotheses(left=long_window, right=short_window)


def test_same_totals_different_paper_electronic_counts_are_not_equivalent():
    left = report()
    right = report(published=((5, 5), (15, 5)), after_share=F(1, 2))
    assert left["periods"]["BEFORE_REFORM"]["visible_source_local_documents"] == 10
    assert right["periods"]["BEFORE_REFORM"]["visible_source_local_documents"] == 10
    assert left["periods"]["AFTER_REFORM"]["visible_source_local_documents"] == 20
    assert right["periods"]["AFTER_REFORM"]["visible_source_local_documents"] == 20
    result = compare_capture_hypotheses(left=left, right=right)
    assert result["same_visible_projection"] is False
    assert result["same_aggregated_totals_only"] is True
    assert result["fictional_registration_trend_not_identified_from_publications"] is False


def test_same_numbers_but_new_capture_is_not_same_source_snapshot():
    left = report()
    right = report(capture="2026-12-01T12:00:00Z",
                   after_share=F(1, 2))
    with pytest.raises(GateError, match="NONCOMPARABLE_CAPTURE_IDENTITY"):
        compare_capture_hypotheses(left=left, right=right)


def test_same_exposure_and_channel_counts_with_other_capture_shares_is_valid():
    a, b = report(), report(after_share=F(1, 2))
    r = compare_capture_hypotheses(left=a, right=b)
    assert r["same_visible_projection"]
    assert r["different_hypothetical_trend_sign"]
    assert r["fictional_registration_trend_not_identified_from_publications"]


def test_malformed_channel_sum_is_not_a_replayable_report():
    r = report()
    before = r["periods"]["BEFORE_REFORM"]
    # New output must include the exact channel-level projection so this
    # mutation can be tested without touching any original source.
    assert "visible_by_channel" in before
    bad = dict(r, periods={
        **r["periods"],
        "BEFORE_REFORM": {
            **before, "visible_by_channel": {
                **before["visible_by_channel"], "PAPER": 9,
            },
        },
    })
    with pytest.raises(GateError, match="INCONSISTENT_CHANNEL_PROJECTION"):
        compare_capture_hypotheses(left=r, right=bad)


def test_replayed_report_with_capture_before_period_ends_is_quarantined():
    r = report()
    post = r["periods"]["AFTER_REFORM"]
    polluted = dict(r, periods={
        **r["periods"],
        "AFTER_REFORM": {
            **post,
            "capture_at_by_channel": {
                **post["capture_at_by_channel"],
                "PAPER": "2026-11-29T23:59:59+01:00",
            },
        },
    })
    with pytest.raises(GateError, match="SYNTHETIC_REPORT_CAPTURE_BEFORE_PERIOD_COMPLETED"):
        compare_capture_hypotheses(left=r, right=polluted)


def test_replayed_report_with_future_capture_is_quarantined():
    r = report()
    post = r["periods"]["AFTER_REFORM"]
    polluted = dict(r, periods={
        **r["periods"],
        "AFTER_REFORM": {
            **post,
            "capture_at_by_channel": {
                **post["capture_at_by_channel"],
                "ELECTRONIC": "2026-12-03T12:00:00Z",
            },
        },
    })
    with pytest.raises(GateError, match="SYNTHETIC_CAPTURE_AFTER_REPORT_KNOWLEDGE_CUT"):
        compare_capture_hypotheses(left=r, right=polluted)


def test_forged_fixture_identity_cannot_pass_as_same_capture():
    r = report()
    post = r["periods"]["AFTER_REFORM"]
    bad = dict(r, periods={
        **r["periods"],
        "AFTER_REFORM": {
            **post,
            "synthetic_fixture_ids_by_channel": {
                **post["synthetic_fixture_ids_by_channel"],
                "PAPER": r["periods"]["BEFORE_REFORM"]["synthetic_fixture_ids_by_channel"]["PAPER"],
            },
        },
    })
    with pytest.raises(GateError, match="INVALID_SYNTHETIC_CAPTURE_IDENTITY"):
        compare_capture_hypotheses(left=r, right=bad)


def test_channel_sum_replay_refuses_nested_private_fields():
    r = report()
    p = r["periods"]["AFTER_REFORM"]
    bad = dict(r, periods={
        **r["periods"], "AFTER_REFORM": {
            **p, "visible_by_channel": {
                **p["visible_by_channel"],
                "PRIVATE_CASE_ID": 123,
            },
        },
    })
    with pytest.raises(GateError, match="INVALID_SYNTHETIC_CHANNEL_PROJECTION"):
        compare_capture_hypotheses(left=r, right=bad)
