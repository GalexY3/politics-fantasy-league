"""C04 synthetic Rule invariants preregistered before running against original Git blob."""
from datetime import datetime, timezone
from hashlib import sha256
from math import isfinite
import pytest
from politics_fantasy.events import PoliticalEvent
from politics_fantasy.scoring import Rule, DEMO_RULE, person_week_points


def dt(d):
    return datetime(2026,1,d,tzinfo=timezone.utc)


def synthetic_event():
    return PoliticalEvent('synthetic-1','speech_recorded',dt(2),dt(3),('FICTIVE-A',),
                          'https://example.invalid/synthetic',sha256(b'fake').hexdigest(),'v1',{})


def score(rule):
    return person_week_points([synthetic_event()],person_id='FICTIVE-A',
                              start=dt(1),end=dt(5),knowledge_cutoff=dt(8),rule=rule)


def test_negative_cap_rejected_before_negative_score():
    with pytest.raises(ValueError,match='INVALID_RULE_CAP'):
        Rule('test', {'speech_recorded':2.0}, {'speech_recorded':-1})


def test_nonfinite_weight_rejected_before_infinite_score():
    with pytest.raises(ValueError,match='INVALID_RULE_WEIGHT'):
        Rule('test', {'speech_recorded':float('inf')}, {'speech_recorded':1})


def test_mismatched_weight_cap_keys_rejected_at_construction():
    with pytest.raises(ValueError,match='RULE_KIND_SET_MISMATCH'):
        Rule('test', {'speech_recorded':2.0}, {})


def test_boolean_cap_rejected_as_noninteger_semantics():
    with pytest.raises(ValueError,match='INVALID_RULE_CAP'):
        Rule('test', {'speech_recorded':2.0}, {'speech_recorded':True})


def test_caller_mutation_does_not_change_frozen_rule_output():
    weights={'speech_recorded':2.0}
    caps={'speech_recorded':1}
    rule=Rule('test',weights,caps)
    before=score(rule)
    weights['speech_recorded']=9000.0
    caps['speech_recorded']=0
    assert score(rule)==before==2.0


def test_direct_mutation_cannot_change_frozen_rule():
    rule=Rule('test', {'speech_recorded':2.0},{'speech_recorded':1})
    with pytest.raises(TypeError):
        rule.weights['speech_recorded']=20.0


def test_original_default_contract_positive():
    assert score(DEMO_RULE)==2.0
    assert isfinite(score(DEMO_RULE))


def test_valid_zero_cap_intentionally_disables_kind():
    assert score(Rule('disable',{'speech_recorded':2.0},{'speech_recorded':0}))==0.0
