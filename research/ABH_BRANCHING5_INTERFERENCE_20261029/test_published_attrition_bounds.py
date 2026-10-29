import unittest
from fractions import Fraction
from math import comb
from published_attrition_bounds import analyze, allocations


class PublishedAggregateAttritionTests(unittest.TestCase):
    def test_original_group_counts_and_total(self):
        r = analyze()
        self.assertEqual(r['included_by_arm'], [36, 37, 36, 36, 37, 37])
        self.assertEqual(r['total_included'], 219)
        self.assertEqual(r['conditional_total_registrants'], 232)

    def test_exact_enumeration_count(self):
        self.assertEqual(analyze()['allocations_enumerated'], comb(18, 5))
        self.assertEqual(comb(18, 5), 8568)

    def test_closed_form_extreme_bound(self):
        r = analyze()
        self.assertEqual(r['exact_max_gap_fraction'], str(Fraction(13, 49)))
        self.assertAlmostEqual(r['max_feasible_arm_retention_difference'], 13/49)

    def test_witness_sum_and_feasible_extreme(self):
        r = analyze(); a = r['one_witness_excluded_by_arm']
        self.assertEqual(len(a), 6)
        self.assertEqual(sum(a), 13)
        self.assertEqual(max(a), 13)
        self.assertEqual(min(a), 0)

    def test_all_weak_compositions_sum_and_unique(self):
        all_rows = list(allocations(3, 3))
        self.assertEqual(len(all_rows), 10)
        self.assertEqual(len(set(all_rows)), 10)
        self.assertTrue(all(sum(row) == 3 and min(row) >= 0 for row in all_rows))

    def test_no_fake_counts_or_large_unbounded_enumeration(self):
        with self.assertRaisesRegex(ValueError, 'PUBLICATION_AGGREGATES_ONLY'):
            analyze(included=(36, 37, 37, 36, 37, 37))
        with self.assertRaisesRegex(ValueError, 'UNSUPPORTED_ENUMERATION'):
            list(allocations(100, 6))

    def test_explicit_noncausal_and_unknown_arm_exclusions(self):
        r = analyze()
        self.assertIs(r['causal_claim'], False)
        self.assertIs(r['randomization_roster_verified'], False)
        self.assertIs(r['per_arm_excluded_counts_known'], False)
        self.assertAlmostEqual(r['conditional_overall_exclusion_share'], 13/232)


if __name__ == '__main__':
    unittest.main(verbosity=2)
