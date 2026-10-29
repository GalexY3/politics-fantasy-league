"""Published aggregate-only partial identification of Pickal et al. 2026.
DOI 10.1016/j.lindif.2025.102836. No human rows.
F(4,422):427; F(4,340):345; F(4,339):344 under standard 5-cell ANOVA.
Bound 1–5 Likert outcomes with arm-specific missing allocations unknown.
"""
from fractions import Fraction
import json
ARM_COUNTS={"higher_up":86,"higher_down":81,"lower_up":75,"lower_down":95,"no_feedback":90}
K=5
INTEREST_HIGH_UP=Fraction(337,100)
INTEREST_CONTROL=Fraction(3)
COMPETENCE_HIGH_UP=Fraction(362,100)
COMPETENCE_CONTROL=Fraction(312,100)
def _bound(a,b,included_anova):
    if not isinstance(a,Fraction) or not isinstance(b,Fraction):raise TypeError('PUBLISHED_FRACTIONS_ONLY')
    n1,n0=ARM_COUNTS['higher_up'],ARM_COUNTS['no_feedback']
    unrepresented=sum(ARM_COUNTS.values())-included_anova
    if unrepresented<0 or unrepresented>sum(ARM_COUNTS.values())-2*K:raise ValueError('INVALID_MISSING_COUNT')
    others_capacity=sum(v-2 for k,v in ARM_COUNTS.items() if k not in ('higher_up','no_feedback'))
    feasible=[]
    for miss1 in range(min(n1-2,unrepresented)+1):
        for miss0 in range(min(n0-2,unrepresented-miss1)+1):
            residual=unrepresented-miss1-miss0
            if residual>others_capacity:continue
            low=a-b+Fraction(miss1,n1)*(1-a)-Fraction(miss0,n0)*(5-b)
            high=a-b+Fraction(miss1,n1)*(5-a)-Fraction(miss0,n0)*(1-b)
            feasible.append((low,high,miss1,miss0,residual))
    if not feasible:raise ValueError('NO_FEASIBLE_ALLOCATION')
    low=min(feasible,key=lambda x:x[0]);high=max(feasible,key=lambda x:x[1])
    return {'observed_group_mean_difference':str(a-b),'conditional_lower':str(low[0]),
      'conditional_upper':str(high[1]),'conditional_lower_decimal':round(float(low[0]),6),
      'conditional_upper_decimal':round(float(high[1]),6),
      'lower_witness_missing_higher_up_control_others':list(low[2:]),
      'upper_witness_missing_higher_up_control_others':list(high[2:]),
      'feasible_focal_allocations_enumerated':len(feasible)}
def analyze():
    total=sum(ARM_COUNTS.values())
    assert total==427
    n_motivation=340+K
    return {'schema':'pfl.pickal.aggregate.partialid.v1','source':'https://doi.org/10.1016/j.lindif.2025.102836',
      'pdf':'https://opus.bibliothek.uni-augsburg.de/opus4/files/127063/127063.pdf',
      'sample_in_five_reported_arms':total,'arm_counts':ARM_COUNTS,
      'performance_anova_cases_inferred_from_df':422+K,
      'interest_motivation_anova_cases_inferred_from_df':n_motivation,
      'treatment_check_anova_cases_inferred_from_df':339+K,
      'cases_not_in_motivation_anova':total-n_motivation,
      'cases_not_in_treatment_check_anova':total-(339+K),
      'conditional_interest_high_up_minus_control':_bound(INTEREST_HIGH_UP,INTEREST_CONTROL,n_motivation),
      'conditional_competence_high_up_minus_control':_bound(COMPETENCE_HIGH_UP,COMPETENCE_CONTROL,n_motivation),
      'assumptions':['F(4,340) represents standard one-way 5-arm ANOVA on 345 complete outcome cases',
      '82 cases in other analysis are unrepresented in this ANOVA; reason and arm distribution unknown',
      'Every arm has at least two represented observations; unrepresented scores can take any value in 1..5',
      'Published two-decimal group means treated as exact; slight rounding error ignored',
      'Only published marginal means and arm counts used, never pseudonymized row-level data'],
      'blocked_inferences':['not a re-estimated ITT','not an estimated dropout effect',
      'not observed unbalanced attrition','not an estimate of PFL effects'],
      'scientific_grade':'0/3','novel_scientific_findings':0}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,ensure_ascii=False))
