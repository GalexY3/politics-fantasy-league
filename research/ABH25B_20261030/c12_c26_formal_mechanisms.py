"""ABH25B C12-C26: 15 independently specified social-mechanism simulations.

All agents, institutions, markets, petitions and rewards are artificial.
No original political people, source data, effects, behavioural estimates or
causal validation. Precommitted A–J: C12_C26_FORMAL_PREREG_AJ.json.
"""
from __future__ import annotations
import json, math, random, statistics, sys
from collections import Counter

N_REPS=200
def gini(v):
    a=sorted(v);s=sum(a);n=len(a)
    if n==0 or s<=0:return 0.0
    return sum((2*i-n-1)*x for i,x in enumerate(a,1))/(n*s)
def hhi(v):
    s=sum(v)
    return sum((x/s)**2 for x in v) if s else 0.0
def choose_weights(weights,u):
    total=sum(weights);target=u*total
    for j,w in enumerate(weights):
        target-=w
        if target<=0:return j
    return len(weights)-1
def c12(rng):
    utilities=[[rng.random() for _ in range(6)] for _ in range(100)]
    def run(beta):
        c=[1]*6
        for row in utilities:
            i=max(range(6),key=lambda j:row[j]+beta*math.log(c[j]))
            c[i]+=1
        return hhi([x-1 for x in c])
    return run(.9),run(0.0),run(0.0)
def c13(rng):
    q=[rng.random() for _ in range(100)]
    coarse=[x+rng.gauss(0,.40) for x in q]
    audited=[x+rng.gauss(0,.10) for x in q]
    clip=lambda v:max(0.0,min(1.0,v))
    control=statistics.mean((clip(a)-v)**2 for a,v in zip(coarse,q))
    improved=statistics.mean((clip(.3*a+.7*z)-v)**2 for a,z,v in zip(coarse,audited,q))
    return improved,control,control
def c14(rng):
    preferences=[[rng.random() for _ in range(8)] for _ in range(24)]
    def allocate(bonus):
        counts=[0]*8
        for row in preferences:
            i=max(range(8),key=lambda j:row[j]+
                  (bonus if counts[j]==3 else 0.0))
            counts[i]+=1
        return sum(v>=4 for v in counts)
    return float(allocate(2.5)),float(allocate(0)),float(allocate(0))
def c15(rng):
    arrivals=[min(20,max(0,round(rng.gauss(9,3)))) for _ in range(65)]
    def process(adaptive):
        q=0;history=[]
        for a in arrivals:
            q+=a
            cap=12 if adaptive and q>15 else 7
            q=max(0,q-cap);history.append(q)
        return statistics.mean(history)
    return process(True),process(False),process(False)
def c16(rng):
    n=60;groups=[i//30 for i in range(n)]
    initial=[(.2 if g==0 else .8)+rng.uniform(-.08,.08) for g in groups]
    coins={(i,j):rng.random() for i in range(n) for j in range(i+1,n)}
    def interact(homophily):
        opinions=initial[:]
        adj=[[] for _ in range(n)]
        for (i,j),u in coins.items():
            p=(.5 if groups[i]==groups[j] else .03) if homophily else .25
            if u<p:adj[i].append(j);adj[j].append(i)
        for _ in range(6):
            opinions=[(.6*opinions[i]+.4*statistics.mean([opinions[j] for j in adj[i]]))
                      if adj[i] else opinions[i] for i in range(n)]
        return abs(statistics.mean(opinions[:30])-statistics.mean(opinions[30:]))
    return interact(True),interact(False),interact(False)
def c17(rng):
    # Potential rewards are generated ex ante for BOTH arms and all periods.
    rewards=[[rng.gauss((.72 if t<40 else .24) if a==0 else (.38 if t<40 else .68),.18)
              for a in range(2)] for t in range(80)]
    explore=[rng.random() for _ in range(80)]
    tie=[rng.random() for _ in range(80)]
    def bandit(delay):
        total=[.5,.5];n=[1,1];pending=[];regret=0.0
        for t in range(80):
            for due,arm,x in list(pending):
                if due<=t:
                    total[arm]+=x;n[arm]+=1;pending.remove((due,arm,x))
            arm=int(tie[t]>.5) if explore[t]<.12 else max((0,1),key=lambda a:total[a]/n[a])
            actual_mean=(.72 if t<40 else .24) if arm==0 else (.38 if t<40 else .68)
            regret+=max((.72 if t<40 else .24),(.38 if t<40 else .68))-actual_mean
            pending.append((t+delay+1,arm,rewards[t][arm]))
        return regret
    return bandit(6),bandit(0),bandit(0)
def c18(rng):
    tastes=[rng.uniform(-.6,.6) for _ in range(120)]
    def reward(proxy):
        return statistics.mean(3.0 if ((2*1.0-1.5+t if proxy else 2*3.0-1.5+t)>
            (2*3.0-1.0 if proxy else 2*0.0-1.0)) else 0.0 for t in tastes)
    # Above rewards: proxy heavily rewards publicity = score 3, whereas
    # substantive work gives score1. Baseline rewards actual quality.
    return reward(True),reward(False),reward(False)
def c19(rng):
    prices=[8]*100
    values=[rng.uniform(4,18) for _ in prices]
    preferences=[[rng.gauss(0,6) for _ in range(12)] for _ in prices]
    def auction(unequal):
        cash=[40 if i<6 else 120 for i in range(12)] if unequal else [80]*12
        owned=[0.0]*12
        for v,pref in zip(values,preferences):
            eligible=[i for i in range(12) if cash[i]>=8]
            if not eligible:break
            winner=max(eligible,key=lambda i:cash[i]*.025+pref[i])
            owned[winner]+=v;cash[winner]-=8
        return gini(owned)
    return auction(True),auction(False),auction(False)
def c20(rng):
    tastes=[rng.uniform(-.5,.5) for _ in range(140)]
    def choices(top_prize):
        if top_prize:
            # Risky option beats the fictional 9-point rival half the time;
            # the safe 7-point option never beats them.
            return statistics.mean(1.0 if (.5+t*.1)>0 else 0.0 for t in tastes)
        return statistics.mean(1.0 if (6+t)>7 else 0.0 for t in tastes)
    return choices(True),choices(False),choices(False)
def c21(rng):
    skill=[rng.uniform(.0,1.0) for _ in range(12)]
    shocks=[[rng.gauss(0,.35) for _ in range(12)] for _ in range(100)]
    def tournament(reinvest):
        wins=[0]*12
        for t in range(100):
            choice=max(range(12),key=lambda i:skill[i]+shocks[t][i]+
                       (.04*min(wins[i],15) if reinvest else 0.0))
            wins[choice]+=1
        return hhi(wins)
    return tournament(True),tournament(False),tournament(False)
def c22(rng):
    n=60;coins={(i,j):rng.random() for i in range(n) for j in range(i+1,n)}
    def bridges(norm):
        crossing=0
        for (i,j),u in coins.items():
            if i//30==j//30:continue
            crossing+=int(u<(.16 if norm else .02))
        return crossing/(30*30)
    return bridges(True),bridges(False),bridges(False)
def c23(rng):
    q=[rng.random() for _ in range(100)]
    coins=[rng.random() for _ in range(100)]
    truth=set(sorted(range(100),key=lambda i:q[i],reverse=True)[:10])
    def precision(nonrandom):
        scored=[q[i] if coins[i]<(.12 if nonrandom and q[i]>.8 else .68)
                else 0.0 for i in range(100)]
        top=set(sorted(range(100),key=lambda i:(scored[i],-i),reverse=True)[:10])
        return len(top&truth)/10
    return precision(True),precision(False),precision(False)
def c24(rng):
    draws=[rng.random() for _ in range(350)]
    def exposure(alpha):
        counts=[1]*10
        for u in draws:
            weights=[c**alpha for c in counts]
            counts[choose_weights(weights,u)]+=1
        return gini([n-1 for n in counts])
    return exposure(1.6),exposure(0.0),exposure(0.0)
def c25(rng):
    # These are hypothetical choices under an explicitly supplied utility.
    expected=[rng.uniform(.05,1.0) for _ in range(120)]
    participation_cost=[rng.uniform(.05,.35) for _ in range(120)]
    def participation(show_unknown):
        return statistics.mean(1.0 if ((.6*x if show_unknown else 0.0)>cost)
                               else 0.0 for x,cost in zip(expected,participation_cost))
    return participation(True),participation(False),participation(False)
def c26(rng):
    counts=[[rng.randint(0,6) for _ in range(3)] for _ in range(40)]
    old=[sum(x*y for x,y in zip(row,[2,1,3])) for row in counts]
    new=[sum(x*y for x,y in zip(row,[4,.3,.2])) for row in counts]
    def inversion(retro):
        scores=new if retro else old
        n=0;d=0
        for i in range(40):
            for j in range(i+1,40):
                if old[i]==old[j] or scores[i]==scores[j]:continue
                d+=1;n+=int((old[i]-old[j])*(scores[i]-scores[j])<0)
        return n/d if d else 0.0
    return inversion(True),inversion(False),inversion(False)

MODELS={12:c12,13:c13,14:c14,15:c15,16:c16,17:c17,18:c18,
        19:c19,20:c20,21:c21,22:c22,23:c23,24:c24,25:c25,26:c26}
DIRECTIONS={12:1,13:-1,14:1,15:-1,16:1,17:1,18:-1,
            19:1,20:1,21:1,22:1,23:-1,24:1,25:1,26:1}
def evaluate(n):
    if n not in MODELS:raise ValueError("SCENARIO_UNKNOWN")
    diffs=[];placebos=[];treat=[];base=[]
    for i in range(N_REPS):
        rng=random.Random(20263000+100*n+i)
        intervention,rival,placebo=MODELS[n](rng)
        if any(not math.isfinite(x) for x in (intervention,rival,placebo)):
            raise ValueError("NONFINITE_MODEL_OUTPUT")
        treat.append(intervention);base.append(rival)
        diffs.append(intervention-rival)
        placebos.append(placebo-rival)
    avg=statistics.mean(diffs)
    se=statistics.stdev(diffs)/math.sqrt(N_REPS)
    lower=avg-1.96*se;upper=avg+1.96*se
    want=DIRECTIONS[n]
    supported=lower>0 if want==1 else upper<0
    rejected=upper<0 if want==1 else lower>0
    if any(abs(x)>1e-12 for x in placebos):
        status="INVALID_PLACEBO"
    else:
        status="SUPPORTED_INSIDE_GENERATIVE_MODEL" if supported else (
            "FALSIFIED_INSIDE_GENERATIVE_MODEL" if rejected else "INCONCLUSIVE_MONTE_CARLO")
    return dict(cycle=f"ABH25B-C{n}",model="SYNTHTETIC_GENERATIVE_ONLY",
       intervention_mean=statistics.mean(treat),rival_mean=statistics.mean(base),
       difference_mean=avg,monte_carlo_se=se,mc95_lower=lower,mc95_upper=upper,
       prespecified_direction="+" if want==1 else "-",
       placebo_max_difference=max(abs(x) for x in placebos),
       status=status,paired_replicates=N_REPS,seed_start=20263000+100*n,
       code_generated_outcomes_not_human_observations=True,
       source="MODEL_ASSUMPTIONS_NOT_EMPIRICAL_CALIBRATION",
       causal_effect_on_real_people=False,scientific_grade="0/3")
def main():
    if len(sys.argv)>2:raise SystemExit("Usage: python c12_c26_formal_mechanisms.py [CYCLE]")
    selection=[int(sys.argv[1])] if len(sys.argv)==2 else list(MODELS)
    results=[evaluate(n) for n in selection]
    print(json.dumps({"schema":"pfl.abh25b.formal_generators.v1","results":results,
      "total_executed_scenarios":len(results),
      "NOT_EMPIRICAL_VALIDATION":True,"external_participants":0,
      "model_assumptions_frozen_before_run":True},indent=2,sort_keys=True))
if __name__=="__main__":main()
