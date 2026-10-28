"""Research-only four-ballot descriptive sensitivity, not inference.

Input must be an already-transcribed documented aggregate sample, never an
issuer-original nominal vote file. No real-person scoring or pseudoreplication.
"""
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_EVEN

def six(x):
    return float(x.quantize(Decimal('0.000001'),rounding=ROUND_HALF_EVEN))


def analyze_vote_sample(records):
    if not isinstance(records,list) or not records:
        raise ValueError('ROWS_NOT_ARRAY_OR_EMPTY')
    observed=set()
    groups=defaultdict(list)
    for r in records:
        if not isinstance(r,dict) or any(not isinstance(r.get(k),str) or not r[k].strip() for k in ('expediente','vote')):
            raise ValueError('INVALID_BALLOT_ID')
        k=(r['expediente'],r['vote'])
        if k in observed:
            raise ValueError('DUPLICATE_BALLOT_KEY')
        observed.add(k)
        counts=[r.get(k) for k in ('yes','no','abstain','total')]
        if any(not isinstance(n,int) or isinstance(n,bool) or n<0 for n in counts):
            raise ValueError('INVALID_TALLY')
        yes,no,abstain,total=counts
        if total!=yes+no+abstain or total==0:
            raise ValueError('INVALID_BALLOT_DENOMINATOR')
        groups[r['expediente']].append({'vote':r['vote'],'yes':yes,'total':total,'yes_pct':Decimal(100)*Decimal(yes)/Decimal(total)})
    output=[]
    for expediente, ballots in sorted(groups.items()):
        ys=sum(b['yes'] for b in ballots)
        n=sum(b['total'] for b in ballots)
        rates=[b['yes_pct'] for b in ballots]
        output.append({'expediente':expediente,'ballots':len(ballots),
                       'per_ballot':[{'vote':b['vote'],'yes_pct':six(b['yes_pct']),'total':b['total']} for b in ballots],
                       'range_pp':six(max(rates)-min(rates)),
                       'naive_collapsed_yes_pct':six(Decimal(100)*Decimal(ys)/Decimal(n)),
                       'naive_collapsed_total':n})
    return {'observed_ballots':len(records),'distinct_expedientes':len(output),'expedientes':output,
            'note':'Only previously transcribed HTML aggregate categories yes/no/abstain; no nominal, no absent/not-voting coverage, no as-of or population inference.'}
