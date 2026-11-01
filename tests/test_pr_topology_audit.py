"""Synthetic PR metadata only. No remote activity or repository mutation."""
import pytest
from scripts.pr_topology_audit import analyze, TopologyError

def pr(num, head, base, files):
    return {"number": num, "headRefName": head, "baseRefName": base,
            "headRefOid": f"{num:040x}", "files": [
                {"path": path, "changeType": "MODIFIED"} for path in files]}

def test_stacked_prs_are_dependency_not_parallel_conflict():
    rows=[pr(10,"p10","main",["research/INDEX.md","src/shared.py"]),
          pr(11,"p11","p10",["research/INDEX.md","src/one.py"]),
          pr(12,"p12","p11",["research/INDEX.md","src/two.py"])]
    result=analyze(rows)
    assert result["dependency_edges"]==[
        {"pr":11,"base_pr":10},{"pr":12,"base_pr":11}]
    assert not result["parallel_overlaps"]
    assert result["topological_order"]==[10,11,12]

def test_parallel_siblings_report_substantive_overlap_not_automatic_merge_conflict():
    result=analyze([
        pr(11,"first","origin",["src/policy.py","HANDOFF.md"]),
        pr(12,"second","origin",["src/policy.py","HANDOFF.md"])])
    assert result["parallel_overlaps"]==[{
        "left_pr":11,"right_pr":12,"relationship":"SAME_BASE",
        "substantive_paths":["src/policy.py"],
        "coordination_paths":["HANDOFF.md"],
        "merge_conflict_proven":False}]

def test_sibling_only_common_generated_indexes_are_not_substantive_clashes():
    report=analyze([pr(16,"rights","core",["PROJECT_INDEX.json","research/INDEX.md","src/a.py"]),
                    pr(18,"cohort","core",["PROJECT_INDEX.json","research/INDEX.md","src/b.py"])])
    assert report["parallel_overlaps"][0]["substantive_paths"]==[]
    assert report["parallel_overlaps"][0]["coordination_paths"]==[
        "PROJECT_INDEX.json","research/INDEX.md"]

def test_distinct_bases_that_do_not_share_a_lineage_are_possible_overlap():
    report=analyze([pr(7,"systems","main",["src/shared.py"]),
                    pr(8,"policy","other-base",["src/shared.py"])])
    assert report["parallel_overlaps"][0]["relationship"]=="DIVERGENT_BASES"

def test_no_guessed_hidden_or_missing_remote_base():
    result=analyze([pr(9,"unique","unknown-private-branch",["src/new.py"])])
    assert result["dependency_edges"]==[]
    assert result["external_or_unknown_bases"]==["unknown-private-branch"]
    assert result["unresolved_base_is_not_mergeable_attestation"] is True

def test_cycle_or_duplicate_names_and_invalid_paths_fail_closed():
    with pytest.raises(TopologyError,match="CYCLE"):
        analyze([pr(1,"a","b",["one"]),pr(2,"b","a",["two"])])
    with pytest.raises(TopologyError,match="DUPLICATE"):
        analyze([pr(1,"a","main",[]),pr(2,"a","main",[])])
    with pytest.raises(TopologyError,match="PATH"):
        analyze([pr(1,"a","main",["../../secret"])])
    with pytest.raises(TopologyError,match="SHA"):
        analyze([{**pr(1,"a","main",[]),"headRefOid":"bogus"}])

def test_untrusted_extra_json_fields_are_rejected():
    with pytest.raises(TopologyError,match="FIELDS"):
        analyze([{**pr(1,"a","main",[]),"source_original":"PII"}])

def test_output_conveys_only_metadata_never_scientific_approval():
    report=analyze([pr(7,"head","main",["src/module.py"])])
    assert report["R5_open"] is False
    assert report["scientific_AB_cycles"]==0
    assert report["integration_approved"] is False
    assert report["merge_conflict_test_executed"] is False
