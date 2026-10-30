"""Read-only aggregate replication from four captured official AEC CSVs."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
import scipy
from scipy.stats import pearsonr, spearmanr
import statsmodels
import statsmodels.api as sm


def table(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        next(stream)
        rows = list(csv.DictReader(stream))
    index = {}
    for row in rows:
        key = int(row.get("DivisionID", row.get("DivisionId")))
        if key in index:
            raise ValueError("DUPLICATE_DIVISION_ID")
        index[key] = row
    if len(index) != 150:
        raise ValueError("EXPECTED_150_DIVISIONS")
    return index


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path)
    parser.add_argument("project", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    names = ["HouseNominationsByDivisionDownload-31496.csv",
             "GeneralEnrolmentByDivisionDownload-31496.csv",
             "HouseInformalByDivisionDownload-31496.csv",
             "HouseTurnoutByDivisionDownload-31496.csv"]
    nom, enrol, informal, turnout = [table(args.raw / n) for n in names]
    assert nom.keys() == enrol.keys() == informal.keys() == turnout.keys()
    panel = []
    for key in sorted(nom):
        n, e, i, t = [d[key] for d in (nom, enrol, informal, turnout)]
        assert len({r["StateAb"] for r in (n, e, i, t)}) == 1
        assert len({r["DivisionNm"] for r in (n, e, i, t)}) == 1
        panel.append(dict(id=key, division=n["DivisionNm"], state=n["StateAb"], demographic=n["Demographic"],
            nominations=int(n["Nominations"]), closeOfRollsEnrolment=int(e["CloseOfRollsEnrolment"]),
            finalEnrolment=int(e["Enrolment"]), informalVotes=int(i["InformalVotes"]),
            formalVotes=int(i["FormalVotes"]), totalBallots=int(i["TotalVotes"]),
            informalPercent=float(i["InformalPercent"]), turnoutVotes=int(t["Turnout"]),
            turnoutPercent=float(t["TurnoutPercentage"]), turnoutSwing=float(t["TurnoutSwing"])))
    reference = args.project / "research/ABH_AECCHOICE5_20261028/AEC2025_DIVISION_PANEL.csv"
    with reference.open(encoding="utf-8-sig", newline="") as stream:
        stored = {int(r["id"]): r for r in csv.DictReader(stream)}
    differences = []
    for row in panel:
        for field, value in row.items():
            expected = stored[row["id"]][field]
            if isinstance(value, (int, float)):
                if abs(value - float(expected)) > 1e-10:
                    differences.append({"id":row["id"], "field":field})
            elif value != expected:
                differences.append({"id":row["id"], "field":field})
    if differences:
        raise ValueError("ORIGINAL_TO_PANEL_DIFFERENCES: " + json.dumps(differences))
    y = np.array([r["informalPercent"] for r in panel])
    x = np.array([r["nominations"] for r in panel])
    logenrol = np.log([r["closeOfRollsEnrolment"] for r in panel])
    states = sorted({r["state"] for r in panel})
    demographics = sorted({r["demographic"] for r in panel})
    state_dummies = np.column_stack([[int(r["state"]==s) for r in panel] for s in states[1:]])
    demo_dummies = np.column_stack([[int(r["demographic"]==d) for r in panel] for d in demographics[1:]])
    baseline = np.column_stack([np.ones(len(y)), logenrol, state_dummies, demo_dummies])
    choice = np.column_stack([np.ones(len(y)), logenrol, x, state_dummies, demo_dummies])
    fit0, fit1 = sm.OLS(y, baseline).fit(), sm.OLS(y, choice).fit(cov_type="HC3")
    unexposed = np.array([r["division"] not in {"Calwell", "Riverina"} for r in panel])
    high = x >= 7
    predictions = {name: np.zeros(len(y)) for name in ("mean", "demo", "choice")}
    base_cv = np.column_stack([np.ones(len(y)), logenrol, demo_dummies])
    choice_cv = np.column_stack([base_cv, x])
    for state in states:
        test = np.array([r["state"]==state for r in panel]); train = ~test
        predictions["mean"][test] = y[train].mean()
        for name, matrix in [("demo",base_cv),("choice",choice_cv)]:
            model = sm.OLS(y[train], matrix[train]).fit()
            predictions[name][test] = model.predict(matrix[test])
    result = {
        "scope":"RETROSPECTIVE_ORIGINAL_BYTE_REPLICATION_NO_CAUSAL_OR_FORECAST_CLAIM",
        "versions":{"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__,"statsmodels":statsmodels.__version__},
        "originals":[{"file":n,"sha256":hashlib.sha256((args.raw/n).read_bytes()).hexdigest()} for n in names],
        "rows":len(panel),"states":len(states),"demographic_types":len(demographics),"stored_panel_field_differences":len(differences),
        "sums":{"informal":sum(r["informalVotes"] for r in panel),"ballots":sum(r["totalBallots"] for r in panel)},
        "pearson":float(pearsonr(x,y).statistic),"spearman":float(spearmanr(x,y).statistic),
        "excluded_spearman":float(spearmanr(x[unexposed],y[unexposed]).statistic),
        "baseline_r2":float(fit0.rsquared),"choice_r2":float(fit1.rsquared),
        "candidate_coef":float(fit1.params[2]),"candidate_hc3_se":float(fit1.bse[2]),
        "high_low_difference":float(y[high].mean()-y[~high].mean()),
        "excluded_high_low_difference":float(y[high & unexposed].mean()-y[(~high) & unexposed].mean()),
        "leave_state_out_mae":{n:float(np.mean(np.abs(y-p))) for n,p in predictions.items()},
        "limits":["Captured bytes match the historical mirrors but do not attest first_public_at", "Outcome and headers were known before this replication", "Post-election observational association, not causal identification or temporal prediction"]}
    expected = json.loads((args.project/"research/ABH_AECCHOICE5_20261028/AEC2025_METRICS.json").read_text(encoding="utf-8"))
    checks = {"pearson":expected["C02"]["pearson"],"spearman":expected["C02"]["spearman"],
        "excluded_spearman":expected["C02"]["preexposed_excluded_Spearman"],
        "baseline_r2":expected["C03"]["baseline_r2"],"choice_r2":expected["C03"]["with_nominations_r2"],
        "candidate_coef":expected["C03"]["candidate_coef_pp"],"candidate_hc3_se":expected["C03"]["candidate_HC3SE"],
        "high_low_difference":expected["C04"]["difference_pp"],"excluded_high_low_difference":expected["C04"]["outliers_excluded"]["difference_pp"]}
    result["comparisons"]={k:{"expected":v,"actual":result[k],"absolute_error":abs(result[k]-v),"pass_abs_1e_8":abs(result[k]-v)<1e-8} for k,v in checks.items()}
    for n,value in result["leave_state_out_mae"].items():
        target=expected["C05"]["models"][n]["MAE"]
        result["comparisons"]["cv_mae_"+n]={"expected":target,"actual":value,"absolute_error":abs(value-target),"pass_abs_1e_8":abs(value-target)<1e-8}
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"rows":result["rows"],"panel_differences":len(differences),"comparisons_pass":sum(c["pass_abs_1e_8"] for c in result["comparisons"].values()),"comparisons_total":len(result["comparisons"])}))
    if not all(c["pass_abs_1e_8"] for c in result["comparisons"].values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
