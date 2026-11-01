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


def test_nested_protected_worktree_path_cannot_mutate_shared_git_objects(monkeypatch, tmp_path):
    protected = tmp_path / "PFL-trabajo"
    nested = protected / "src" / "politics_fantasy"
    nested.mkdir(parents=True)
    calls = []

    def forbid_git(*args, **kwargs):
        calls.append(args)
        raise AssertionError("Git must never execute within protected subtree")

    monkeypatch.setattr(subprocess, "run", forbid_git)
    with pytest.raises(ProbeError, match="PROTECTED_READONLY_CHECKOUT_FORBIDDEN"):
        probe_pair(SHA_A, SHA_B, repo_dir=nested)
    assert calls == []


def test_linked_worktree_gitdir_into_protected_repository_is_rejected(monkeypatch, tmp_path):
    protected = tmp_path / "PFL-trabajo"
    gitdir = protected / ".git" / "worktrees" / "linked"
    gitdir.mkdir(parents=True)
    linked = tmp_path / "linked-worktree"
    linked.mkdir()
    (linked / ".git").write_text(f"gitdir: {gitdir}\n", encoding="utf-8")
    calls = []

    def forbid_git(*args, **kwargs):
        calls.append(args)
        raise AssertionError("shared object database was reached")

    monkeypatch.setattr(subprocess, "run", forbid_git)
    with pytest.raises(ProbeError, match="PROTECTED_READONLY_CHECKOUT_FORBIDDEN"):
        probe_pair(SHA_A, SHA_B, repo_dir=linked)
    assert calls == []


def test_git_env_override_cannot_redirect_object_writes(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setenv("GIT_OBJECT_DIRECTORY", str(tmp_path / "PFL-trabajo" / ".git" / "objects"))

    def forbid_git(*args, **kwargs):
        calls.append(args)
        raise AssertionError("Git object directory override reached")

    monkeypatch.setattr(subprocess, "run", forbid_git)
    with pytest.raises(ProbeError, match="GIT_ENV_OVERRIDE_NOT_ALLOWED"):
        probe_pair(SHA_A, SHA_B, repo_dir=tmp_path)
    assert calls == []
