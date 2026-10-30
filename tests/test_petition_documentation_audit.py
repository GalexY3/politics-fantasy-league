"""Adversarial fixtures for an observational, publicly licensed petition dataset."""
import csv
from datetime import date
from pathlib import Path
import pytest

# Research directory is not a Python package; load exactly this frozen file.
import importlib.util
SOURCE = Path(__file__).resolve().parents[1] / "research/R0_INSTITUTIONAL_PETITIONS_20261030/petition_documentation_audit.py"
spec = importlib.util.spec_from_file_location("petition_documentation_audit", SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

FIELDS = ["identifiant","date_publication","nb_votes","statut","commission",
          "decision_commission","titre","description","url"]


def write_csv(tmp_path, rows):
    path = tmp_path / "petitions.csv"
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    return path


def row(uid, votes, decision="", year="2024", status="classee", commission="A"):
    return {"identifiant": str(uid), "date_publication": year + "-02-03",
            "nb_votes": str(votes), "statut": status, "commission": commission,
            "decision_commission": decision, "titre":"No emit", "description":"Person-like private text",
            "url":"https://example.invalid/private"}


def test_public_doc_field_is_not_actual_commission_inactivity(tmp_path):
    src = write_csv(tmp_path,[row(1,12000,""),row(2,150,"Decision")])
    x = mod.analyze(src)
    assert x["high_10000_plus"]["documented"] == 0
    assert x["low_100_to_9999"]["documented"] == 1
    assert x["outcome_meaning"] == "DECISION_FIELD_DOCUMENTED_VS_UNDOCUMENTED_NOT_REAL_DECISION"
    assert x["causal"] is False
    assert "private" not in str(x).lower()


def test_duplicate_key_rejected_not_double_counted(tmp_path):
    with pytest.raises(ValueError,match="DUPLICATE_OR_EMPTY_PETITION_KEY"):
        mod.analyze(write_csv(tmp_path,[row(1,100),row(1,200)]))


def test_future_and_open_are_not_assumed_closed(tmp_path):
    x=mod.analyze(write_csv(tmp_path,[row(1,100,status="ouverte"),
                                  row(2,100,year="2027"),row(3,100,year="2024")]))
    assert x["eligible"]==1 and x["counts"]["excluded_open"]==1
    assert x["counts"]["excluded_young"]==1


def test_unknown_votes_not_zero(tmp_path):
    x=mod.analyze(write_csv(tmp_path,[row(1,""),row(2,"NaN"),row(3,100)]))
    assert x["counts"]["excluded_missing"]==2
    assert x["eligible"]==1


def test_require_schema_and_reject_missing_columns(tmp_path):
    f=tmp_path/"bad.csv"
    f.write_text("date;nb_votes;example\n2024-02-03;100;long nonpersonal fixture without mandatory fields\n")
    with pytest.raises(ValueError,match="REQUIRED_FIELDS_MISSING"):
        mod.analyze(f)


def test_positive_year_consistency_only_descriptive(tmp_path):
    rows=[]
    for year in ("2023","2024"):
        for i in range(5):
            rows.append(row(year+"h"+str(i),15000,"Decision",year))
        for i in range(12):
            rows.append(row(year+"l"+str(i),200,"",year))
    x=mod.analyze(write_csv(tmp_path,rows))
    assert x["high_10000_plus"]["n"]==10 and x["low_100_to_9999"]["n"]==24
    assert x["verdict"]=="DESCRIPTIVE_POSITIVE_ASSOCIATION_NOT_CAUSAL"
    assert x["comparable_year_count"]==2
    assert x["person_identifiers_emitted"] is False


def test_insufficient_high_cases_does_not_become_positive(tmp_path):
    rows=[row(i,12000,"Decision") for i in range(1,4)]
    rows += [row(i,200) for i in range(4,20)]
    x=mod.analyze(write_csv(tmp_path,rows))
    assert x["verdict"]=="INCONCLUSIVE_INSUFFICIENT_COMPARABLE_STRATA"


def test_count_conservation_missing_and_low_support(tmp_path):
    rows=[row(1,150),row(2,2),row(3,"broken"),row(4,12000)]
    x=mod.analyze(write_csv(tmp_path,rows))
    assert x["counts"]["total"]==4
    assert x["counts"]["excluded_low_support"]==1
    assert x["counts"]["excluded_missing"]==1
    assert x["eligible"]==2
