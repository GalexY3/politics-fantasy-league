"""AB10 P01: strictly synthetic oracles. Do not run before freeze commit."""
import json

import pytest

from scripts.ab10_candidate_rank_benchmark import (
    BenchmarkError, CONFIRMATION_SEEDS, DECOYS, N, SEEDS,
    decision, idf_weights, measure, norm, rank_three,
    synthetic_corpus, weighted_jaccard,
)


def test_generator_closed_population_and_known_synthetic_oracle():
    data = synthetic_corpus(4711)
    assert data["ground_truth_count"] == 198
    assert len(data["plan"]) == N
    assert len(data["report"]) == N + DECOYS
    assert data == synthetic_corpus(4711)
    assert all(r["synthetic_id"].startswith("FICTIONAL-") for r in data["report"])
    assert set(x["true_plan_id"] for x in data["report"] if x["true_plan_id"]) == {
        r["synthetic_id"] for r in data["plan"]
    }
    assert all("Ministerio de" not in r["title"] for r in data["report"])


def test_baselines_see_exactly_same_source_strings_and_k():
    titles = ("REAL DECRETO DEL PROTOCOLO LUMBRE",
              "LEY DEL PROTOCOLO ARISTA", "LEY DEL PROTOCOLO NACAR",
              "REAL DECRETO DEL PROTOCOLO CORAL")
    for alg in ("B0_SEQUENCE", "B1_IDF", "B2_JACCARD", "ABLATION_NO_IDF"):
        choice = rank_three("LEY DEL PROTOCOLO ARISTA", titles, algorithm=alg)
        assert len(choice) == 3
        assert len(set(choice)) == 3
        assert choice[0] == 1


def test_idf_has_no_ground_truth_or_status_input():
    a = frozenset(("ALFA", "BETA"))
    b = frozenset(("ALFA", "GAMMA"))
    weights = idf_weights((a, b))
    assert weights["ALFA"] < weights["BETA"]
    assert weighted_jaccard(a, a, weights) == 1
    assert weighted_jaccard(a, b, weights) < 1


def test_uniform_jaccard_and_no_idf_ablation_equal_on_same_corpus():
    data = synthetic_corpus(4711)
    a = measure(data, "B2_JACCARD")
    b = measure(data, "ABLATION_NO_IDF")
    assert a["recall_at_3"] == b["recall_at_3"]
    assert a["recall_at_1"] == b["recall_at_1"]
    assert all(0 <= x <= 1 for x in a["by_stratum_recall_at_3"].values())


def test_inadmissible_seed_or_algorithm_fails_closed():
    with pytest.raises(BenchmarkError, match="SEED_NOT_PREDECLARED"):
        synthetic_corpus(994)
    with pytest.raises(BenchmarkError, match="ALGORITHM_OR_CANDIDATES"):
        rank_three("LEY FICTICIA", ("A", "B", "C"), algorithm="FAKE_BEST")


def test_normalization_equally_expands_royal_decree_shorthand():
    assert norm("RD de coordinación ÁREA") == "REAL DECRETO DE COORDINACION AREA"
    assert norm("REAL DECRETO") == "REAL DECRETO"
    with pytest.raises(BenchmarkError, match="TITLE_NOT_BOUNDED"):
        norm("")


def test_performance_is_not_promoted_to_legal_identity():
    summary = measure(synthetic_corpus(4711), "B0_SEQUENCE")
    assert summary["authenticated_legal_links"] == 0
    assert summary["real_world_source_read"] is False
    assert summary["status_of_real_norms_used"] is False
    assert summary["R5"] == "STOP"
    assert "actual_approval" not in json.dumps(summary)


def _fake(seed, b0, b1, b2, stratum_b0=None, stratum_b1=None):
    zero = {k: 0.8 for k in ("reordered", "abbreviated", "stable")}
    def row(score, strata):
        return {"recall_at_3": score, "by_stratum_recall_at_3": strata or zero}
    return {
        "seed": seed, "results": {
            "B0_SEQUENCE": row(b0, stratum_b0),
            "B1_IDF": row(b1, stratum_b1),
            "B2_JACCARD": row(b2, None),
        }
    }


def test_h1_requires_gain_against_b0_and_parity_with_strong_b2():
    passing = tuple(_fake(seed, .70, .80, .79) for seed in CONFIRMATION_SEEDS)
    yes = decision(passing)
    assert yes["h1_predeclared_threshold_met"] is True
    failing = tuple(_fake(seed, .70, .74, .78) for seed in CONFIRMATION_SEEDS)
    no = decision(failing)
    assert no["h1_predeclared_threshold_met"] is False
    assert no["AB_decide"] == "STOP_OR_PIVOT"


def test_stratum_loss_and_any_missing_holdout_force_failure():
    old = {"reordered": 0.8, "abbreviated": 0.8, "stable": 0.8}
    new = {"reordered": 0.65, "abbreviated": 0.8, "stable": 0.8}
    rows = tuple(_fake(s, .7, .85, .83, old, new) for s in CONFIRMATION_SEEDS)
    assert decision(rows)["h1_predeclared_threshold_met"] is False
    with pytest.raises(BenchmarkError, match="CONFIRMATION_SEEDS_INVALID"):
        decision(rows[:2])
