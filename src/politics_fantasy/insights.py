"""Ten explainable LOCAL FICTIONAL game insights for ABH25B C17-C26.

Values are derived from one authenticated account's state, never official data.
No persistence, prediction, person scoring, trading, pricing or public claims.
Only settled rounds with frozen component receipts support contribution shares.
"""
from __future__ import annotations
from collections import Counter
from math import isclose, log

FIXED_PRICE_CREDIT_UNIT="SYNTHETIC_CREDITS_NOT_CURRENCY"
MAX_ROSTER=5
LINEUP_SIZE=3

def _roster(s,cid):
    return [f for f in s["figures"] if f.get("owner_id")==cid]
def _club(s,cid):
    return next((c for c in s["clubs"] if c["id"]==cid),None)

def c17_valuation(s,cid):
    c=_club(s,cid); roster=_roster(s,cid)
    return {"credits":c["credits"],"asset_book_value":sum(f["price"] for f in roster),
            "portfolio_book_value":c["credits"]+sum(f["price"] for f in roster),
            "currency":FIXED_PRICE_CREDIT_UNIT,"market_revaluation":False}

def c18_affordability(s,cid):
    c=_club(s,cid); roster=_roster(s,cid)
    free=[f for f in s["figures"] if f.get("owner_id") is None]
    can=[f for f in free if c["credits"]>=f["price"]] if len(roster)<MAX_ROSTER else []
    return {"vacant_roster_slots":max(0,MAX_ROSTER-len(roster)),
            "unowned_market_count":len(free),"affordable_unowned_count":len(can),
            "affordable_figure_ids":sorted(f["id"] for f in can),
            "no_purchase_committed":True}

def c19_role_entropy(s,cid):
    owners=_roster(s,cid);counts=Counter(f["role"] for f in owners)
    roles=set(f["role"] for f in s["figures"])
    if not owners:return {"role_counts":{},"entropy_normalized":None,"reason":"EMPTY_ROSTER"}
    n=len(owners)
    entropy=-sum((v/n)*log(v/n) for v in counts.values())
    den=log(len(roles)) if len(roles)>1 else 0
    return {"role_counts":dict(sorted(counts.items())),
            "entropy_normalized":entropy/den if den else 0.0,
            "reason":"SHANNON_ROLE_DIVERSITY_FICTIONAL"}

def c20_group_hhi(s,cid):
    owners=_roster(s,cid)
    if not owners:return {"hhi":None,"group_counts":{},"reason":"EMPTY_ROSTER"}
    counts=Counter(f["group_name"] for f in owners)
    return {"hhi":sum((x/len(owners))**2 for x in counts.values()),
            "group_counts":dict(sorted(counts.items())),"reason":"FICTIONAL_GROUP_CONCENTRATION"}

def _next_round(s):
    return next((r for r in reversed(s["rounds"]) if r["coverage_state"]=="NOT_AVAILABLE"),None)

def c21_starter_bench(s,cid):
    rnd=_next_round(s)
    if rnd is None:return {"status":"NO_PENDING_ROUND","starter_value":None,"bench_value":None}
    own={f["id"]:f for f in _roster(s,cid)}
    ids=rnd["lineups"].get(cid,[])
    if len(ids)!=LINEUP_SIZE or len(set(ids))!=LINEUP_SIZE or not set(ids).issubset(own):
        return {"status":"NO_VALID_SAVED_LINEUP","starter_value":None,"bench_value":None}
    return {"status":"SAVED_VALID_LINEUP","starter_value":sum(own[i]["price"] for i in ids),
            "bench_value":sum(f["price"] for i,f in own.items() if i not in ids),
            "not_forecast_points":True}

def c22_bounded_cash_flow(s,cid):
    trades=[t for t in s.get("trades",[]) if t.get("club_id")==cid]
    return {"observed_buys":sum(t["action"]=="buy" for t in trades),
            "observed_sells":sum(t["action"]=="sell" for t in trades),
            "cash_delta_bounded":sum(t["credits_delta"] for t in trades),
            "truncated_window_possible":len(s.get("trades",[]))>=40,
            "baseline_credits_attested":False}

def c23_churn(s,cid):
    trades=[t for t in s.get("trades",[]) if t.get("club_id")==cid]
    ids=Counter(t["figure_id"] for t in trades)
    return {"observed_transactions":len(trades),
            "distinct_figures_traded":len(ids),
            "figures_traded_multiple_times":sum(n>=2 for n in ids.values()),
            "truncated_window_possible":len(s.get("trades",[]))>=40,
            "not_all_time_churn":True}

def c24_lineup_readiness(s,cid):
    rnd=_next_round(s)
    if rnd is None:return {"status":"NO_FUTURE_ROUND","round_id":None}
    lineup=rnd["lineups"].get(cid,[])
    own={f["id"] for f in _roster(s,cid)}
    good=len(lineup)==LINEUP_SIZE and len(set(lineup))==LINEUP_SIZE and set(lineup)<=own
    state="LOCKED" if rnd["is_locked"] else "READY" if good else "INCOMPLETE"
    return {"status":state,"round_id":rnd["id"],"selected":len(lineup),
            "required":LINEUP_SIZE,"lock_at":rnd["lock_at"],"not_a_predicted_score":True}

def c25_settled_mean(s,cid):
    settled=[r for r in s["rounds"] if r.get("is_settled")]
    actual=[r["scores"].get(cid) for r in settled]
    known=[v for v in actual if v is not None]
    return {"settled_rounds":len(settled),"scored_rounds":len(known),
            "unscored_settled_rounds":len(actual)-len(known),
            "mean_scored":sum(known)/len(known) if known else None,
            "coverage":len(known)/len(settled) if settled else None,
            "unsettled_excluded":len(s["rounds"])-len(settled)}

def c26_component_concentration(s,cid):
    settled=[r for r in s["rounds"] if r.get("is_settled")]
    if not settled:return {"status":"NO_SETTLED_ROUND","hhi":None}
    rnd=settled[-1];detail=rnd.get("score_details",{}).get(cid,{})
    if detail.get("status")!="FROZEN_COMPONENTS":
        return {"status":"NO_FROZEN_BREAKDOWN","hhi":None}
    total=rnd["scores"].get(cid)
    parts=detail.get("components",[])
    if total is None or len(parts)!=LINEUP_SIZE or not isclose(
            sum(p["points"] for p in parts),total,abs_tol=1e-9):
        raise ValueError("FROZEN_COMPONENTS_INCONSISTENT")
    if total<=0:return {"status":"ZERO_SCORE_NOT_DISTRIBUTED","hhi":None}
    shares=[p["points"]/total for p in parts]
    return {"status":"CONCENTRATION_OF_FICTIONAL_SCORES","hhi":sum(x*x for x in shares),
            "max_share":max(shares),"round_id":rnd["id"],"frozen_only":True}

INSIGHT_FUNCTIONS=(c17_valuation,c18_affordability,c19_role_entropy,
 c20_group_hhi,c21_starter_bench,c22_bounded_cash_flow,c23_churn,
 c24_lineup_readiness,c25_settled_mean,c26_component_concentration)

def derive_all(s):
    """Derive 10 metrics per club from this account's already isolated state."""
    result={}
    for c in s["clubs"]:
        cid=c["id"]
        result[cid]={f.__name__.split("_",1)[0]:f(s,cid)
                     for f in INSIGHT_FUNCTIONS}
    return result
