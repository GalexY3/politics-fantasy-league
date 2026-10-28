"""Research-only deterministic replay of 12 official UK petition events, manually transcribed.
Input JSON is derived from publisher-rendered API responses (NOT byte-authenticated originals).
Cohort top 12 most signed CLOSED petitions; do not estimate systemwide rates or causal thresholds.
Not executed on a clean checkout in original campaign: executable provided for T022 Codex.
"""
import json
from pathlib import Path
from datetime import datetime, timezone
from statistics import median, mean

ROOT=Path(__file__).parent

def timestamp(x):
    return datetime.fromisoformat(x.replace("Z","+00:00"))

def days(a,b):
    return (timestamp(a)-timestamp(b)).total_seconds()/86400

def rank(xs):
    order=sorted(enumerate(xs),key=lambda v:v[1])
    res=[None]*len(xs)
    pos=0
    while pos<len(xs):
        end=pos+1
        while end<len(xs) and order[end][1]==order[pos][1]:
            end+=1
        middle=(pos+1+end)/2
        for j in range(pos,end):
            res[order[j][0]]=middle
        pos=end
    return res

def pearson(a,b):
    am,bm=mean(a),mean(b)
    top=sum((x-am)*(y-bm) for x,y in zip(a,b))
    bot=(sum((x-am)**2 for x in a)*sum((y-bm)**2 for y in b))**0.5
    return top/bot

def spearman(a,b):
    return pearson(rank(a),rank(b))

def run():
    entries=json.loads((ROOT/"PETITIONS12_EVENT_PANEL.json").read_text())["data"]
    assert len(entries)==12 and len({i["id"] for i in entries})==12
    assert all(i["signatures"]>=100000 for i in entries)
    assert all(timestamp(i["opened_at"]) <= timestamp(i["response_threshold_reached_at"])
               < timestamp(i["government_response_at"]) for i in entries)
    assert all(timestamp(i["debate_threshold_reached_at"]) <
               timestamp(i["scheduled_debate_date"]+"T00:00:00Z") for i in entries)
    lag=[days(i["government_response_at"],i["response_threshold_reached_at"]) for i in entries]
    crossing=[days(i["response_threshold_reached_at"],i["opened_at"]) for i in entries]
    scheduled=[days(i["scheduled_debate_date"]+"T00:00:00Z",i["debate_threshold_reached_at"]) for i in entries]
    published=[days(i["response_responded_on"]+"T00:00:00Z",i["response_threshold_reached_at"]) for i in entries]
    wrong_dates=[i["id"] for i in entries
                 if i["government_response_at"][:10]!=i["response_responded_on"]]
    output={
        "n":len(entries), "response_median_days":median(lag),
        "response_mean_days":mean(lag), "response_over_30":sum(x>30 for x in lag),
        "debate_median_days":median(scheduled), "debate_over_90":sum(x>90 for x in scheduled),
        "speed_to_10k_vs_response_delay_spearman":spearman(crossing,lag),
        "response_published_date_median_days":median(published),
        "response_publication_date_mismatches":wrong_dates,
        "all_updated_after_closure":all(timestamp(i["updated_at"])>timestamp(i["closed_at"]) for i in entries)
    }
    print(json.dumps(output,indent=2,ensure_ascii=False))

if __name__=="__main__": run()
