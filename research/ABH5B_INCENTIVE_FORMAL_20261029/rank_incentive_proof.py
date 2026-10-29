"""Exact rational audit of a *hypothetical* single-prize forecasting contest.

Not a PFL product feature or empirical model. Two forecasters, one binary
outcome, public rival report q fixed, subjective belief p. Comparing a
winner-take-all *deterministic* quadratic-score ranking to a quadratic-score
lottery. Witkowski et al., Incentive-Compatible Forecasting Competitions,
Management Science (2023), DOI 10.1287/mnsc.2022.4410.
"""
from fractions import Fraction as F
import json


def probability(x):
    if type(x) is not F or not 0 <= x <= 1:
        raise ValueError('FRACTION_PROBABILITY_REQUIRED')
    return x


def score(r, y):
    probability(r)
    if type(y) is not int or y not in (0, 1):
        raise ValueError('BINARY_OUTCOME_REQUIRED')
    return 1-(r-F(y))**2


def deterministic_win(r, q, y):
    """Win probability conditional on outcome, with fair split of exact ties."""
    delta=score(r,y)-score(q,y)
    return F(1) if delta>0 else F(0) if delta<0 else F(1,2)


def lottery_win(r, q, y):
    """Two-player quadratic lottery: probability 1/2 + (score_i-score_j)/2.

    This is an expository, single-event special case of the ELF idea, not a
    claim to implement the published full algorithm or a deployed product.
    """
    return F(1,2)+(score(r,y)-score(q,y))/2


def expected_win(p, r, q, mechanism):
    probability(p)
    return (1-p)*mechanism(r,q,0)+p*mechanism(r,q,1)


def exact_truthfulness_gap(p, r, q):
    """Identity: E[ELF win at r=p] - E[ELF win at r] == (p-r)^2/2."""
    for x in (p,r,q):probability(x)
    observed=expected_win(p,p,q,lottery_win)-expected_win(p,r,q,lottery_win)
    algebraic=(p-r)**2/2
    if observed!=algebraic:raise AssertionError('ELF_IDENTITY_FAIL')
    return algebraic


def audit():
    p,q,truth,deviation=F(11,20),F(3,5),F(11,20),F(61,100)
    deterministic_truth=expected_win(p,truth,q,deterministic_win)
    deterministic_deviate=expected_win(p,deviation,q,deterministic_win)
    elf_truth=expected_win(p,truth,q,lottery_win)
    elf_deviate=expected_win(p,deviation,q,lottery_win)
    return {
      'schema':'pfl.ab5b.hypothetical.incentive.formal.v1',
      'source':'https://doi.org/10.1287/mnsc.2022.4410',
      'subjective_belief':str(p),'fixed_rival_report':str(q),
      'truthful_report':str(truth),'strategic_report':str(deviation),
      'deterministic_winning_probability_truthful':str(deterministic_truth),
      'deterministic_winning_probability_deviation':str(deterministic_deviate),
      'deviation_gain_in_deterministic_win_probability':str(deterministic_deviate-deterministic_truth),
      'lottery_winning_probability_truthful':str(elf_truth),
      'lottery_winning_probability_deviation':str(elf_deviate),
      'truthful_advantage_in_lottery':str(exact_truthfulness_gap(p,deviation,q)),
      'formal_identity':'E_P[LotteryWin(p,q,X)] - E_P[LotteryWin(r,q,X)] = (r-p)^2/2 >= 0',
      'no_claims':['not a behavioral experiment','not a PFL implemented prize scheme',
          'no claim monetary rewards currently exist in PFL',
          'not proof against every competition scoring rule',
          'does not determine preferences for public recognition',
          'not original theoretical novelty; result anticipated by Witkowski et al.'],
      'scoped_decision':'Hypothetical two-player single-event mechanisms only; require product-scope decision and broader proof before deployment',
      'real_human_rows':0,'scientific_grade':'0/3'}


if __name__=='__main__':
    print(json.dumps(audit(),indent=2))
