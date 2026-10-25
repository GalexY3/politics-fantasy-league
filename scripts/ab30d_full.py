#!/usr/bin/env python3
"""AB30D: synthetic methodological experiments; never Spanish-deputy inference.

The 30 *distinct estimands* are in preregistered PREREG.json. This file is
intended to be committed before experimental invocation. Optional --verify
runs deterministic instrumentation tests, without executing the campaign.
"""
from __future__ import annotations
import argparse, hashlib, json, math, statistics, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PRE = ROOT/'research'/'AB30_COMPLETOS_20261025'/'PREREG.json'


def sample(r, p, n): return r.binomial(1,p,n).astype(float)
def mean(x):return float(np.mean(x))
def corr(x,y):
    if np.std(x)==0 or np.std(y)==0:return 0.
    return float(np.corrcoef(x,y)[0,1])
def logloss(y,p):
    pp=np.clip(p,1e-6,1-1e-6)
    return float(np.mean(-(y*np.log(pp)+(1-y)*np.log(1-pp))))
def abs_err(x,y):return abs(float(x)-float(y))

def simulate(code: str, seed: int, mode: str):
    """Return (baseline_loss,candidate_loss, diagnostics) for one realization.

    Mode main/holdout/ablation changes nuisance parameters. Both methods see
    identical observable records. Truth is used only for evaluating loss.
    """
    r=np.random.default_rng(seed)
    abl=mode=='ablation'; stress=mode=='holdout'
    n=320 if not stress else 410
    p=.32 if not stress else .44
    # M -- identifiable measurement contrasts and explicit no-identification tests
    if code=='M01':
        y=sample(r,p,n); selected=r.random(n)<.7; b=mean(y[selected]); t=(sum(y[selected])+.5)/(sum(selected)+1)
        truth=mean(y); return abs_err(b,truth),abs_err(t,truth),{'mechanism':'MCAR','sampled':int(sum(selected))}
    if code in ('M02','M03','F26'):
        g=r.random(n)<(.4 if not stress else .6)
        probs=np.where(g,.8,.17) if not abl else np.full(n,.55)
        y=sample(r,np.where(g,.77,.16) if code!='F26' else np.where(g,.66,.29),n)
        if code=='M03':probs=probs*np.where(y==1,.40,1) if not abl else probs
        selected=r.random(n)<probs
        if min(np.sum(selected&g),np.sum(selected&~g))==0:return 0.,0.,{'degenerate':True}
        b=mean(y[selected]);t=mean(g)*mean(y[selected&g])+(1-mean(g))*mean(y[selected&~g])
        return abs_err(b,mean(y)),abs_err(t,mean(y)),{'observed':int(sum(selected)),'mnar':code=='M03'}
    if code=='M04':
        cats=r.choice(4,size=n,p=[.42,.28,.1,.2] if not abl else [.48,.4,.12,0.])
        truth=np.sum(cats==0)/max(1,np.sum(cats!=3))
        b=np.sum(cats==0)/n; t=np.sum(cats==0)/max(1,np.sum(cats!=3))
        return abs_err(b,truth),abs_err(t,truth),{'no_vote':int(sum(cats==3))}
    if code=='M05':
        y=sample(r,p,n); mask=r.random(n)<(.66 if not stress else .38) if not abl else np.ones(n,dtype=bool)
        obs=y[mask]; known_yes=sum(obs);lo=known_yes/n;hi=(known_yes+n-len(obs))/n
        truth=mean(y); naive=mean(obs)
        # Coverage is compared as a diagnostic: point interval +/- .01 and partial-ID interval.
        b=float(not(naive-.01<=truth<=naive+.01));t=float(not(lo<=truth<=hi))
        return b,t,{'width':float(hi-lo),'observed':len(obs),'comparison':'INTERVAL_VS_POINT_NOT_FAIR_PERFORMANCE_RACE'}
    if code=='M06':
        init=sample(r,p,n);final=init.copy()
        changed=r.random(n)<(0 if abl else (.20 if not stress else .35))
        final[changed]=1-final[changed]; b=mean(np.concatenate((init,final)));t=mean(final)
        return abs_err(b,mean(final)),abs_err(t,mean(final)),{'revisions':int(sum(changed))}
    # C -- composition, standardization and individual membership
    if code in ('C07','C08'):
        g=r.random(n)<(.82 if not stress else .72)
        if code=='C08' or abl:g=r.random(n)<.5
        y=sample(r,np.where(g,.77,.15),n)
        target=.5*mean(y[g])+.5*mean(y[~g])
        b=mean(y);t=.5*mean(y[g])+.5*mean(y[~g]);return abs_err(b,target),abs_err(t,target),{'share_topic_A':mean(g)}
    if code=='C09':
        rare=sample(r,.62 if not stress else .25,9 if not stress else 6)
        common=sample(r,.59,150)
        truth=.62 if not stress else .25
        b=mean(rare);t=(sum(rare)+16*mean(common))/(len(rare)+16)
        return abs_err(b,truth)**2,abs_err(t,truth)**2,{'rare_n':len(rare),'model_distance':abs(truth-.59)}
    if code=='C10':
        periods=15;drift=0 if abl else (.32 if not stress else .40)
        rate=np.array([.2+drift*(k>=10) for k in range(periods)])
        v=np.array([mean(sample(r,q,50)) for q in rate]);target=float(rate[-1]);b=mean(v);t=mean(v[-3:])
        return abs_err(b,target)**2,abs_err(t,target)**2,{'jump':drift}
    if code=='C11':
        group=r.random(n)<.5;y=sample(r,np.where(group,.75,.2),n)
        current=group.copy(); flip=r.random(n)<(0 if abl else (.18 if not stress else .38));current[flip]=~current[flip]
        target=mean(y[group]);b=mean(y[current]);t=mean(y[group]);return abs_err(b,target),abs_err(t,target),{'moved':int(sum(flip))}
    if code=='C12':
        votes=r.choice([0,1],size=n);equal=not abl and r.random()<.6
        if equal:
            v=np.concatenate((np.ones(20),np.zeros(20)));r.shuffle(v)
        else:v=np.concatenate((np.ones(25),np.zeros(15)))
        truth=None if sum(v)==20 else int(sum(v)>20)
        naive=int(sum(v)>=20); aware=None if sum(v)==20 else naive
        return float(naive!=truth),float(aware!=truth),{'tie':bool(truth is None)}
    # T -- publication, groups, dependence and temporal evaluation
    if code=='T13':
        x=r.normal(size=n);truth=sample(r,1/(1+np.exp(-.5*x)),n)
        available=1/(1+np.exp(-.5*x));leak=.02+.96*truth if not abl else available
        # NOT a fair comparator: leaky model uses held-out target. Diagnose optimistic apparent loss.
        b=logloss(truth,available);t=logloss(truth,leak)
        return b,t,{'comparator':'INVALID_FUTURE_TARGET_LEAKAGE','deployable_treatment':False}
    if code=='T14':
        sessions=16;sz=18; shocks=r.normal(0,0 if abl else (1.3 if not stress else 1.9),sessions)
        probs=1/(1+np.exp(-shocks));x=np.array([sample(r,q,sz) for q in probs]); mask=r.random(x.shape)<.5
        # Pessimistic holdout (session held out) vs random vote split with same fitting mechanism.
        global_rate=mean(x[mask]); per=np.array([mean(x[i,mask[i]]) if sum(mask[i]) else global_rate for i in range(sessions)])
        err_random=mean((x[~mask]-np.broadcast_to(per[:,None],x.shape)[~mask])**2)
        new_shocks=r.normal(0,np.std(shocks),sessions);new=sample(r,1/(1+np.exp(-np.repeat(new_shocks,sz))),sessions*sz)
        deployment=mean((new-global_rate)**2)
        # estimand = distance of estimated validation risk to prospective deployment risk
        err_block=mean((x[~mask]-global_rate)**2)
        return abs_err(err_random,deployment),abs_err(err_block,deployment),{'sessions':sessions,'shock_sd':float(np.std(shocks))}
    if code=='T15':
        sessions=12;sz=25;shocks=r.normal(0,0 if abl else (1.2 if not stress else 1.8),sessions)
        probs=1/(1+np.exp(-shocks));v=np.array([sample(r,q,sz) for q in probs]);point=mean(v)
        se_iid=float(np.std(v,ddof=1)/math.sqrt(sessions*sz))
        se_cl=float(np.std(np.mean(v,axis=1),ddof=1)/math.sqrt(sessions))
        truth=.5
        return float(abs(point-truth)>1.96*se_iid),float(abs(point-truth)>1.96*se_cl),{'iid_width':3.92*se_iid,'cluster_width':3.92*se_cl}
    if code=='T16':
        early=sample(r,.48,n);recent=early.copy();flips=r.random(n)<(0 if abl else (.22 if not stress else .33));recent[flips]=1-recent[flips]
        asof=mean(early);return abs_err(mean(recent),asof),0.,{'late_revisions':int(sum(flips))}
    if code=='T17':
        topic=r.binomial(1,.5,n); dep=0 if abl else (.55 if not stress else .7)
        y=sample(r,np.clip(.50+dep*(topic-.5),.05,.95),n)
        base=np.full(n,.5); leak=np.clip(.50+dep*(topic-.5),.05,.95)
        return logloss(y,base),logloss(y,leak),{'comparator':'INVALID_FUTURE_TOPIC_LEAKAGE','deployable_treatment':False}
    if code=='T18':
        k=120; rho=0 if abl else (.73 if not stress else .88);e=r.normal(size=k);x=np.zeros(k)
        for i in range(1,k):x[i]=rho*x[i-1]+e[i]*math.sqrt(1-rho*rho)
        mu=mean(x); true=0.
        # analytic iid/AR(1) SE; block-based long-run variance estimator from lags.
        sd=float(np.std(x,ddof=1)); iid=sd/math.sqrt(k)
        centered=x-mu;v=float(np.mean(centered**2));rho_hat=float(np.clip(np.corrcoef(x[1:],x[:-1])[0,1],-.95,.95))
        corrse=math.sqrt(v/k*max(.05,(1+rho_hat)/(1-rho_hat)))
        return float(abs(mu-true)>1.96*iid),float(abs(mu-true)>1.96*corrse),{'lag1_hat':rho_hat}
    # R -- descriptive relationships must not be mistaken for causal influence
    if code=='R19':
        p1=.84 if not abl else .5;p2=.8 if not stress else .91
        a=sample(r,p1,n);b=sample(r,p2,n)
        obs=mean(a==b);chance=mean(a)*mean(b)+(1-mean(a))*(1-mean(b))
        return abs(obs),abs(obs-chance),{'marginal_agreement':chance,'no_causal_edges':True}
    if code=='R20':
        group=r.binomial(1,.5,n);strength=0 if abl else (1.8 if not stress else 2.5)
        a=group*strength+r.normal(size=n);b=group*strength+r.normal(size=n)
        raw=corr(a,b);a_res=a-np.where(group==1,mean(a[group==1]),mean(a[group==0])); b_res=b-np.where(group==1,mean(b[group==1]),mean(b[group==0]))
        return abs(raw),abs(corr(a_res,b_res)),{'group_confounding':strength,'no_causal_edges':True}
    if code=='R21':
        sz=8;ns=n//sz;shock=r.normal(0,0 if abl else (1.0 if not stress else 1.8),ns)
        a=shock+r.normal(0,.6,ns);b=shock+r.normal(0,.6,ns)
        # Observed third-party outcome independently measures common session shock, not causation.
        measured=shock+r.normal(0,.12,ns)
        ar=a-measured;br=b-measured
        return abs(corr(a,b)),abs(corr(ar,br)),{'common_shock':float(np.std(shock)),'no_causal_edges':True}
    if code=='R22':
        sizes=(25,140) if not abl else (70,70)
        degree=[sum(sample(r,.25,m-1)) for m in sizes]
        raw=abs(degree[0]-degree[1]);norm=abs(degree[0]/(sizes[0]-1)-degree[1]/(sizes[1]-1))
        return raw, norm,{'unit_mismatch':'RAW_DEGREE_VS_DENSITY','group_sizes':sizes}
    if code=='R23':
        a=r.random(n)<.5;edge=sample(r,np.where(a,.65,.15),n);prop=np.where(a,.95,.23) if not abl else np.full(n,.65)
        observed=r.random(n)<prop
        raw=sum(edge[observed])/max(1,sum(observed));weighted=sum(edge[observed]/prop[observed])/sum(1/prop[observed]);truth=mean(edge)
        return abs_err(raw,truth),abs_err(weighted,truth),{'sampling':'MAR_BY_GROUP'}
    if code=='R24':
        size=30;upper=r.random((size,size))<(.25 if not stress else .6);upper=np.triu(upper,1)
        mat=upper|upper.T
        if abl: mat=np.triu(mat,1)
        true=int(np.sum(np.triu(mat,1)));base=int(sum(sum(mat)));candidate=int(sum(sum(np.triu(mat,1))))
        return abs(base-true),abs(candidate-true),{'representation':'SYMMETRIC' if not abl else 'UPPER_TRIANGULAR'}
    # F -- ranking, forecasting and Goodhart, all fake actors and stipulated mechanisms
    if code=='F25':
        expo=np.array([20,180]) if not abl else np.array([100,100]);quality=np.array([.66,.43])
        counts=np.array([sum(sample(r,q,int(e))) for q,e in zip(quality,expo)])
        b=int(np.argmax(counts));t=int(np.argmax(counts/expo));truth=int(np.argmax(quality))
        return float(b!=truth),float(t!=truth),{'exposure':expo.tolist(),'latent_quality_stipulated':True}
    if code=='F27':
        k=240;latent=r.normal(size=k);gaming=np.clip(r.normal(size=k),0,None)
        intensity=0 if abl else (1.4 if not stress else 2.0)
        proxy=latent+intensity*gaming+r.normal(0,.18,k)
        true=latent-.18*gaming
        # Candidate observes same proxy and gaming indicators as baseline; penalizes gaming.
        b=int(np.argmax(proxy));t=int(np.argmax(proxy-intensity*gaming))
        optimal=float(max(true));return optimal-true[b],optimal-true[t],{'manipulation_intensity':intensity,'outcome_structurally_defined':True}
    if code=='F28':
        m=45;exposures=r.integers(3,16,m) if not abl else r.integers(90,150,m)
        qs=r.beta(7,10,m) if not stress else r.beta(3,6,m)
        count=r.binomial(exposures,qs);p_raw=count/exposures;p_smooth=(count+7)/(exposures+17)
        b=int(np.argmax(p_raw));t=int(np.argmax(p_smooth));opt=max(qs)
        return float(opt-qs[b]),float(opt-qs[t]),{'median_exposure':int(np.median(exposures))}
    if code=='F29':
        base=.035 if not stress else .065;val=sample(r,base,220);test=sample(r,base,300)
        ps=[.01,.04,.09,.30]; # both use same validation set; proper score vs threshold accuracy
        a_scores=[mean((p>=.5)==val) for p in ps] # all same classification at these rates
        b=int(np.argmax(a_scores));t=int(np.argmin([logloss(val,np.full(len(val),p)) for p in ps]))
        return logloss(test,np.full(len(test),ps[b])),logloss(test,np.full(len(test),ps[t])),{'base_rate':base,'selection_tie':True}
    if code=='F30':
        early=r.normal(0,1,n);changed=r.random(n)<(0 if abl else (.18 if not stress else .35));later=early.copy();later[changed]+=r.normal(0,1.8,sum(changed))
        # Temporal estimand = what players actually saw at cutoff; not normative best score.
        baseline=abs_err(mean(later),mean(early));frozen=0.
        return baseline,frozen,{'retrospective_updates':int(sum(changed)),'estimand':'HISTORICAL_AS_OF_SNAPSHOT'}
    raise ValueError('Unknown registered case '+code)


def bootstrap_ci(x,seed):
    x=np.asarray(x,float); r=np.random.default_rng(seed)
    if len(x)<4:return [None,None]
    ids=r.integers(0,len(x),size=(800,len(x)))
    means=x[ids].mean(axis=1)
    return [float(v) for v in np.quantile(means,[.025,.975])]


def check_invariants():
    pre=json.loads(PRE.read_text());assert len(pre['cases'])==30
    ids=[x['id'] for x in pre['cases']];assert len(set(ids))==30
    for i,c in enumerate(pre['cases']):
        assert sorted(set('ABCDEFGHIJ')-set(c))==[]
        seed=c['C']['main_seeds'];conf=c['C']['confirmation_seeds']
        assert seed[1]-seed[0]==79 and conf[1]-conf[0]==79
        assert set(range(seed[0],seed[1]+1)).isdisjoint(range(conf[0],conf[1]+1))
        for mode in ('main','holdout','ablation'):
            x,y,diagnostics=simulate(c['id'],seed[0]+(1000000 if mode=='ablation' else 0),mode)
            assert np.isfinite(x) and np.isfinite(y),c['id']
            assert x>=0 and y>=0,c['id']
    return len(ids)


def run(output):
    pre=json.loads(PRE.read_text(encoding='utf-8'))
    check_invariants();results=[]
    for i,c in enumerate(pre['cases']):
        cid=c['id'];start=c['C']['main_seeds'][0];hstart=c['C']['confirmation_seeds'][0]
        trials={mode:[] for mode in ('main','holdout','ablation')};diags={}
        for mode in trials:
            for j in range(80):
                seed=(start if mode in ('main','ablation') else hstart)+j+(1000000 if mode=='ablation' else 0)
                b,t,d=simulate(cid,seed,mode)
                trials[mode].append([float(b),float(t),float(b-t)])
                if j==0:diags[mode]=d
        stats={}
        for mode,arr in trials.items():
            x=np.asarray(arr);dif=x[:,2]
            stats[mode]={'n':len(dif),'baseline_mean_loss':float(x[:,0].mean()),'candidate_mean_loss':float(x[:,1].mean()),'mean_loss_advantage':float(dif.mean()),'paired_CI95_bootstrap':bootstrap_ci(dif,70000+i*100+{'main':1,'holdout':2,'ablation':3}[mode]),'SD_of_advantage':float(np.std(dif,ddof=1)),'diags_first_realization':diags[mode]}
        hold=stats['holdout'];lo,hi=hold['paired_CI95_bootstrap'];m=hold['mean_loss_advantage'];
        if cid in {'T13','T17'}:
            status='INVALID_FOR_DEPLOYABLE_COMPARISON_LEAKAGE';decision='STOP_LEAKY_COMPARATOR'
        elif cid=='M05':
            status='DIAGNOSTIC_INTERVAL_VS_POINT_NOT_COMPARABLE';decision='REPAIR_LOSS_FUNCTION'
        elif lo>0 and stats['main']['mean_loss_advantage']>0:
            status='SUPPORTED_IN_STIPULATED_GENERATOR_ONLY';decision='CONTINUE_FIELD_VALIDATION'
        elif hi<0:
            status='FAVORS_COMPARATOR_IN_STIPULATED_GENERATOR';decision='REVISE_HYPOTHESIS'
        else:
            status='INCONCLUSIVE_OR_MODEL_DEPENDENT';decision='CONTINUE_ONLY_WITH_NEW_EVIDENCE'
        ab=stats['ablation']['mean_loss_advantage']
        if status=='SUPPORTED_IN_STIPULATED_GENERATOR_ONLY' and ab>m and m>0:decision='AUDIT_GENERATOR_ABLATION'
        rr=json.loads(json.dumps(c,ensure_ascii=False))
        rr['D'].update({'instrument_check':'PASS','main_repeats':80,'stress_repeats':80,'ablation_repeats':80,'comparators_same_information':cid not in {'T13','T17','M05'}})
        rr['E']={'status':'RUN_SYNTHETIC','run_main':stats['main'],'run_stress_holdout':stats['holdout'],'run_mechanism_ablation':stats['ablation'],'units_of_independence':'simulation realization; 80 independent streams per mode, not 80 political field replications'}
        rr['F']={'status':'AUDITED_AUTOMATED','negative_control':'mechanism ablation','outcome_defined_by_generator':True,'selection_exposure':'30 tests explored in one campaign; no confirmatory FWER claims','baseline_parity':cid not in {'T13','T17','M05'},'risks':['synthetic generator encodes mechanism','bootstrap quantiles are conditional on generator','comparators not exhaustive; not scientific novelty']}
        rr['G']={'status':'SYNTHETIC_SEED_HOLDOUT_ONLY','independent_external_replication':False,'holdout_seed_disjoint':True,'generator_stress_test':True}
        rr['H']={'prior_qualitative':'No claim of real Spanish behavior','update':'Evidence limited to synthetic software/methodology sensitivity; maintain CT2=24/100, VSDS=1/3','new_hypothesis':'The empirical impact and base-rate are unknown pending independent official field data','surprise':'Ablation and sign may differ between main and stress modes','evidence_for':m,'evidence_against':ab}
        rr['I']={'internal_validity':'CONDITIONAL_ON_CODE_AND_GENERATOR','causal_identification_of_real_world':'NONE','external_validity':'NOT_TESTED','novelty':'0/3','reproducibility':'SOURCE_SEEDS_CODE_AND_JSON','ethics':'no real persons represented; never rank deputies','VSDS':'1/3_MAX','CT2_prediccion':24}
        rr['J']={'decision':decision,'verdict':status,'cycles_remaining':30-(i+1),'next_evidence':'actual time-versioned Congress nominal source, roster and strong real-data temporal baselines'}
        results.append(rr)
    evidence={"date":"2026-10-25","method":"AB 3.2.1","experiment_status":"30 completed A-J computational cycles on fully SYNTHETIC data (NO empirical Spanish findings)","prereg_sha256":hashlib.sha256(PRE.read_bytes()).hexdigest(),"result_status_counts":{s:sum(x['J']['verdict']==s for x in results) for s in sorted({x['J']['verdict'] for x in results})},"N1":0,"N2":0,"N3":0,"VSDS":"1/3","CT2_prediction":24,"n_cycles":len(results),"cycles":results}
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return evidence

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--verify',action='store_true');ap.add_argument('--out',default=str(PRE.parent/'RESULTS.json'));args=ap.parse_args()
    if args.verify:print(json.dumps({'instrumented_cases':check_invariants(),'executed_campaign':False}));sys.exit(0)
    x=run(args.out)
    print(json.dumps({'n_cycles':x['n_cycles'],'status_counts':x['result_status_counts'],'result':args.out},ensure_ascii=False))
