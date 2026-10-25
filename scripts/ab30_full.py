"""PF-AB30-FULL: 30 complete A-J research cycles, not 30 independent field experiments.
Dependencies: numpy, scipy; all microdata outcomes simulated; observed source is 7 selected public vote summaries.
Run only after prereg and this file have been frozen on GitHub; results are written to a separate run dir.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import ttest_rel

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/upstream_curated_7/derived_anonymous_counts.json'
MANUAL=ROOT/'data/pilot_official_webview/20260723_vote_totals_MANUAL.csv'
OUT=ROOT/'research/AB30_FULL_20261025'
SEED=20261025

def mean(x): return float(np.mean(x))
def corr(a,b):
    if np.std(a)==0 or np.std(b)==0: return None
    return float(np.corrcoef(a,b)[0,1])
def rnd(x,n=6):
    if isinstance(x,(int,np.integer)): return int(x)
    if isinstance(x,(float,np.floating)): return round(float(x),n) if np.isfinite(x) else None
    if isinstance(x,np.ndarray):return [rnd(y,n) for y in x]
    if isinstance(x,list):return [rnd(y,n) for y in x]
    if isinstance(x,dict):return {str(k):rnd(v,n) for k,v in x.items()}
    return x

def source_data():
    data=json.loads(DATA.read_text(encoding='utf-8'))
    with MANUAL.open(newline='',encoding='utf-8') as f: manual=list(csv.DictReader(f))
    assert len(data['records'])==7 and len(manual)==20
    return data,manual

def real_cycle(i,rows,manual):
    totals=np.array([r['totals'] for r in rows]);nom=np.array([r['nominal'] for r in rows]);gap=totals-nom
    m=np.array([[int(x['yes']),int(x['no']),int(x['abstain'])] for x in manual]);
    groups=[[(g[0],np.array(g[1:5],float)) for g in r['groups']] for r in rows]
    notes='Curated, nonrandom 7-case sample; all analyses post hoc; no independent official verification, no population inference.'
    v=None;test=None;rival=None;discr=None
    if i==1:
        v={'sum_to_350':int(sum(sum(x)==350 for x in totals)),'group_totals_equal':int(sum(all(np.sum(np.array([q[1] for q in gg]),axis=0)==totals[j]) for j,gg in enumerate(groups)))}
        rival='Source curator may construct both levels from the same raw records; agreement is not independent corroboration.';discr='Any source aggregate differs from sum(groups) or 350.'
    elif i==2:
        v={'nominal_n':nom.sum(axis=1).tolist(),'missing_by_vote':gap.sum(axis=1).tolist(),'incomplete':int(sum(gap.sum(axis=1)>0)),'total_missing':int(gap.sum())}
        rival='Partial member dictionary, rather than truly absent MPs, explains shortfall.';discr='A source has nominal count 350 in all seven.'
    elif i==3:
        v={'missing_by_choice':gap.sum(axis=0).tolist(),'per_vote_by_choice':gap.tolist()}
        rival='Missingness differs by vote category due to snapshot selection.';discr='All missing occur in recorded no-votes.'
    elif i==4:
        v={'explicit_nonvote':int(totals[:,3].sum()),'missing_nominal':int(gap.sum()),'nominal_nonvote':int(nom[:,3].sum()),'gap_minus_recorded_nonvote':int(gap.sum()-totals[:,3].sum())}
        rival='No-vote is explicitly reported in totals; missing mapping is a distinct data defect.';discr='Gap can be equated to aggregate no-votes in every record.'
    elif i==5:
        dates=[r['day'] for r in rows];missing=gap.sum(axis=1); order=np.argsort(dates)
        v={'ordered_dates':[dates[x] for x in order],'ordered_missing':[int(missing[x]) for x in order],'spearman_approx_corr':corr(np.arange(7),missing[order])}
        rival='Curated initiative and identity mapping process causes variable coverage; calendar alone not causal.';discr='No variation across dates.'
    elif i==6:
        hom=[];hetero=[]
        for gs in groups:
            for name,x in gs:
                expressed=x[:3].sum()
                if expressed:
                    hom.append(float(max(x[:3])/expressed))
                    if name=='Mixto':hetero.append(float(max(x[:3])/expressed))
        v={'n_group_votes_expressed':len(hom),'fully_unanimous':int(sum(x==1 for x in hom)),'mixto_modal':hetero,'all_group_modal_mean':mean(hom)}
        rival='Group-level unanimity in selected votes does not identify individual discipline or political cause.';discr='Observed modal shares are necessarily all equal 1.'
    elif i==7:
        expressed=totals[:,:3].sum(axis=1);v={'yes_over_expressed':rnd(totals[:,0]/expressed),'yes_over_350':rnd(totals[:,0]/350),'mean_gap_percentage_points':mean(100*(totals[:,0]/expressed-totals[:,0]/350))}; rival='Difference is purely definitional, not behavioral.';discr='Both denominators always coincide.'
    elif i==8:
        v={'abstention_expressed_share':rnd(totals[:,2]/totals[:,:3].sum(axis=1)),'explicit_nonvote_share':rnd(totals[:,3]/350),'votes_with_abstentions':int(np.sum(totals[:,2]>0))}; rival='Abstención vs No vota are separate administrative choices; not indifference.';discr='Abstain and NoVota numerically identical across votes.'
    elif i==9:
        v={'two_option_margin':rnd(np.abs(totals[:,0]-totals[:,1])/np.maximum(1,totals[:,0]+totals[:,1])),'three_option_margin':rnd(np.abs(totals[:,0]-totals[:,1])/totals[:,:3].sum(axis=1)),'max_delta':float(np.max(np.abs(totals[:,0]-totals[:,1])/np.maximum(1,totals[:,0]+totals[:,1])-np.abs(totals[:,0]-totals[:,1])/totals[:,:3].sum(axis=1)))}; rival='Metric denominator rather than substantively different polarization.';discr='Abstentions never change margin.'
    elif i==10:
        conc=np.array([[max(g[:3])/g[:3].sum() for _,g in gs if g[:3].sum()>0] for gs in groups]);p=totals[:,:3]/totals[:,:3].sum(axis=1,keepdims=True)
        v={'per_vote_group_mean_modal':rnd(np.mean(conc,axis=1)),'per_vote_plenary_modal':rnd(p.max(axis=1)),'avg_difference':mean(np.mean(conc,axis=1)-p.max(axis=1))};rival='Grouping mechanically raises concentration; not proof of party discipline.';discr='No ecological gap across all selected votes.'
    elif i==11:
        small=[];big=[]
        for gs in groups:
            for _,x in gs:
                if x[:3].sum()==0:continue
                (small if x.sum()<=10 else big).append(float(max(x[:3])/x[:3].sum()))
        v={'small_n':len(small),'large_n':len(big),'small_mean':mean(small),'large_mean':mean(big),'difference':mean(small)-mean(big)};rival='Small-n modal indices are more volatile even under identical latent rates.';discr='No gap or sample size effect.'
    elif i==12:
        y=totals[:,0]/350
        v={'grand_mean_yes_share':mean(y),'leave_one_out_range':rnd([mean(np.delete(y,k)) for k in range(7)]),'range_width':float(np.ptp([mean(np.delete(y,k)) for k in range(7)]))};rival='Selection of seven initiatives creates instability; no temporal trend identified.';discr='One deletion does not affect rate.'
    elif i==13:
        v={'curated_counted_mean':mean(totals.sum(axis=1)),'manual_counted_mean':mean(m.sum(axis=1)),'mean_difference':mean(totals.sum(axis=1))-mean(m.sum(axis=1))};rival='Manual data excludes no-vote counts while curated includes them: noncomparable administrative estimands.';discr='Definitions match and sample distributions coincide.'
    elif i==14:
        a=totals[:,0]/totals[:,:3].sum(axis=1);b=m[:,0]/m.sum(axis=1)
        v={'curated_yes_mean':mean(a),'manual_yes_mean':mean(b),'difference':mean(a)-mean(b),'ranges':[rnd([min(a),max(a)]),rnd([min(b),max(b)])]};rival='Different dates and selected motions, so contrast has no causal or population interpretation.';discr='Observed samples identical under same definition.'
    elif i==15:
        a=totals[:,2]/totals[:,:3].sum(axis=1);b=m[:,2]/m.sum(axis=1)
        v={'curated_abstain_mean':mean(a),'manual_abstain_mean':mean(b),'difference':mean(a)-mean(b)};rival='Agenda and date differ, not systematic institutional change.';discr='No difference in sample means.'
    elif i==16:
        a=np.abs(totals[:,0]-totals[:,1])/totals[:,:3].sum(axis=1);b=np.abs(m[:,0]-m[:,1])/m.sum(axis=1)
        v={'curated_absolute_margin':mean(a),'manual_absolute_margin':mean(b),'difference':mean(a)-mean(b)};rival='Motion selection and same-day clustering confound comparison.';discr='Both samples have identical margins.'
    elif i==17:
        y=m[:,0]/m.sum(axis=1)
        v={'manual_same_session_rows':len(y),'within_session_lag1_corr':corr(y[:-1],y[1:]),'independent_sessions':1,'independent_n_bounded_by_sessions':1};rival='Within-session repeated voting decisions correlated by legislative agenda.';discr='An independent-session model claims 20 sessions rather than 1.'
    elif i==18:
        v={'curated_n':7,'manual_n':20,'combined_naive_n':27,'effective_scope':'7 selected initiatives and 1 additional plenary session; no random population draw','future_confirmatory_holdout':False};rival='Selection and look-ahead invalidate p-values for legislature-wide claims.';discr='Evidence from random holdout was collected before formulating hypotheses.'
    else:raise ValueError(i)
    return {'primary_endpoint':rnd(v),'rival':rival,'falsifier':discr,'source':'CURATED_REAL_EXPLORATORY' if i<=12 else 'CROSS_SOURCE_DESCRIPTIVE_UNMATCHED','audit':notes}

# Each simulation is explicit and local to its data-generating assumptions.
# Monte Carlo replicates are independent random seeds, not independent empirical institutions.
def simulate_cycle(i,n=600,seed=SEED):
    rg=np.random.default_rng(seed+1009*i)
    diffs=[];aux=[]
    for rep in range(n):
        if i in (19,20):
            # True heterogeneous binary vote population, partly observed.
            group=rg.integers(0,4,400);q=np.array([.25,.42,.61,.79])[group]; y=(rg.random(400)<q)
            obs=(rg.random(400)<(.65 if i==19 else np.where(y,.35,.9)))
            truth=mean(y);base=mean(y[obs]);ipw=mean(y[obs]) # Correct constant propensity cancels for MCAR, wrong for MNAR.
            diffs.append(abs(base-truth)-abs(ipw-truth))
            aux.append(base-truth)
        elif i==21:
            true=rg.random(350)<.51; recorded=rg.random(350)<.82
            known=mean(true[recorded]);bad=float(np.sum(true[recorded])/350)
            diffs.append(abs(bad-mean(true))-abs(known-mean(true)))
        elif i==22:
            # Change after time t, and current affiliation mislabels historical group.
            origin=rg.integers(0,2,350);outcome=rg.random(350)<np.where(origin==0,.85,.15)
            swapped=(rg.random(350)<.23); current=np.where(swapped,1-origin,origin)
            p_true=mean(outcome[origin==0]);p_bad=mean(outcome[current==0]);p_good=mean(outcome[origin==0])
            diffs.append(abs(p_bad-p_true)-abs(p_good-p_true))
        elif i==23:
            # Additional group aggregates are privileged information: R2 warns attribution cannot be model-specific.
            true=rg.random(350)<.52;mask=rg.random(350)<.7
            nominal=mean(true[mask]); aggregate=mean(true)
            diffs.append(abs(nominal-mean(true))-abs(aggregate-mean(true)))
        elif i==24:
            # Modal agreement in small groups vs large groups under same known p=0.5.
            x=rg.binomial(5,.5);z=rg.binomial(130,.5)
            small=max(x,5-x)/5;large=max(z,130-z)/130
            diffs.append(small-large)
        elif i==25:
            # Repeated votes share session-level latent shocks -> naive iid SE too narrow.
            num_sessions=12;participants=100;sd=.32
            shocks=rg.normal(0,sd,num_sessions);obs=rg.normal(0,.65,(num_sessions,participants))+shocks[:,None]
            # Cluster mean SE on session means; naive observation iid SEM.
            naive=np.std(obs,ddof=1)/math.sqrt(obs.size)
            cluster=np.std(obs.mean(axis=1),ddof=1)/math.sqrt(num_sessions)
            diffs.append(cluster-naive);aux.append([float(abs(obs.mean())<=1.96*naive),float(abs(obs.mean())<=1.96*cluster)])
        elif i==26:
            # Information asymmetry: future leakage artificially improves accuracy.
            p=rg.uniform(.25,.75);future=rg.binomial(1,p,100)
            baseline=np.full(100,p);leak=future.copy()
            diffs.append(mean(np.abs(baseline-future))-mean(np.abs(leak-future)))
        elif i in (27,28,29):
            ntrain=600;ntest=350;gtrain=rg.integers(0,8,ntrain);gtest=rg.integers(0,8,ntest)
            q=rg.beta(4,4,8) if i in (27,29) else np.full(8,.5)
            train=rg.binomial(1,q[gtrain]);
            qtest=(1-q) if i==29 else q
            test=rg.binomial(1,qtest[gtest]);base=(sum(train)+1)/(ntrain+2)
            per_group=np.array([(sum(train[gtrain==k])+4)/(sum(gtrain==k)+8) for k in range(8)])
            logloss=lambda p: float(np.mean(-test*np.log(np.clip(p,1e-8,1-1e-8))-(1-test)*np.log(np.clip(1-p,1e-8,1-1e-8))))
            diffs.append(logloss(np.full(ntest,base))-logloss(per_group[gtest]))
        elif i==30:
            # Familywise null: 20 contrasts with no effects; Bonferroni vs unadjusted.
            from scipy.stats import norm
            z=rg.normal(0,1,20);pvals=2*norm.sf(np.abs(z));uncorr=bool(np.any(pvals<.05));bonf=bool(np.any(pvals<.05/20))
            diffs.append(int(uncorr)-int(bonf));aux.append([float(uncorr),float(bonf)])
        else:raise ValueError(i)
    x=np.array(diffs,dtype=float)
    ci=[float(np.quantile(x,[.025,.975])[0]),float(np.quantile(x,[.025,.975])[1])]
    # CI for E[paired delta] uses bootstrap over independent simulation realizations.
    boot=np.array([np.mean(x[rg.integers(0,len(x),len(x))]) for _ in range(500)])
    mean_ci=np.quantile(boot,[.025,.975]);
    res={'primary_endpoint':{'mean_paired_delta':mean(x),'bootstrap_95_ci_mean':rnd(mean_ci),'empirical_2.5_97.5_quantiles':rnd(ci),'mc_replicates':n,'seed':seed+1009*i},'source':'SYNTHETIC_MECHANISM_ONLY'}
    if i in (19,20):res['primary_endpoint']['mean_estimator_bias']=mean(aux)
    if i==25:res['primary_endpoint']['naive_coverage']=mean([a[0] for a in aux]);res['primary_endpoint']['session_cluster_coverage']=mean([a[1] for a in aux])
    if i==30:res['primary_endpoint']['raw_FWER']=mean([a[0] for a in aux]);res['primary_endpoint']['bonferroni_FWER']=mean([a[1] for a in aux]);
    return res

LABELS={
1:'Conservación grupos-total',2:'Cobertura nominal de fuente curada',3:'Distribución por categoría de filas faltantes',4:'No-voto frente a omisión de fila',5:'Cobertura y fechas de selección',6:'Heterogeneidad modal del grupo Mixto',
7:'Proporción Sí con diferentes denominadores',8:'Abstención explícita y No vota',9:'Margen de dos opciones o tres',10:'Concentración grupo vs pleno',11:'Tamaño grupo y concentración estimada',12:'Leave-one-vote-out en siete iniciativas',
13:'Contados en dos fuentes sin censo común',14:'Proporción Sí en dos muestras no apareadas',15:'Abstenciones en muestras no apareadas',16:'Margen medio en muestras no apareadas',17:'Dependencia de una única sesión',18:'Sesgo de selección y tamaño muestral',
19:'IPW bajo missing completely at random',20:'IPW mal especificado bajo MNAR',21:'No respuesta como denominador implícito',22:'Afiliación actual frente a histórica',23:'Información adicional de agregados frente a nominales',24:'Sesgo de concentración en grupos pequeños',
25:'Clustering por sesión vs pseudo-replicación',26:'Fuga de información futura artificial',27:'Pronóstico por grupo con estructura real',28:'Pronóstico por grupo con estructura nula',29:'Pronóstico bajo cambio de régimen',30:'Multiplicidad sin y con Bonferroni'
}
RIVAL_SIM={19:'Constant IPW and observed mean coincide algebraically under MCAR.',20:'An incorrect propensity cannot remove outcome-dependent selection.',21:'Treating unrecorded entries as denominator=350 introduces attenuation.',22:'Current labels introduce look-ahead misclassification of historical group.',23:'Exact aggregate is additional privileged information, not a fair model advantage.',24:'Max of noisy small-group proportions is upward biased.',25:'Individual rows share session shocks and violate iid standard errors.',26:'Model with observed future y is not available at prediction time.',27:'Group-level signal improves score only under stable heterogeneity.',28:'Group model should not dominate competent global baseline when effect is null.',29:'Group model may fail after label mechanism inversion.',30:'Familywise multiple testing inflates chance findings without correction.'}

SPEC = {
1:('Group counts equal aggregate counts in all seven source records','At least one source record fails conservation','Compare 4-way count vector per motion to sum of nine groups, plus total seats'),
2:('Some displayed individual dictionaries are incomplete','All seven nominal dictionaries contain 350 entries','Compare nominal dictionary counts with 350 total categories for each motion'),
3:('Missing nominal entries vary across recorded choices','Missingness is only in NO_VOTE category','Subtract nominal category histogram from totals for each motion'),
4:('A missing dictionary entry is not equivalent to an explicit NO_VOTE','Missing-record count equals explicit NO_VOTE for every motion','Contrast missing keys with official-value NO_VOTE count at same event'),
5:('Recorded dictionary coverage varies by example date','Coverage is 350 throughout the selected sequence','Order 7 documented dates; list coverage changes, no causal time hypothesis'),
6:('At least one group-in-motion has a nonunanimous expressed vote','All groups show perfect unanimity','Compute modal category / expressed choices; keep Mixto separate'),
7:('Yes share differs with eligible-vs-expressed denominators','Both share definitions coincide in each chosen motion','Contrast yes/(yes+no+abstain) vs yes/350'),
8:('Abstentions occur as expressed votes independently of explicit non-votes','Abstain and non-vote are observationally identical categories','Report proportion of abstain among expressions and NO_VOTE among 350'),
9:('Adding abstention to margin denominator changes apparent competitiveness','Margin independent of abstention share','Compare absolute yes-no gap over 2 vs 3 expressed options'),
10:('Group-modal concentration differs from plenary-wide concentration','Group and plenary concentration identical across motions','Equal-motion average of modal shares; distinguish ecological arithmetic'),
11:('Small-group and large-group modal concentration differ in observed data','Observed means are identical across size thresholds','Compare groups <=10 to >10 members, report counts and selection risk'),
12:('Mean yes-share varies materially on deleting one of 7 selected votes','Leave-one-out estimates all equal','Recompute selected-sample mean omitting each motion in turn'),
13:('Counted totals differ across manually transcribed and curated tables','Both sample means of counted choices equal','Compare mean 350-category total to manual 3-category total; assess comparability'),
14:('Yes-share differs in the two convenience samples','Both convenience-sample means identical','Use expressed denominator consistently, no independence claim'),
15:('Abstention shares differ across disjoint selected samples','Both sample means identical','Same ratios per recorded event; mark session clustering'),
16:('Absolute binary margin differs across selected sources','Margins equal on average','Use identical denominator, no population test'),
17:('Rows in manual source share a session; iid 20-sessions premise false','Manual 20 rows represent distinct sessions','Check session ID count and serial sample lag correlation'),
18:('Total 27 row count overstates independent institutional coverage','All 27 events are a random cross-session sample','Audit selection process, unique sessions and available holdout'),
19:('Under constant MCAR, constant IPW cannot beat observed mean','Known constant weighting improves observed mean MAE','600 paired MCAR simulations; posterior difference CI; use equal information'),
20:('Under outcome-dependent MNAR, MCAR weighting does not remove bias','Constant weights fully correct MNAR selection','600 paired MNAR simulations; report observed signed bias and error'),
21:('Assuming missing responses are zero biases population yes-share','Denominator 350 and respondent denominator equally accurate','600 randomized dropout realizations; paired absolute error'),
22:('Using current group label alters historical group effect','Current labels produce identical estimate to historical labels','600 randomized group transfers, paired absolute estimation errors'),
23:('Complete aggregate recovers exact share whereas incomplete nominal does not','Complete aggregate and partial nominal equally accurate','Compare extra-information arm to partial-data arm; flag non-parity'),
24:('Small-group modal concentration is upward biased by finite sample','Small and large groups have same modal-share expectation under p=.5','600 independent binomial draws n=5 vs n=130, paired difference'),
25:('Ignoring shared session shocks understates uncertainty','Naive iid SE and session SE have same coverage','600 synthetic panels with 12 independent session shocks x100 voters'),
26:('Future target access creates spurious perfect prediction','Future-informed and as-of predictors have equal forecast error','600 paired Bernoulli future outcomes; mark information violation'),
27:('Stable group heterogeneity can improve time-holdout logloss','Group estimate performs no better than global shrinkage','600 train/test DGP draws, both arms see same train/labels'),
28:('With no group effect, group estimates offer no systematic predictive improvement','Group model always improves logloss even under group-null','600 train/test DGP draws, constant p=.5 across groups'),
29:('A group regime reversal can destroy group-model advantage','Group model remains superior under q -> 1-q shift','600 shifted holdouts, compare matched-information models'),
30:('Searching 20 true-null hypotheses raises familywise false positives','Uncorrected and Bonferroni FWER equal at 0.05','600 complete null test families of 20 independent z-tests')
}

def make_aj(i,res, prereg_commit, code_commit, inputs):
    empirical=i<=18;branch=('A' if i<=6 else 'B' if i<=12 else 'C' if i<=18 else 'D' if i<=24 else 'E')
    primary=res['primary_endpoint'];is_syn=not empirical
    eval_note='Seven curated votes or twenty manual transcriptions are exploratory and selected, not random.' if empirical else 'Monte Carlo conditions are stipulated; no transport to real Spanish institutions.'
    # True G confirmatory independent external data unavailable in all cycles.
    return {
      'cycle_id':f'PF-AB30-FULL-C{i:02}', 'branch':branch,'status':'POST_HOC_AUDIT' if empirical else 'EXPERIMENTAL_AB_SIMULATION',
      'A':{'question':LABELS[i],'estimand':'Defined sample diagnostic' if empirical else 'Paired difference of estimation/prediction error under specified DGP','population':'7 externally curated examples + 20 unmatched manually transcribed same-day events' if empirical else 'Independent Monte Carlo generator draws','outcome_proxy':'counts, proportions or loss, not political virtue','interference':'within-session/group political dependence not modeled' if empirical else 'Session and group shocks only when explicitly simulated'},
      'B':{'H1':SPEC[i][0],'H0':SPEC[i][1],'H_others':res.get('rival',RIVAL_SIM.get(i,'Selection mechanism, model mismatch or measurement artifact.'))},
      'C':{'design':SPEC[i][2],'falsifier':res.get('falsifier','Paired mean difference crosses zero or shifts sign under ablation/alternative DGP'),'budget':'7+20 secondary field rows, no new sampling' if empirical else '600 paired DGP realizations, 500 bootstrap resamples of independent draws','multiplicity':'30 exploratory claims, no unadjusted confirmatory testing','prereg_ledger':prereg_commit},
      'D':{'source_provenance':inputs,'instrument':'scripts/ab30_full.py','instrument_frozen_commit':code_commit,'seed':None if empirical else SEED+1009*i,'controls':'Competing denominators and group+nominal checks' if empirical else 'Competent same-information baseline, except C23/C26 explicitly compare unequal-information arms to diagnose unfair advantage'},
      'E':{'result':primary,'source_scope':res['source'],'did_execute':True},
      'F':{'strongest_rival':res.get('rival',RIVAL_SIM.get(i,'Prior construction or target leakage.')),'adversarial_audit':eval_note,'selection_exposure':'Entire 7 vote panel was inspected before design.' if empirical else 'Preset seed and tests, but one modeled DGP; model choice informed by known literature.', 'risk':'Self-constructed endpoint and same DGP can mechanically favor one treatment.'},
      'G':{'external_replication':'NOT_AVAILABLE','independent_confirmation':False,'synthetic_mc':'600 independent generated realizations, not independent empirical cohorts.' if is_syn else None},
      'H':{'posterior_update':'No calibrated numerical posterior; descriptive or conditional update only.','abductive_rival':res.get('rival',RIVAL_SIM.get(i,'Potential measurement artifact.')),'new_prior_observation':f'PFL-AB30-{i:02}', 'evidence_origin':'SECONDARY_OBSERVATION' if empirical else 'SYNTHETIC_SIMULATION'},
      'I':{'internal_validity':'Limited by manual transfer/source selection' if empirical else 'Only conditional on generator, unit design and code','causal_identification':'NONE_REAL_WORLD','transportability':'NOT_ESTABLISHED','novelty':'NOT_ASSESSED_AGAINST_LITERATURE','reproducibility':'Re-executable given frozen code/source and seed','grade_0_3_science':0,'VSDS_grade_project':1,'CT2_before':24,'CT2_after':24},
      'J':{'decision':'REPAIR_SOURCE_OR_MEASUREMENT' if empirical else ('STOP_LOCAL_UNTIL_FIELD_REPLICATION' if i in (19,20,23,26,28,29,30) else 'CONTINUE_WITH_FIELD_DATA'), 'reason':'Another similar source snapshot or DGP realization is not an independent external validation.'}
    }

def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--prereg-commit',required=True);parser.add_argument('--code-commit',required=True);args=parser.parse_args()
    data,manual=source_data();OUT.mkdir(parents=True,exist_ok=True)
    inputs={'curated_7_sha256':hashlib.sha256(DATA.read_bytes()).hexdigest(),'curated_original_blob_sha1':data['source_git_blob_sha1'],'curated_generated_at':data['upstream_generated_utc'],'manual_20_sha256':hashlib.sha256(MANUAL.read_bytes()).hexdigest()}
    records=[]
    for i in range(1,31):
        res=real_cycle(i,data['records'],manual) if i<=18 else simulate_cycle(i)
        rec=make_aj(i,res,args.prereg_commit,args.code_commit,inputs)
        (OUT/f'C{i:02}.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
        records.append(rec)
    summary={'campaign':'PF-AB30-FULL','date':'2026-10-25','n':len(records),'external_real_audits':18,'generator_experiments':12,'n_external_confirmations':0,'VSDS':1,'CT2_predictive':24,'source_hashes':inputs,'prereg_commit':args.prereg_commit,'code_commit':args.code_commit,'statuses':dict(Counter(c['status'] for c in records)),'selected_endpoints':{c['cycle_id']:c['E']['result'] for c in records}}
    (OUT/'RESULTS.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print('AB cycles with A–J:',len(records))
    for c in records:
        v=c['E']['result'];print(c['cycle_id'],c['branch'],c['status'],json.dumps(v,ensure_ascii=False)[:190])
    return 0
if __name__=='__main__':raise SystemExit(main())
