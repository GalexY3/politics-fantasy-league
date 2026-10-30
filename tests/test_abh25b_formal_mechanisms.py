"""Validate model contracts and completed outputs; model falsifications are NOT CI failures."""
import json,math,sys,unittest
from pathlib import Path
from research.ABH25B_20261030 import c12_c26_formal_mechanisms as model

class ContractChecks(unittest.TestCase):
    def test_unique_independent_scenarios_and_seed_schedule(self):
        self.assertEqual(sorted(model.MODELS),list(range(12,27)))
        self.assertEqual(len(set(model.MODELS.values())),15)
        self.assertEqual(set(model.DIRECTIONS),set(model.MODELS))
        self.assertEqual(model.N_REPS,200)
    def test_falsifying_nonfinite_model_output_is_rejected(self):
        prior=model.MODELS[12]
        try:
            model.MODELS[12]=lambda rng:(float('nan'),0.0,0.0)
            with self.assertRaisesRegex(ValueError,"NONFINITE_MODEL_OUTPUT"):
                model.evaluate(12)
        finally:model.MODELS[12]=prior
    def test_unknown_model_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"SCENARIO_UNKNOWN"):
            model.evaluate(99)

def check_file(path):
    obj=json.loads(Path(path).read_text())
    if obj.get("NOT_EMPIRICAL_VALIDATION") is not True:
        raise ValueError("CLAIM_MISLABELED")
    arr=obj.get("results")
    if not isinstance(arr,list) or len(arr)!=15 or obj["total_executed_scenarios"]!=15:
        raise ValueError("INCOMPLETE_OUTPUT")
    ids=set()
    for row in arr:
        n=int(row["cycle"].split("C")[-1])
        if n in ids or n not in range(12,27):raise ValueError("DUPLICATE_SCENARIO")
        ids.add(n)
        if row["paired_replicates"]!=200 or row["scientific_grade"]!="0/3":
            raise ValueError("INVALID_SCOPE")
        if row["placebo_max_difference"]>1e-12:
            raise ValueError("INVALID_PLACEBO")
        if row["status"] not in ("SUPPORTED_INSIDE_GENERATIVE_MODEL",
            "FALSIFIED_INSIDE_GENERATIVE_MODEL","INCONCLUSIVE_MONTE_CARLO"):
            raise ValueError("INVALID_MODEL_STATUS")
        if any(not math.isfinite(row[k]) for k in (
            "intervention_mean","rival_mean","difference_mean","monte_carlo_se",
            "mc95_lower","mc95_upper")):raise ValueError("NONFINITE_RESULT")
    print("ABH25B_15_FORMAL_DISTINCT_RESULTS_STRUCTURALLY_VALID")
    print(json.dumps({"results":arr},indent=2,sort_keys=True))
if __name__=="__main__":
    if len(sys.argv)==2:check_file(sys.argv[1])
    else:unittest.main()
