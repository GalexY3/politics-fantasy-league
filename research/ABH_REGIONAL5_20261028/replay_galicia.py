#!/usr/bin/env python3
"""Exact rational seat replay on manually transcribed 2024 Galicia DOG fixture.
Standalone stdlib, no downloads. Not a prediction, no person records.
"""
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

def allocate(votes, seats, valid, barrier=True):
    eligible = {k: v for k, v in votes.items() if not barrier or 100 * v >= 5 * valid}
    quotients = sorted(((Fraction(v, i), v, k) for k, v in eligible.items()
                       for i in range(1, seats + 1)), reverse=True)
    result = Counter(k for _, _, k in quotients[:seats])
    return dict(result)

def run():
    data = json.loads(Path(__file__).with_name("C02_GALICIA_FULL_PROVINCIAL_REPLAY.json").read_text(encoding="utf-8"))
    parties = Counter()
    seat_totals = Counter()
    for p in data["provinces"]:
        assert sum(p["votes"].values()) == p["candidacy"], p["id"]
        out = allocate(p["votes"], p["seats"], p["valid"])
        assert out == p["observed"], (p["id"], out, p["observed"])
        parties.update(p["votes"])
        seat_totals.update(out)
    assert dict(seat_totals) == data["expected"]["aggregate_observed"]
    assert sum(parties.values()) == 1488705
    assert sum(p["seats"] for p in data["provinces"]) == 75
    assert sum(p["valid"] for p in data["provinces"]) == 1501757
    invalid_pool = allocate(dict(parties), 75, 1501757)
    invalid_no_barrier = allocate(dict(parties), 75, 1501757, barrier=False)
    assert invalid_pool == data["expected"]["regional_single_district_75_with_barrier_5pct"]
    assert invalid_no_barrier == data["expected"]["regional_single_district_75_no_barrier"]
    return {"provincial":dict(seat_totals),"invalid_region_pool":invalid_pool,
            "invalid_region_no_barrier":invalid_no_barrier,
            "legal_observed_seats":75,"local_test":"PASS_NOT_EXTERNAL_REPLICATION"}

if __name__=="__main__":
    print(json.dumps(run(), ensure_ascii=False, sort_keys=True))
