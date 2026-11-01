"""Synthetic Git merge-tree output only; no real branches or originals."""

import subprocess

import pytest

from scripts.pr_virtual_merge_probe import ProbeError, parse_merge_tree, probe_pair


SHA_A = "a" * 40
SHA_B = "b" * 40
TREE = "c" * 40


def test_real_conflict_lines_distinguish_coordination_from_scientific_paths():
    out = (TREE + "\n\nHANDOFF.md\nPROJECT_INDEX.json\n"
           "src/politics_fantasy/pan_iaen_original_frame.py\n\n"
           "Auto-merging HANDOFF.md\n"
           "CONFLICT (content): Merge conflict in HANDOFF.md\n"
           "CONFLICT (add/add): Merge conflict in src/politics_fantasy/pan_iaen_original_frame.py\n")
    report = parse_merge_tree(out, 1)
    assert report["tree_merge_has_conflicts"] is True
    assert report["coordination_conflict_paths"] == ["HANDOFF.md", "PROJECT_INDEX.json"]
    assert report["substantive_conflict_paths"] == ["src/politics_fantasy/pan_iaen_original_frame.py"]
    assert report["semantic_compatibility_verified"] is False
    assert report["R5_open"] is False


def test_clean_virtual_tree_is_not_scientific_approval():
    report = parse_merge_tree(TREE + "\n", 0)
    assert report["tree_merge_has_conflicts"] is False
    assert report["conflict_paths"] == []
    assert report["integration_approved"] is False


def test_missing_invalid_or_suspicious_paths_do_not_become_safe_evidence():
    with pytest.raises(ProbeError):
        parse_merge_tree(TREE + "\n\n../secrets\n", 1)
    with pytest.raises(ProbeError):
        parse_merge_tree("notatree\n", 0)
    with pytest.raises(ProbeError):
        parse_merge_tree(TREE + "\n", 1)


def test_probe_requires_exact_hashes_and_runs_git_with_argument_list(monkeypatch, tmp_path):
    calls = []

    def fake_run(args, **kwargs):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, stdout=TREE + "\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert probe_pair(SHA_A, SHA_B, repo_dir=tmp_path)["tree_merge_has_conflicts"] is False
    assert calls == [["git", "merge-tree", "--write-tree", "--name-only", SHA_A, SHA_B]]
    with pytest.raises(ProbeError):
        probe_pair("HEAD; echo secret", SHA_B, repo_dir=tmp_path)
