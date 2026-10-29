"""Exact aggregate-only attrition sensitivity, NOT an effect estimate.

Six included arm counts and total short-session exclusions come from a published
2026 experiment. The assignment of excluded users to arms is NOT reported.
We assume for this *conditional* sensitivity analysis that all 13 excluded
registrants belonged to one of the six arms. No participant data are used.
"""
from fractions import Fraction
from itertools import combinations
from math import comb

SOURCE = 'Karabiber & Gurol (2026), Acta Psychologica 266:106908, Sec 4.2/Table 2'
INCLUDED = (36, 37, 36, 36, 37, 37)
EXCLUDED = 13


def allocations(total, groups):
    """Generate all weak compositions of `total` into `groups` bins."""
    if not (isinstance(total, int) and not isinstance(total, bool) and 0 <= total <= 20
            and isinstance(groups, int) and not isinstance(groups, bool) and 2 <= groups <= 6):
        raise ValueError('UNSUPPORTED_ENUMERATION')
    for bars in combinations(range(total + groups - 1), groups - 1):
        p = (-1,) + bars + (total + groups - 1,)
        yield tuple(p[i + 1] - p[i] - 1 for i in range(groups))


def analyze(included=INCLUDED, excluded=EXCLUDED):
    if tuple(included) != INCLUDED or excluded != EXCLUDED or type(excluded) is not int:
        raise ValueError('PUBLICATION_AGGREGATES_ONLY')
    best = Fraction(-1, 1)
    witness = None
    enumerated = 0
    for allocation in allocations(excluded, len(included)):
        rates = [Fraction(n, n + e) for n, e in zip(included, allocation)]
        gap = max(rates) - min(rates)
        enumerated += 1
        if gap > best:
            best, witness = gap, allocation
    assert enumerated == comb(excluded + len(included) - 1, len(included) - 1)
    return {
        'schema': 'pfl.published.aggregate.attrition.sensitivity.v1',
        'source': SOURCE,
        'included_by_arm': list(included),
        'excluded_unallocated': excluded,
        'total_included': sum(included),
        'conditional_total_registrants': sum(included) + excluded,
        'conditional_overall_exclusion_share': float(Fraction(excluded, sum(included)+excluded)),
        'allocations_enumerated': enumerated,
        'max_feasible_arm_retention_difference': float(best),
        'exact_max_gap_fraction': str(best),
        'one_witness_excluded_by_arm': list(witness),
        'causal_claim': False,
        'randomization_roster_verified': False,
        'per_arm_excluded_counts_known': False,
        'assumptions': 'Every one of the 13 excluded registrants belonged to one of the six arms; per-arm allocation is unknown.',
        'interpretation': 'Feasibility bound for missingness imbalance only; not a treatment effect, bias estimate, or ITT.'
    }


if __name__ == '__main__':
    import json
    print(json.dumps(analyze(), indent=2))
