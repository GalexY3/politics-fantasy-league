#!/usr/bin/env python3
"""Adversarial post-hoc audit. Never silently rewrite the raw RESULTS.json."""
from __future__ import annotations
from collections import Counter
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'research'/'AB30_COMPLETOS_20261025'
DIAGNOSTIC={
 'M05':('INVALID_COMPARISON','Coverage of interval vs arbitrary ±0.01 point band; width/coverage tradeoff unpriced.'),
 'T13':('INVALID_COMPARISON','Future observed outcome leaks into predictor; treatment not deployable.'),
 'T17':('INVALID_COMPARISON','Future topic unavailable at prediction time; treatment not deployable.'),
 'R19':('INVALID_COMPARISON','Raw observed agreement and chance-corrected excess agreement have different estimands.'),
 'R22':('INVALID_COMPARISON','Absolute degree counts and edge densities use different units and losses.'),
 'F29':('INVALID_BASELINE','All candidate probabilities are below 0.5 and tied on classification accuracy; arbitrary tie-break not competent.'),
}
DEFINITIONAL={
 'M04':'Comparator misdefines expressed denominator; candidate is definitional correction.',
 'M06':'Latest revision is defined as estimand truth; exercise verifies semantics.',
 'C07':'Target equals formula for standardized estimate; guaranteed zero error, tautological under this setup.',
 'C08':'Same as C07; sample mix fluctuation yields residual difference despite planned no-shift.',
 'C11':'Correct historical group label defines target; not a predictive empirical effect.',
 'C12':'Candidate implements exact tie definition.',
 'T16':'As-of snapshot truth is simply original snapshot; identity check.',
 'R24':'Unique undirected dyads mathematically equal upper triangle count.',
 'F30':'Historical as-of score is identical to initial score by the definition of the estimand.'}

def audit():
    raw=(DIR/'RESULTS.json').read_bytes(); obj=json.loads(raw); audited=[]
    for x in obj['cycles']:
        id=x['id'];h=x['E']['run_stress_holdout']['mean_loss_advantage']; a=x['E']['run_mechanism_ablation']['mean_loss_advantage']
        if id in DIAGNOSTIC: grade,reason=DIAGNOSTIC[id]
        elif id in DEFINITIONAL:grade,reason='DEFINITIONAL_ONLY',DEFINITIONAL[id]
        elif id=='C09':grade,reason='STRESS_REVERSAL','Shrinkage wins when rare group resembles base group and loses in withheld shifted rare-group regime.'
        elif id=='M03':grade,reason='IDENTIFICATION_FAILURE','Marginal group weights do not identify outcome-dependent MNAR selection; holdout favors pooled sample.'
        elif id=='M01':grade,reason='NEGATIVE_CONTROL','No systematic gain from Bayesian smoothing for MCAR at these sample sizes.'
        else:grade,reason='CONDITIONAL_SYNTHETIC','Experiment distinguishes methods under stipulated generator only; no original empirical support.'
        warnings=[]
        if abs(a)>0.5*max(abs(h),1e-12) and abs(h)>0.005:
            warnings.append('ABLATION_RETAINS_EFFECT_MATERIAL: mechanism removal does not fully eliminate advantage')
        if x['J']['verdict']=='SUPPORTED_IN_STIPULATED_GENERATOR_ONLY' and grade in ('DEFINITIONAL_ONLY','INVALID_COMPARISON','INVALID_BASELINE'):
            warnings.append('RAW_SUPPORT_DOWNGRADED_BY_ADVERSARIAL_REVIEW')
        x['F'].update({'independent_posthoc_audit':grade,'auditor_reason':reason,'flags':warnings})
        x['H']['update'] += ' | Adversarial audit: '+reason
        x['I'].update({'validity_after_audit':grade,'empirical_grade':'0/3','VSDS':'1/3','no_original_discovery':True})
        x['J'].update({'scientific_verdict':grade,'decision_after_audit':('REPAIR' if grade.startswith('INVALID') else 'STOP_FOR_EXTERNAL_EVIDENCE' if grade in ('DEFINITIONAL_ONLY','NEGATIVE_CONTROL') else 'CONTINUE_WITH_COMPETENT_FIELD_BASELINE'),'decision_reason':reason})
        audited.append(x)
    counts=dict(Counter(x['J']['scientific_verdict'] for x in audited))
    out={'method':'AB_3_2_1','date':'2026-10-25','source_raw_result_sha256':hashlib.sha256(raw).hexdigest(), 'source_prereg_sha256':obj['prereg_sha256'], 'n_cycles_A_to_J_completed_computational':len(audited),'n_empirical_field_cycles':0,'n_independent_external_replications':0,'scientific_novelties_N1_N2_N3':[0,0,0],'VSDS':'1/3','CT2_prediction':24,'audit_grade_counts':counts,'not_scientific_superiority_claim':'Counts of synthetic cases are not independent knowledge discoveries or calibrated scientific tests','cycles':audited}
    (DIR/'RESULTS_AUDITED.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return out

if __name__=='__main__':
    v=audit();print(json.dumps({'total':len(v['cycles']),'counts':v['audit_grade_counts'],'output':'RESULTS_AUDITED.json'},ensure_ascii=False))
