"""Reproduce the EU27 descriptive diagnostics. Data are transcribed official HTML, NOT signed original CSV."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, theilslopes
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).parent
df = pd.read_csv(ROOT / "EU27_OFFICIAL_HTML_TRANSCRIPTION.csv")
assert len(df) == 27 and df.iso.nunique() == 27 and df.notna().all().all()
def correlation(a, b):
    return {"n": len(a), "pearson": float(pearsonr(a,b).statistic), "spearman": float(spearmanr(a,b).statistic)}

x, y = df.turnout2024.to_numpy(), df.women2024.to_numpy()
model_results = {}
for label, features in {
    "M0_mean": [], "M1_2019_women": ["women2019"],
    "M2_2024_turnout": ["turnout2024"],
    "M3_both": ["women2019", "turnout2024"]
}.items():
    predictions = []
    for i in range(len(df)):
        train = df.drop(df.index[i])
        if not features:
            pred = float(train.women2024.mean())
        else:
            reg = LinearRegression().fit(train[features], train.women2024)
            pred = float(reg.predict(df.iloc[[i]][features])[0])
        predictions.append(pred)
    model_results[label] = {"mae": float(mean_absolute_error(y,predictions)),
                            "rmse": float(np.sqrt(mean_squared_error(y,predictions)))}
slope = theilslopes(y,x)
loo = [correlation(np.delete(x,i),np.delete(y,i))["spearman"] for i in range(len(df))]
compulsory = {}
for code_set in ({"BE","BG","LU","CY","EL"}, {"BE","BG","LU","EL"}):
    tmp=df[~df.iso.isin(code_set)]
    compulsory[",".join(sorted(code_set))] = correlation(tmp.turnout2024,tmp.women2024)
metrics = {
    "n":27, "c02": correlation(x,y),
    "theil_women_pp_per_10pp_turnout": float(slope.slope*10),
    "loo_spearman_min": float(min(loo)), "loo_spearman_max": float(max(loo)),
    "c03": compulsory,
    "c04": correlation(df.turnout2024-df.turnout2019,df.women2024-df.women2019),
    "c05":model_results
}
print(json.dumps(metrics,indent=2,ensure_ascii=False))
