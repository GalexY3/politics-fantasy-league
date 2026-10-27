from datetime import datetime, timezone
from hashlib import sha256
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from politics_fantasy.events import PoliticalEvent, as_utc, unique_events
from politics_fantasy.scoring import person_week_points, league_points
from politics_fantasy.forecast import historical_rate, rolling_origin_splits
from politics_fantasy.simulation import simulate_auction, gini


HASH = sha256(b'FAKE_SYNTHETIC_DOCUMENT').hexdigest()


def dt(day):
    return datetime(2026, 1, day, tzinfo=timezone.utc)


def event(id, pub, kind='speech_recorded', who=('P1',), occ=2, ver='v1'):
    return PoliticalEvent(id, kind, dt(occ), dt(pub), tuple(who),
                          'https://example.invalid/synthetic', HASH, ver, {})


def test_future_publication_is_not_usable():
    e = event('one', 7, occ=2)
    assert not e.observable_at(dt(6))
    assert e.observable_at(dt(7))


def test_round_points_de_dup_caps_and_publication():
    xs = [event(f'e{i}', 3, occ=2) for i in range(5)]
    xs += [event('not_public', 9, occ=2), event('other', 3, who=('P2',))]
    xs += [xs[0]]
    assert person_week_points(xs, person_id='P1', start=dt(1), end=dt(5),
                              knowledge_cutoff=dt(8)) == 6.0
    assert league_points(xs, lineup=('P1','P2'), start=dt(1), end=dt(5),
                         cutoff=dt(8)) == 8.0


def test_forecast_disallows_future_publication_leakage():
    xs = [event('a', 3, occ=2), event('b', 7, occ=4)]
    p = historical_rate(xs, person_id='P1', start=dt(1), as_of=dt(6), exposure=8)
    assert p.observed_history == 1
    assert abs(p.event_rate - 0.2) < 1e-12


def test_clocks_and_conflict_rejected():
    with pytest.raises(ValueError):
        as_utc(datetime(2026, 1, 1))
    with pytest.raises(ValueError):
        event('bad', 1, occ=3)
    with pytest.raises(ValueError):
        unique_events([event('dup', 3, who=('P1',)), event('dup', 3, who=('P2',))])


def test_sequential_splits_nonoverlap():
    splits = list(rolling_origin_splits(['2026-01-05','2026-01-12',
                                        '2026-01-19','2026-01-26'], min_train=2))
    assert len(splits) == 2
    assert all(max(tr) < min(te) for tr, te in splits)


def test_game_simulation_reproducible_but_not_evidence():
    assert simulate_auction(seed=4) == simulate_auction(seed=4)
    assert 0 <= gini([1, 2, 3]) <= 1
    assert 0.2 < simulate_auction(seed=4).top_20_percent_value_share < 1


def test_counterfactual_change_in_hidden_future_does_not_change_forecast():
    """Operational AB-M037 style leakage invariance on the demonstrator."""
    published=[event('visible',3,occ=2)]
    invisible=[event('private_A',8,occ=4)]
    alternative=[event('private_B',9,occ=4),event('private_C',10,occ=5)]
    kwargs=dict(person_id='P1',start=dt(1),as_of=dt(6),exposure=8)
    assert historical_rate(published+invisible,**kwargs)==historical_rate(
        published+alternative,**kwargs)


def test_public_revisions_count_one_event_and_preserve_historical_cutoff():
    original = event('revised', 3)
    revised = event('revised', 7, kind='initiative_registered', ver='v2')
    xs = [revised, original, original]
    score_args = dict(person_id='P1', start=dt(1), end=dt(5))
    assert person_week_points(xs, knowledge_cutoff=dt(6), **score_args) == 2.0
    assert person_week_points(xs, knowledge_cutoff=dt(8), **score_args) == 3.0
    for cutoff in (dt(6), dt(8)):
        prediction = historical_rate(xs, person_id='P1', start=dt(1), as_of=cutoff, exposure=8)
        assert prediction.observed_history == 1
        assert prediction.event_rate == pytest.approx(0.2)
    # The archive-level deduplicator must still preserve both source revisions.
    assert len(unique_events(xs)) == 2


@pytest.mark.parametrize('revised', [
    event('revised', 7, who=('P2',), ver='v2'),
    event('revised', 7, occ=6, ver='v2'),
])
def test_revision_resolved_before_person_and_event_time_filters(revised):
    xs = [event('revised', 3), revised]
    assert person_week_points(xs, person_id='P1', start=dt(1), end=dt(5),
                              knowledge_cutoff=dt(8)) == 0.0
    # A corrected occurrence outside the requested history must not resurrect v1.
    prediction = historical_rate(xs, person_id='P1', start=dt(1), as_of=dt(8), exposure=8)
    assert prediction.observed_history == (1 if revised.person_ids == ('P1',) else 0)


def test_revision_outside_history_does_not_resurrect_original():
    xs = [event('revised', 3, occ=2), event('revised', 7, occ=1, ver='v2')]
    prediction = historical_rate(xs, person_id='P1', start=dt(2), as_of=dt(8), exposure=8)
    assert prediction.observed_history == 0


def test_ambiguous_public_revisions_fail_instead_of_double_counting():
    xs = [event('revised', 3), event('revised', 3, ver='v2')]
    with pytest.raises(ValueError, match='Ambiguous public revisions'):
        person_week_points(xs, person_id='P1', start=dt(1), end=dt(5), knowledge_cutoff=dt(8))
    with pytest.raises(ValueError, match='Ambiguous public revisions'):
        historical_rate(xs, person_id='P1', start=dt(1), as_of=dt(8), exposure=8)
