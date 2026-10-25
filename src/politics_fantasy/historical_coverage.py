"""Audit a local copy of secondary XV roll-call JSONL without releasing personal votes.

NOT an official dataset certifier. 'Missing' means absent identity matches in a
secondary catalogue, NOT an absent deputy, parliamentary non-participation or a
no-vote. User must download legal original and log acquisition time himself.
"""
from __future__ import annotations
from collections import defaultdict, Counter
from datetime import date
from hashlib import sha1, sha256
from pathlib import Path
import json
import random
import statistics

CATEGORIES = ("S", "N", "A", "X")
SOURCE = "https://github.com/MarcoAnarmo/CongresoAbierto/blob/main/data/raw/votaciones/pleno.jsonl"
KNOWN_GIT_BLOB = "71918bb689c7a62cfbbdafe0b9248eac6b5c4be1"


def git_blob_hash(b: bytes) -> str:
    return sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()


def _ids(s: str) -> list[str]:
    if not isinstance(s, str):
        raise ValueError("Invalid compact nominal vote string")
    return s.split()


def load_jsonl(path: str | Path, *, expected_blob_sha1: str | None = None, max_bytes: int = 40_000_000) -> tuple[list[dict], dict]:
    path = Path(path)
    with path.open("rb") as f:
        data = f.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError("Source too large")
    githash = git_blob_hash(data)
    if expected_blob_sha1 is not None and githash != expected_blob_sha1:
        raise ValueError("Git blob SHA-1 mismatch")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as e:
        raise ValueError("Source must be UTF-8") from e
    records = []
    seen = set()
    for i, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        x = json.loads(line)
        if not isinstance(x, dict) or x.get("id") in seen or not isinstance(x.get("id"), str):
            raise ValueError(f"Bad/duplicate row {i}")
        seen.add(x["id"])
        if not isinstance(x.get("fecha"), str) or date.fromisoformat(x["fecha"]).isoformat() != x["fecha"]:
            raise ValueError("Invalid date")
        if not isinstance(x.get("sesion"), int) or x["sesion"] < 0:
            raise ValueError("Invalid session")
        t = x.get("totales")
        if not isinstance(t, dict):
            raise ValueError("Missing official-like totals")
        counts = tuple(t[k] for k in ("si", "no", "abstencion", "noVota"))
        if any(type(z) is not int or z < 0 for z in counts) or sum(counts) > 350:
            raise ValueError("Invalid total counts")
        votes = x.get("votos") or {}
        groups = x.get("grupos") or {}
        if not isinstance(votes, dict) or set(votes) - set(CATEGORIES) or not isinstance(groups, dict):
            raise ValueError("Bad compact form")
        nominal = tuple(len(_ids(votes.get(k, ""))) for k in CATEGORIES)
        ids = [ident for k in CATEGORIES for ident in _ids(votes.get(k, ""))]
        if len(ids) != len(set(ids)):
            raise ValueError("Deputy code duplicated in multiple categories")
        if any(n > c for n, c in zip(nominal, counts)):
            raise ValueError("Named-vote count exceeds official-like total")
        agg = [0] * 4
        tie = 0
        modal_num = 0
        expressed_num = 0
        filtered_modal = 0
        filtered_exp = 0
        for group, values in groups.items():
            if not isinstance(group, str) or not isinstance(values, list) or len(values) != 4:
                raise ValueError("Invalid group row")
            if any(type(z) is not int or z < 0 for z in values):
                raise ValueError("Invalid group count")
            for k in range(4):
                agg[k] += values[k]
            yes, no, abstain, _ = values
            ex = yes + no + abstain
            if ex:
                maximum = max(yes, no, abstain)
                if (yes, no, abstain).count(maximum) > 1:
                    tie += 1
                modal_num += maximum
                expressed_num += ex
                if group != "GMx" and sum(values) > 5:
                    filtered_modal += maximum
                    filtered_exp += ex
        if groups and tuple(agg) != counts:
            raise ValueError("Group sum contradicts published total")
        records.append({"id": x["id"], "day": x["fecha"], "year": x["fecha"][:4], "session": x["sesion"],
                        "totals": counts, "nominal": nominal, "named": sum(nominal), "total": sum(counts),
                        "group_count": len(groups), "tie_groups": tie,
                        "modal": modal_num, "expressed": expressed_num,
                        "filtered_modal": filtered_modal, "filtered_expressed": filtered_exp,
                        "keys": ids})
    if not records:
        raise ValueError("No roll calls")
    return records, {"git_blob_sha1": githash, "sha256": sha256(data).hexdigest(), "bytes": len(data),
                     "data_status": "SECONDARY_SOURCE_DATA_NOT_OFFICIAL_CERTIFICATION", "source": SOURCE}


def _sum(a, key: str):
    return sum(x[key] for x in a)


def _ratio(a: list[dict]) -> float | None:
    return _sum(a, "named") / _sum(a, "total") if _sum(a, "total") else None


def _bootstrap_year_gap(rows: list[dict], y0: str, y1: str, *, reps: int = 600, seed: int = 20261025):
    rng = random.Random(seed)
    grouped = {}
    for y in (y0, y1):
        d = defaultdict(list)
        for r in rows:
            if r["year"] == y and r["named"] > 0:
                d[r["session"]].append(r)
        grouped[y] = list(d.values())
    if any(not grouped[y] for y in (y0, y1)):
        return None
    out = []
    for _ in range(reps):
        rates = []
        for y in (y0, y1):
            s = grouped[y]
            sample = [r for _ in s for r in rng.choice(s)]
            rates.append(_ratio(sample))
        out.append(rates[1] - rates[0])
    out.sort()
    return {"unit": "plenary_session_cluster", "replicates": reps, "seed": seed,
            "coverage_difference_2026_minus_2023_ci95": [out[int(.025 * reps)], out[min(reps - 1, int(.975 * reps))]],
            "status": "DESCRIPTIVE_RESAMPLING_NOT_CAUSAL_INFERENCE"}


def summary(rows: list[dict], provenance: dict) -> dict:
    years = sorted({r["year"] for r in rows})
    active = [r for r in rows if r["named"]]
    cats = [sum(x["totals"][i] for x in active) for i in range(4)]
    ncats = [sum(x["nominal"][i] for x in active) for i in range(4)]
    by_year = {}
    for y in years:
        q = [r for r in rows if r["year"] == y]
        qa = [r for r in q if r["named"]]
        by_year[y] = {"votes": len(q), "sessions": len({x["session"] for x in q}),
                      "nominal_observed": _sum(q, "named"), "positions_all": _sum(q, "total"),
                      "coverage_all": _ratio(q), "coverage_with_nominal": _ratio(qa),
                      "with_nominal": len(qa), "explicit_no_votes": sum(x["totals"][3] for x in q),
                      "missing_by_code_lookup": sum(x["total"] - x["named"] for x in qa)}
    uniques = {y: set(k for r in rows if r["year"] == y for k in r["keys"]) for y in years}
    n_sessions = len({r["session"] for r in rows})
    bysession = defaultdict(list)
    for r in rows: bysession[r["session"]].append(r)
    ratio_sessions = [_ratio([r for r in group if r["named"]]) for group in bysession.values()]
    ratio_sessions = [r for r in ratio_sessions if r is not None]
    halfway = len(rows) // 2
    return {"provenance": provenance,
        "votes": len(rows), "unique_vote_ids": len({r["id"] for r in rows}), "date_min": min(r["day"] for r in rows),
        "date_max": max(r["day"] for r in rows), "plenary_sessions": n_sessions,
        "total_not_350": sum(r["total"] != 350 for r in rows), "totals_over_350": sum(r["total"] > 350 for r in rows),
        "with_nominal": len(active), "without_nominal": len(rows)-len(active),
        "group_rows": _sum(rows, "group_count"),
        "nominal_rows": _sum(rows, "named"), "total_positions": _sum(rows, "total"),
        "matched_nominal_votations": sum(x["named"] == x["total"] for x in active),
        "partial_nominal_votations": sum(x["named"] < x["total"] for x in active),
        "missing_by_choice_on_votes_with_nominal": dict(zip(CATEGORIES, [x-y for x, y in zip(cats, ncats)])),
        "explicit_no_votes_total": sum(x["totals"][3] for x in rows),
        "yearly": by_year,
        "coverage_vote_weighted": _ratio(active),
        "coverage_session_equal_weighted": statistics.mean(ratio_sessions) if ratio_sessions else None,
        "nominal_code_union": len(set().union(*uniques.values())),
        "codes_by_year": {y: len(uniques[y]) for y in years},
        "code_overlap_2023_2026": len(uniques.get("2023", set()) & uniques.get("2026", set())),
        "tied_group_votes": _sum(rows, "tie_groups"),
        "modal_share_expressed": (_sum(rows, "modal") / _sum(rows, "expressed") if _sum(rows, "expressed") else None),
        "modal_share_excluding_mixto_and_small_groups": (_sum(rows, "filtered_modal") / _sum(rows, "filtered_expressed") if _sum(rows, "filtered_expressed") else None),
        "first_half_coverage": _ratio([x for x in rows[:halfway] if x["named"]]),
        "second_half_coverage": _ratio([x for x in rows[halfway:] if x["named"]]),
        "cluster_bootstrap_2023_2026": _bootstrap_year_gap(rows, "2023", "2026"),
        "inference_gate": "NOT_OFFICIAL_NOMINAL_VERIFICATION_OR_HISTORICAL_ROSTER",
        "privacy": "COUNTS_ONLY_NO_DEPUTY_IDS_EXPORTED"}
