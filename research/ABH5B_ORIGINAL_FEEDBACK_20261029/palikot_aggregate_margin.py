"""Noncausal decomposition of published RCT aggregate story counts into shares.
Palikot et al 2026, Quantitative Marketing and Economics, DOI:10.1007/s11129-026-09311-3.
Full-randomized-school ITT is causal for bundled contest, but conditional
mean among active users is post-treatment selection, NOT causal. The algebra
requires active share to correspond to the same nonzero outcome and time window.
"""
from fractions import Fraction as F
import json
PUBLISHED={
 '4_weeks':{'control_stories':F('0.146'),'treatment_increment':F('0.178'),
            'control_active':F('0.065'),'treatment_active':F('0.096')},
 '12_weeks':{'control_stories':F('0.395'),'treatment_increment':F('0.301'),
             'control_active':F('0.122'),'treatment_active':F('0.143')}
}

def decompose(row):
    if set(row)!=set(next(iter(PUBLISHED.values()))):raise ValueError('INCOMPLETE_PUBLISHED_ROW')
    mu0=row['control_stories'];mu1=mu0+row['treatment_increment']
    p0=row['control_active'];p1=row['treatment_active']
    if not 0<p0<=1 or not 0<p1<=1 or mu0<0 or mu1<0:raise ValueError('INCONSISTENT_RATE')
    r0=mu0/p0;r1=mu1/p1
    # Shapley/Kitagawa symmetric identity mu=p*r, not mediation identification.
    extensive=(p1-p0)*(r0+r1)/2
    intensive=(r1-r0)*(p0+p1)/2
    assert extensive+intensive==mu1-mu0
    return {'control_mean':float(mu0),'treatment_mean_reconstructed':float(mu1),
      'difference':float(mu1-mu0),'control_active_share':float(p0),'treatment_active_share':float(p1),
      'activity_percentage_point_difference':float(100*(p1-p0)),
      'conditional_story_mean_if_active_definition_matches':{'control':round(float(r0),6),'treatment':round(float(r1),6)},
      'symmetric_extensive_component':round(float(extensive),8),
      'symmetric_intensive_component':round(float(intensive),8),
      'extensive_share_of_difference':round(float(extensive/(mu1-mu0)),8),
      'intensive_share_of_difference':round(float(intensive/(mu1-mu0)),8),
      'exact_algebra_check':True}

def analyze():
    return {'schema':'pfl.palikot.original.aggregate.margins.v1',
      'source':'https://doi.org/10.1007/s11129-026-09311-3',
      'design':'138 randomized schools; 9327 students. Treatment bundles contest rank, prizes, in-app notices and parental WhatsApp. Control has standard leaderboard.',
      'periods':{k:decompose(v) for k,v in PUBLISHED.items()},
      'critical_assumptions':['Active share represents probability of positive completed-story count in same four- or twelve-week measurement period.',
       'Published adjusted model treatment effects and control means are treated as comparable raw arm expectations; original methods use strata weighting and clustering, so algebra is descriptive approximation only.',
       'Reported rates and mean effects are rounded, and their joint covariance is unavailable.',
       'Active-user conditional means and components are POST-TREATMENT SELECTED, NOT causal intensive or extensive mediation effects.',
       'Four- and twelve-week windows differ in length; do not interpret different aggregate shares as weekly trends.'],
      'no_claims':['not isolated leaderboard impact','not adult political behavior','no original participant records','not independent RCT replication'],
      'grade':'0/3','CT2_scientific':22}
if __name__=='__main__':print(json.dumps(analyze(),indent=2))
