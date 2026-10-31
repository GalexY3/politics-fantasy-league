"""AB10 P01. Closed-world synthetic benchmark for document REVIEW ordering.

No Spanish source files are read. Titles are intentionally imaginary. A title
ranking is not a legal identity link, a probability, or an IAEN outcome.
"""
from __future__ import annotations

from collections import Counter
from difflib import SequenceMatcher
import hashlib
import json
import math
import random
import re
from typing import Callable


N = 198
DECOYS = 55
TOPK = 3
EXPLORATION_SEED = 4711
CONFIRMATION_SEEDS = (991, 992, 993)
SEEDS = (EXPLORATION_SEED, *CONFIRMATION_SEEDS)
TOPICS = ("NIMBO", "ZEFIRO", "TESERA", "ARISTA", "AURORA", "LUMBRE",
          "MIRTO", "NACAR", "ORNATO", "SILEX", "URANO")
SECTORS = ("BASALTO", "CORAL", "VETIVER", "LUMEN", "TALCO",
           "MARMOL", "CIRCON", "LAUREL", "OPALO", "SABINA")
AREAS = ("DELTA", "OMEGA", "SIGMA", "GAMMA", "LAMBDA")
SHARED_WORDS = {"REAL", "DECRETO", "LEY", "SOBRE", "DE", "EL", "LA",
                "EN", "DEL", "PARA", "Y", "PROCEDIMIENTO", "REGULACION"}
VALID_STRATA = ("reordered", "abbreviated", "stable")


class BenchmarkError(ValueError):
    pass


def norm(text: str) -> str:
    if not isinstance(text, str) or not text or len(text) > 1400:
        raise BenchmarkError("TITLE_NOT_BOUNDED")
    from unicodedata import normalize, combining
    latin = normalize("NFKD", text.upper())
    raw = " ".join(re.findall(r"[A-Z0-9]+", "".join(c for c in latin if not combining(c))))
    if not raw:
        raise BenchmarkError("EMPTY_TITLE")
    # All comparators receive the same deterministic normalization.
    return " ".join("REAL DECRETO" if x == "RD" else x for x in raw.split())


def _title(kind: int, topic: str, sector: str, area: str) -> str:
    prefix = ("REAL DECRETO", "LEY", "LEY ORGANICA")[kind]
    return (f"{prefix} SOBRE EL PROCEDIMIENTO DE REGULACION Y COORDINACION "
            f"DEL PROTOCOLO {topic} EN EL SISTEMA {sector} PARA EL AMBITO {area}")


def _variant(text: str, kind: int, topic: str, sector: str, area: str,
             stratum: str) -> str:
    prefix = ("REAL DECRETO", "LEY", "LEY ORGANICA")[kind]
    if stratum == "reordered":
        return (f"EN EL AMBITO {area} Y SISTEMA {sector} SE COORDINA EL PROTOCOLO "
                f"{topic} MEDIANTE {prefix} DE REGULACION")
    if stratum == "abbreviated":
        abbr = "RD" if kind == 0 else prefix
        return f"{abbr} DE COORDINACION {area} PARA {sector} SOBRE {topic}"
    if stratum == "stable":
        return text + " DE CARACTER SINTETICO"
    raise BenchmarkError("STRATUM_UNKNOWN")


def synthetic_corpus(seed: int) -> dict:
    if type(seed) is not int or seed not in SEEDS:
        raise BenchmarkError("SEED_NOT_PREDECLARED")
    rng = random.Random(seed)
    combinations = [
        (kind, topic, sector, area)
        for topic in TOPICS
        for sector in SECTORS
        for area in AREAS
        for kind in (0, 1, 2)
    ]
    rng.shuffle(combinations)
    selected = combinations[:N]
    # Each pair is unique by *construction*; IDs are only revealed to scoring.
    plan = []
    report = []
    for ix, (kind, topic, sector, area) in enumerate(selected):
        t = _title(kind, topic, sector, area)
        stratum = ("reordered", "abbreviated", "stable")[ix % 3]
        plan.append({"synthetic_id": f"FICTIONAL-PLAN-{ix:04d}",
                     "title": t, "stratum": stratum})
        report.append({"synthetic_id": f"FICTIONAL-REPORT-{ix:04d}",
                       "title": _variant(t, kind, topic, sector, area, stratum),
                       "true_plan_id": f"FICTIONAL-PLAN-{ix:04d}"})
    for i, (kind, topic, sector, area) in enumerate(combinations[N:N + DECOYS]):
        # Distractors have similar word frequency but zero ground-truth link.
        report.append({"synthetic_id": f"FICTIONAL-DECOY-{i:04d}",
                       "title": _title(kind, topic, sector, area),
                       "true_plan_id": None})
    rng.shuffle(report)
    if len(plan) != N or len(report) != N + DECOYS:
        raise BenchmarkError("POPULATION_INVARIANT_FAILED")
    return {"plan": plan, "report": report,
            "seed": seed, "ground_truth_count": N,
            "source_type": "SYNTHETIC_INVENTED_NOT_SPANISH"}


def token_sets(titles: tuple[str, ...]) -> tuple[frozenset[str], ...]:
    return tuple(frozenset(norm(x).split()) for x in titles)


def idf_weights(documents: tuple[frozenset[str], ...]) -> dict[str, float]:
    # Document frequencies over candidate titles ONLY; labels not consulted.
    frequencies = Counter(token for row in documents for token in row)
    n = len(documents)
    if n == 0:
        raise BenchmarkError("NO_CANDIDATE_DOCUMENTS")
    return {word: math.log((n + 1) / (df + 1)) + 1
            for word, df in frequencies.items()}


def weighted_jaccard(a: frozenset[str], b: frozenset[str],
                     weights: dict[str, float]) -> float:
    union = a | b
    if not union:
        return 0.0
    numerator = sum(weights.get(x, 1.0) for x in a & b)
    denominator = sum(weights.get(x, 1.0) for x in union)
    return numerator / denominator


def rare_token_score(query: frozenset[str], candidate: frozenset[str],
                     weights: dict[str, float]) -> float:
    """Prospective post-exploration PIVOT: reward rare shared terms.

    Uses candidate-corpus document frequency only; never true pair IDs, rank,
    ministry/outcome, or future labels. The fallback is fixed before holdout.
    """
    rare = {word: value for word, value in weights.items() if value >= 2.0}
    if not rare:
        rare = weights
    q = frozenset(word for word in query if word in rare)
    c = frozenset(word for word in candidate if word in rare)
    return weighted_jaccard(q, c, rare)


def rank_three(title: str, candidate_titles: tuple[str, ...],
               *, algorithm: str) -> tuple[int, ...]:
    if (type(candidate_titles) is not tuple
            or not 3 <= len(candidate_titles) <= 500
            or algorithm not in {"B0_SEQUENCE", "B1_IDF", "B2_JACCARD", "ABLATION_NO_IDF"}):
        raise BenchmarkError("BENCHMARK_ALGORITHM_OR_CANDIDATES_INVALID")
    query = norm(title)
    candidates_norm = tuple(norm(x) for x in candidate_titles)
    candidate_tokens = tuple(frozenset(x.split()) for x in candidates_norm)
    query_tokens = frozenset(query.split())
    if algorithm in {"B1_IDF", "B2_JACCARD", "ABLATION_NO_IDF"}:
        weights = (idf_weights(candidate_tokens) if algorithm == "B1_IDF"
                   else {word: 1.0 for item in candidate_tokens for word in item})
    else:
        weights = {}
    scoring = []
    for j, (candidate, tokens) in enumerate(zip(candidates_norm, candidate_tokens)):
        seq = SequenceMatcher(None, query, candidate, autojunk=False).ratio()
        if algorithm == "B0_SEQUENCE":
            score = seq
        elif algorithm == "B1_IDF":
            score = 0.95 * rare_token_score(query_tokens, tokens, weights) + 0.05 * seq
        else:
            score = weighted_jaccard(query_tokens, tokens, weights)
        scoring.append((score, j))
    scoring.sort(key=lambda x: (-x[0], x[1]))
    return tuple(j for _, j in scoring[:TOPK])


def measure(corpus: dict, algorithm: str) -> dict:
    plan = corpus["plan"]
    reports = corpus["report"]
    if (len(plan) != N or len(reports) != N + DECOYS
            or any(x["synthetic_id"].startswith("FICTIONAL-") is False for x in plan)):
        raise BenchmarkError("SYNTHETIC_POPULATION_REQUIRED")
    cand_titles = tuple(x["title"] for x in reports)
    rank_one = []
    correct_top1 = 0
    correct_top3 = 0
    by_stratum: dict[str, list[int]] = {x: [] for x in VALID_STRATA}
    for row in plan:
        choices = rank_three(row["title"], cand_titles, algorithm=algorithm)
        ranked_targets = [reports[i]["true_plan_id"] for i in choices]
        top1 = reports[choices[0]]["synthetic_id"]
        rank_one.append(top1)
        is_top1 = ranked_targets[0] == row["synthetic_id"]
        is_top3 = row["synthetic_id"] in ranked_targets
        correct_top1 += is_top1
        correct_top3 += is_top3
        by_stratum[row["stratum"]].append(int(is_top3))
    counts = Counter(rank_one)
    return {
        "algorithm": algorithm,
        "seed": corpus["seed"],
        "n_plan": N, "n_report": len(reports), "top_k": TOPK,
        "recall_at_1": correct_top1 / N,
        "recall_at_3": correct_top3 / N,
        "distinct_first_choice_destinations": len(counts),
        "first_choice_collisions": sum(x - 1 for x in counts.values() if x > 1),
        "by_stratum_recall_at_3": {k: sum(v) / len(v) for k, v in by_stratum.items()},
        "authenticated_legal_links": 0,
        "real_world_source_read": False, "status_of_real_norms_used": False,
        "R5": "STOP",
    }


def run_seed(seed: int) -> dict:
    corpus = synthetic_corpus(seed)
    results = {name: measure(corpus, name)
               for name in ("B0_SEQUENCE", "B1_IDF", "B2_JACCARD", "ABLATION_NO_IDF")}
    if (results["ABLATION_NO_IDF"]["recall_at_3"]
            != results["B2_JACCARD"]["recall_at_3"]):
        raise BenchmarkError("ABLATION_NOT_EQUIVALENT_TO_EQUAL_JACCARD")
    canonical = json.dumps({
        "seed": seed, "titles": [(x["title"], x["synthetic_id"]) for x in corpus["report"]],
    }, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return {
        "schema": "pfl.ab10.candidate_rank_synthetic.v1",
        "seed": seed, "synthetic_corpus_sha256": hashlib.sha256(canonical).hexdigest(),
        "results": results,
        "source_kind": "FULLY_SYNTHETIC_NOT_LEGAL_CROSSWALK",
        "all_suggested_links_unknown": True,
        "scientific_R5": "STOP",
    }


def decision(rows: tuple[dict, ...]) -> dict:
    if len(rows) != 3 or tuple(x["seed"] for x in rows) != CONFIRMATION_SEEDS:
        raise BenchmarkError("CONFIRMATION_SEEDS_INVALID")
    b0 = [x["results"]["B0_SEQUENCE"]["recall_at_3"] for x in rows]
    b1 = [x["results"]["B1_IDF"]["recall_at_3"] for x in rows]
    b2 = [x["results"]["B2_JACCARD"]["recall_at_3"] for x in rows]
    strata = VALID_STRATA
    stratum_ok = all(
        x["results"]["B1_IDF"]["by_stratum_recall_at_3"][key]
        >= x["results"]["B0_SEQUENCE"]["by_stratum_recall_at_3"][key] - 0.10
        for x in rows for key in strata
    )
    absolute_stratum_floor = all(
        x["results"]["B1_IDF"]["by_stratum_recall_at_3"][key] >= 0.55
        for x in rows for key in strata
    )
    avg = lambda xs: sum(xs) / len(xs)
    h1 = (avg(b1) - avg(b0) >= 0.05
          and avg(b1) >= avg(b2) - 0.02
          and stratum_ok and absolute_stratum_floor)
    return {
        "confirmatory_seeds": list(CONFIRMATION_SEEDS),
        "baseline_mean_recall_at_3": avg(b0),
        "weighted_mean_recall_at_3": avg(b1),
        "unweighted_mean_recall_at_3": avg(b2),
        "weighted_minus_sequence": avg(b1) - avg(b0),
        "strata_noninferiority": stratum_ok,
        "per_seed_per_stratum_absolute_floor": absolute_stratum_floor,
        "h1_predeclared_threshold_met": h1,
        "AB_decide": "READY_REVIEW_SYNTHETIC_PRODUCT_ONLY" if h1 else "STOP_OR_PIVOT",
        "external_replication_verified": False, "R5": "STOP",
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True, choices=SEEDS)
    opt = parser.parse_args()
    print(json.dumps(run_seed(opt.seed), indent=2, sort_keys=True))
