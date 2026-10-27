"""Fixture-only tests for identity reconciliation. No official vote is included."""
import json
import unittest
from politics_fantasy.identity_reconcile import reconcile_vote, roster_mapping

ROSTER=b"1|Apellido Uno|Ana|0\n2|Apellido Dos|Belen|0\n"
ROWS=[{"diputado":"Apellido Uno, Ana","voto":"Sí"},
      {"diputado":"Apellido Dos, Belen","voto":"No"},
      {"diputado":"Apellido Tres, Carmen","voto":"Sí"}]
TOTAL={"afavor":2,"enContra":1,"abstenciones":0,"noVotan":0}
ST={"si":2,"no":1,"abstencion":0,"noVota":0}

def official(rows=None,total=None):
    return json.dumps({"data":{"totales":total if total is not None else TOTAL,
                                "votaciones":rows if rows is not None else ROWS}},ensure_ascii=False).encode()

def derivative(votes=None,total=None):
    return {"id":"synthetic","totales":total if total is not None else ST,
            "votos":votes if votes is not None else {"S":"1","N":"2"}}

class ReconciliationTests(unittest.TestCase):
    def test_unresolved_category_counts_and_privacy(self):
        x=reconcile_vote(official(),derivative(),ROSTER)
        self.assertEqual(x["unmatched_names_by_option"]["S"],1)
        self.assertTrue(x["secondary_codes_equal_resolved_official"])
        self.assertEqual(x["individual_match_status"],"INCOMPLETE_UNMATCHED")
        self.assertEqual(x["roster_resolution_coverage"],{"resolved":2,"nominal_rows":3,"unmatched":1})
        self.assertNotIn("Apellido",json.dumps(x))
    def test_empty_resolved_sets_are_not_a_complete_identity_match(self):
        rows=[{"diputado":"Desconocido, Uno","voto":"Sí"}]
        total={"afavor":1,"enContra":0,"abstenciones":0,"noVotan":0}
        sec={"si":1,"no":0,"abstencion":0,"noVota":0}
        x=reconcile_vote(official(rows,total),derivative({},sec),ROSTER)
        self.assertTrue(x["secondary_codes_equal_resolved_official"])
        self.assertEqual(x["individual_match_status"],"INCOMPLETE_UNMATCHED")
        self.assertEqual(x["roster_resolution_coverage"]["resolved"],0)
    def test_complete_matching_codes_require_full_coverage(self):
        rows=ROWS[:2]
        total={"afavor":1,"enContra":1,"abstenciones":0,"noVotan":0}
        sec={"si":1,"no":1,"abstencion":0,"noVota":0}
        x=reconcile_vote(official(rows,total),derivative(total=sec),ROSTER)
        self.assertEqual(x["individual_match_status"],"SAME_CODE_SETS")
        self.assertEqual(x["roster_resolution_coverage"]["unmatched"],0)
    def test_incomplete_and_mismatch_retains_both_signals(self):
        x=reconcile_vote(official(),derivative({"S":"2","N":"1"}),ROSTER)
        self.assertEqual(x["individual_match_status"],"INCOMPLETE_UNMATCHED")
        self.assertFalse(x["secondary_codes_equal_resolved_official"])
    def test_complete_names_but_inconsistent_nominal_totals_are_not_full_match(self):
        x=reconcile_vote(official(ROWS[:2]),derivative(),ROSTER)
        self.assertEqual(x["individual_match_status"],"NOMINAL_TOTAL_MISMATCH")
    def test_exact_upstream_name_rule(self):
        self.assertEqual(roster_mapping(ROSTER)["Apellido Uno, Ana"],"1")
    def test_code_swap_detected(self):
        self.assertFalse(reconcile_vote(official(),derivative({"S":"2","N":"1"}),ROSTER)["secondary_codes_equal_resolved_official"])
    def test_secondary_aggregate_mismatch(self):
        d=derivative(total={"si":1,"no":2,"abstencion":0,"noVota":0})
        self.assertFalse(reconcile_vote(official(),d,ROSTER)["secondary_totals_match_official"])
    def test_duplicate_secondary_code(self):
        with self.assertRaises(ValueError):
            reconcile_vote(official(),derivative({"S":"1","N":"1"}),ROSTER)
    def test_duplicate_roster_name(self):
        with self.assertRaises(ValueError):reconcile_vote(official(),derivative(),ROSTER+ROSTER)
    def test_duplicate_roster_code(self):
        with self.assertRaises(ValueError):reconcile_vote(official(),derivative(),ROSTER+b"1|Otra|Persona|0\n")
    def test_duplicate_official_name(self):
        with self.assertRaises(ValueError):reconcile_vote(official(ROWS+[ROWS[0]]),derivative(),ROSTER)
    def test_invalid_vote_label(self):
        with self.assertRaises(ValueError):reconcile_vote(official([{"diputado":"X","voto":"maybe"}]),derivative(),ROSTER)
    def test_negative_official_total(self):
        with self.assertRaises(ValueError):reconcile_vote(official(total={**TOTAL,"afavor":-1}),derivative(),ROSTER)
    def test_boolean_total_not_integer(self):
        with self.assertRaises(ValueError):reconcile_vote(official(total={**TOTAL,"afavor":True}),derivative(),ROSTER)
    def test_no_nominal_not_misreported_as_zero_unmatched(self):
        x=reconcile_vote(official([]),derivative(),ROSTER)
        self.assertEqual(x["status"],"NO_ORIGINAL_NOMINAL_ROWS")
        self.assertIsNone(x["unmatched_names_by_option"])
        self.assertIsNone(x["roster_resolution_coverage"])
    def test_original_nominal_count_disagreement(self):
        x=reconcile_vote(official(ROWS[:2]),derivative(),ROSTER)
        self.assertFalse(x["official_nominal_counts_match_official_totals"])
