"""Aggregate-only test of a 2024 randomized leaderboard field experiment.
Original paper: Kloc, Belo & Li (2024) author PDF, Table 3 p.16.
All five outcome estimates standardized except login indicator; pooled original
SE cluster by user; normal-approximation, not re-estimation from individual rows.
"""
import json
from math import sqrt, erf
from statistics import NormalDist

PAPER='https://rodrigobelo.com/assets/pdf/leaderboards.pdf'
TABLE={
 'login': {'beta':0.008, 'se':0.006, 'n_panel':108171, 'unit':'visits indicator per user-day'},
 'active_time': {'beta':0.009, 'se':0.016, 'n_panel':108171, 'unit':'standard deviations daily activity'},
 'learning': {'beta':0.008, 'se':0.014, 'n_panel':108171, 'unit':'standard deviations daily learning'},
 'practice': {'beta':0.002, 'se':0.020, 'n_panel':108171, 'unit':'standard deviations daily practice'},
 'hardest_subject': {'beta':0.007, 'se':0.015, 'n_panel':79956, 'unit':'standard deviations subject time'},
}

def analyze():
    normal=NormalDist()
    z_single=normal.inv_cdf(.975)
    z_bonf=normal.inv_cdf(1-.05/(2*len(TABLE)))
    rows={}
    for key,source in TABLE.items():
        b,se=source['beta'],source['se']
        rows[key]={**source,'ci95_normal':[round(b-z_single*se,8),round(b+z_single*se,8)],
            'ci_bonferroni_95_family':[round(b-z_bonf*se,8),round(b+z_bonf*se,8)],
            't_standard_normal_approx':round(b/se,5)}
    return {
     'schema':'pfl.kloc.published.randomized.leaderboard.bounds.v1',
     'source_pdf':PAPER,'paper_year':2024,'table':'3 (printed p.16; PDF index15)',
     'eligible_users_reported':3762,'original_assignment':'2/3 leaderboard offer, 1/3 no leaderboard at registration',
     'exposure_mechanism':'actual leaderboard allocation delayed 3+ days, conditional on continued activity',
     'rows':rows,
     'primary_active_time':{'single_endpoint_upper_below_0_05_SD':rows['active_time']['ci95_normal'][1]<.05,
                           'five_endpoint_bonf_upper_below_0_05_SD':rows['active_time']['ci_bonferroni_95_family'][1]<.05,
                           'max_plausible_positive_effect_SD_preselected':rows['active_time']['ci95_normal'][1],
                           'max_plausible_positive_effect_SD_familywise':rows['active_time']['ci_bonferroni_95_family'][1]},
     'interpretation':['The 95% normal approximation for preselected active-time excludes a +0.05 SD positive offer effect; 5-endpoint Bonferroni CI does not.',
       'Bonferroni is conservative if endpoints correlated; not evidence of null or full equivalence.',
       '3,762 eligible analysis population does not establish ITT for all registered users; assignment precedes activity-based exposure eligibility.',
       'Dispersion among already-ranked groups is post-allocation association and not the direct randomized leaderboard offer effect.',
       'Published table reports clustered user SE, panel rows are not independent participants; no re-estimation or new human data.'],
     'scientific_grade':'0/3','CT2_science':22,'new_human_rows':0}
if __name__=='__main__':
 print(json.dumps(analyze(),indent=2,ensure_ascii=False))
