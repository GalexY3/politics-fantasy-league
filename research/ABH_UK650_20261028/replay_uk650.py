#!/usr/bin/env python3
"""Research-only reproduction. Input is a THIRD-PARTY MIRROR-derived CSV, not a signed official original.

Requires pandas scipy scikit-learn statsmodels numpy. Does not score voters or MPs.
Analyses are retrospective: margin/ENP use votes observed after the election.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
import statsmodels.formula.api as smf
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

HERE = Path(__file__).parent
df = pd.read_csv(HERE / "UK650_DERIVED_AGGREGATES.csv")
assert len(df) == 650 and df.id.nunique() == 650
assert df[['turnout','margin','enp','valid','candidate_sum','candidate_majority','declared_majority']].notna().all().all()
assert (df.valid == df.candidate_sum).all()
assert (df.candidate_majority == df.declared_majority).all()
assert set(df.country) == {"England", "Scotland", "Wales", "Northern Ireland"}
df['margin2'] = df.margin ** 2

def regression(formula):
    result = smf.ols(formula, data=df).fit(cov_type='HC3')
    return dict(beta={k:float(v) for k,v in result.params.items()},
                seHC3={k:float(v) for k,v in result.bse.items()},
                r2=float(result.rsquared))

def group_cv(group_column):
    preds = {name:np.empty(len(df),float) for name in ('mean','margin','margin_enp')}
    counts={}
    for group in sorted(df[group_column].unique()):
        train = df[df[group_column] != group]
        holdout = df[df[group_column] == group]
        index = df.index.get_indexer(holdout.index)
        preds['mean'][index] = train.turnout.mean()
        for label, cols in (('margin',['margin']),('margin_enp',['margin','enp'])):
            mdl = LinearRegression().fit(train[cols],train.turnout)
            preds[label][index] = mdl.predict(holdout[cols])
        counts[group] = int(len(holdout))
    return dict(group_counts=counts,
                metrics={name:dict(mae=float(mean_absolute_error(df.turnout,pred)),
                                   rmse=float(np.sqrt(mean_squared_error(df.turnout,pred))))
                         for name,pred in preds.items()})

s = df.sort_values('margin')
quart = [np.arange(int(i*len(s)//4), int((i+1)*len(s)//4)) for i in range(4)]  # exact preregistered V8 quartile boundaries
outputs = {
    'n':len(df),
    'quality':dict(candidate_sum_matches=int((df.valid==df.candidate_sum).sum()),
                   margin_matches=int((df.candidate_majority==df.declared_majority).sum())),
    'c02':dict(pearson=float(pearsonr(df.margin,df.turnout).statistic),
               spearman=float(spearmanr(df.margin,df.turnout).statistic),
               quartile_mean_turnout=[float(s.iloc[ix].turnout.mean()) for ix in quart],
               linear=regression('turnout ~ margin'),
               quadratic=regression('turnout ~ margin + margin2')),
    'c03':dict(enp_spearman=float(spearmanr(df.enp,df.turnout).statistic),
               enp_pearson=float(pearsonr(df.enp,df.turnout).statistic),
               ordinary=regression('turnout ~ margin + enp'),
               region_adjusted=regression('turnout ~ margin + enp + C(region)')),
    'c04':dict(region_adjusted=regression('turnout ~ margin + C(region)'),
               country_spearman={nation:float(spearmanr(
                   group.margin,group.turnout).statistic)
                   for nation,group in df.groupby('country')}),
    'c05':dict(leave_one_country_out=group_cv('country'),
               leave_one_region_out=group_cv('region'))
}
print(json.dumps(outputs,ensure_ascii=False,indent=2))
