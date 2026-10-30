"""Independent official-open-dataset descriptive test; NEVER event/person scoring.

Source: data.gouv.fr Assemblée nationale petitions (Licence Ouverte 2.0).
Only support, petition date/status, commission and whether an official dataset
decision field is DOCUMENTED are used. An empty cell is NOT 'no decision'.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path

NEEDED = ("identifiant", "date_publication", "nb_votes", "statut",
          "commission", "decision_commission")
TERMINAL = {"classee", "expiree", "archivee"}
MISSING = {"", "nan", "none", "null"}


def _count(raw):
    if raw is None or str(raw).strip().lower() in MISSING:
        return None
    try:
        d = Decimal(str(raw).strip().replace(" ", ""))
    except InvalidOperation:
        return None
    if not d.is_finite() or d != d.to_integral_value() or not 0 <= d <= 50000000:
        return None
    return int(d)


def analyze(path: Path, *, cutoff: date = date(2026, 4, 29)):
    # 180 days before the fixed 26 October 2026 snapshot. Not a time series.
    content = path.read_bytes()
    if not (50 < len(content) <= 16_000_000):
        raise ValueError("BAD_SOURCE_BYTES")
    sha = hashlib.sha256(content).hexdigest()
    from io import StringIO
    text = content.decode("utf-8-sig")
    # This parser touches source text to parse CSV, but retains no names, text
    # or full rows outside the current loop, and emits aggregates only.
    reader = csv.DictReader(StringIO(text, newline=""), delimiter=";")
    if reader.fieldnames is None or len(reader.fieldnames) != len(set(reader.fieldnames)):
        raise ValueError("INVALID_COLUMNS")
    if not set(NEEDED).issubset(reader.fieldnames):
        raise ValueError("REQUIRED_FIELDS_MISSING")
    stats = {"total": 0, "excluded_open": 0, "excluded_young": 0,
             "excluded_missing": 0, "excluded_low_support": 0}
    seen = set()
    bands = {"low": [0, 0], "high": [0, 0]}
    strata = {}
    commission_strata = {}
    for row in reader:
        stats["total"] += 1
        ident = str(row["identifiant"] or "").strip()
        if not ident or ident in seen:
            raise ValueError("DUPLICATE_OR_EMPTY_PETITION_KEY")
        seen.add(ident)
        try:
            published = date.fromisoformat(str(row["date_publication"] or "").strip())
        except ValueError:
            stats["excluded_missing"] += 1
            continue
        if published > cutoff:
            stats["excluded_young"] += 1
            continue
        status = str(row["statut"] or "").strip().lower()
        if status == "ouverte":
            stats["excluded_open"] += 1
            continue
        if status not in TERMINAL:
            stats["excluded_missing"] += 1
            continue
        votes = _count(row["nb_votes"])
        if votes is None:
            stats["excluded_missing"] += 1
            continue
        if votes < 100:
            stats["excluded_low_support"] += 1
            continue
        group = "high" if votes >= 10000 else "low"
        documented = str(row["decision_commission"] or "").strip().lower() not in MISSING
        bands[group][0] += 1
        bands[group][1] += int(documented)
        year = str(published.year)
        ys = strata.setdefault(year, {"low": [0, 0], "high": [0, 0]})
        ys[group][0] += 1
        ys[group][1] += int(documented)
        commission = str(row["commission"] or "").strip()
        # No committee names are output; only number of comparable strata.
        cy = (year, commission)
        cs = commission_strata.setdefault(cy, {"low": [0, 0], "high": [0, 0]})
        cs[group][0] += 1
        cs[group][1] += int(documented)
    eligible = sum(x[0] for x in bands.values())
    if stats["total"] != (eligible + sum(v for k, v in stats.items()
                                        if k.startswith("excluded_"))):
        raise ValueError("ROW_CONSERVATION_FAILED")
    def rate(arr):
        return arr[1] / arr[0] if arr[0] else None
    delta = (rate(bands["high"]) - rate(bands["low"])
             if all(bands[g][0] for g in ("high", "low")) else None)
    comparable_years = {
        year: {"high": v["high"][0], "low": v["low"][0],
               "rate_difference": rate(v["high"]) - rate(v["low"])}
        for year, v in strata.items() if v["high"][0] >= 3 and v["low"][0] >= 10
    }
    positive_years = sum(v["rate_difference"] > 0 for v in comparable_years.values())
    comparable_commission_years = sum(
        v["high"][0] >= 2 and v["low"][0] >= 5 for v in commission_strata.values())
    if (bands["high"][0] < 10 or bands["low"][0] < 10
            or len(comparable_years) < 2):
        verdict = "INCONCLUSIVE_INSUFFICIENT_COMPARABLE_STRATA"
    elif delta > 0 and positive_years > len(comparable_years) / 2:
        verdict = "DESCRIPTIVE_POSITIVE_ASSOCIATION_NOT_CAUSAL"
    else:
        verdict = "DIRECTIONAL_H1_NOT_SUPPORTED_BY_PREDECLARED_CRITERION"
    return {
        "schema": "pfl.r0.petitions.documentation_descriptive.v1",
        "source_sha256": sha, "source_bytes": len(content), "counts": stats,
        "eligible": eligible, "threshold_descriptive_only": 10000,
        "low_100_to_9999": {"n": bands["low"][0], "documented": bands["low"][1],
                            "rate": rate(bands["low"])},
        "high_10000_plus": {"n": bands["high"][0], "documented": bands["high"][1],
                            "rate": rate(bands["high"])},
        "overall_rate_difference": delta,
        "within_years": comparable_years,
        "comparable_year_count": len(comparable_years),
        "positive_year_count": positive_years,
        "comparable_year_commission_cells": comparable_commission_years,
        "verdict": verdict,
        "outcome_meaning": "DECISION_FIELD_DOCUMENTED_VS_UNDOCUMENTED_NOT_REAL_DECISION",
        "source_kind": "GOV_PUBLISHED_WEEKLY_SCRAPED_AGGREGATE_PETITION_RECORDS",
        "person_identifiers_emitted": False, "causal": False,
        "snapshot_not_original_event_history": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    args = parser.parse_args()
    print(json.dumps(analyze(args.csv_path), sort_keys=True))


if __name__ == "__main__":
    main()
