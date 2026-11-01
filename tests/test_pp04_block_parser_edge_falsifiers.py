"""Falsifiers for source-local parser #11, using only invented page text."""

import pytest

from politics_fantasy.pan_iaen_original_frame import (
    parse_report_ministry_listings,
    require_private_output_directory,
)
from politics_fantasy.procedural_index_contract import GateError


def test_planned_heading_not_overridden_by_nonincluded_words_in_a_bullet():
    text = (
        "4.1.1.- INICIATIVAS NORMATIVAS INCLUIDAS EN EL PLAN ANUAL\n"
        "I. Aprobadas\n"
        "- Real Decreto sobre normas NO INCLUIDAS en un listado distinto.\n"
        "4.1.2.- NORMAS APROBADAS NO INCLUIDAS EN EL PLAN\n"
    )
    result = parse_report_ministry_listings(
        (text,), expected_total=1, expected_approved=1,
    )
    assert result["planned_listing_count"] == 1
    assert result["approved_listing_count"] == 1


def test_private_output_rejects_a_different_git_repository(tmp_path):
    source_repo = tmp_path / "source_repo"
    source_repo.mkdir()
    (source_repo / ".git").mkdir()
    other_repo = tmp_path / "other_repo"
    other_repo.mkdir()
    (other_repo / ".git").mkdir()
    with pytest.raises(GateError, match="PP04_PRIVATE_OUTPUT_MUST_BE_OUTSIDE"):
        require_private_output_directory(other_repo / "private", source_repo)


def test_unknown_roman_stage_does_not_inherit_approval_in_block_parser():
    text = (
        "4.1.1.- INICIATIVAS NORMATIVAS INCLUIDAS EN EL PLAN ANUAL\n"
        "I. Aprobadas\n- Real Decreto alfa.\n"
        "III. Rechazadas\n- Ley beta.\n"
        "4.1.2.- NORMAS NO INCLUIDAS\n"
    )
    with pytest.raises(GateError, match="IAEN_UNKNOWN_HEADING_CLASS"):
        parse_report_ministry_listings(
            (text,), expected_total=2, expected_approved=2,
        )


def test_private_output_rejects_worktree_git_file(tmp_path):
    repository = tmp_path / "home"
    repository.mkdir()
    worktree = tmp_path / "other_worktree"
    worktree.mkdir()
    (worktree / ".git").write_text("gitdir: ../shared/.git/worktrees/other", encoding="utf-8")
    with pytest.raises(GateError, match="PP04_PRIVATE_OUTPUT_MUST_BE_OUTSIDE"):
        require_private_output_directory(worktree / "private", repository)
