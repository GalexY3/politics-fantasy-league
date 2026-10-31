"""AB10 P03: frozen tests, all text and sources completely synthetic.

Do not execute these tests before the frozen Git commit is pushed remotely.
"""
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts import ab10_mempalace_semantic_benchmark as m


def test_fixed_ten_cases_have_distinct_targets_and_no_question_id_leakage():
    corpus = m.docs()
    assert len(corpus) == 10
    assert len({x["file"] for x in corpus}) == 10
    assert all("synthetic" in x["current_content"].lower() or "sintético" in x["current_content"].lower()
               for x in corpus)
    assert all(x["file"].startswith("syn-") for x in corpus)
    assert all("DECISION ACTUAL" in x["current_content"] for x in corpus)
    assert all("VERSION RETIRADA" in x["historical_content"] for x in corpus)
    assert set(x["query"] for x in corpus) == {x["query"] for x in m.docs()}


def test_textual_baseline_is_runnable_on_identical_current_docs_without_history():
    corpus = m.docs()
    for case in corpus:
        top = m.fts_search(corpus, case["query"])
        assert len(top) <= 3
        assert all(item in {x["file"] for x in corpus} for item in top)
    with pytest.raises(m.MemBenchmarkError, match="TOPK_MUST_BE_EQUAL"):
        m.fts_search(corpus, corpus[0]["query"], k=4)


def test_cli_parse_requires_allowlisted_real_source_metadata():
    observed = """
Results for: fictional question
[1] sample / general
    Source: syn-04.md
    Match: cosine_sim=0.87 bm25=0.72
[2] sample / general
    Source: syn-02.md
"""
    files = {x["file"] for x in m.docs()}
    assert m.parse_mempalace_sources(observed, allowed=files) == ("syn-04.md", "syn-02.md")
    with pytest.raises(m.MemBenchmarkError, match="SEMANTIC_SOURCE_NOT_IN_CURRENT_CORPUS"):
        m.parse_mempalace_sources("Source: syn-77.md", allowed=files)
    with pytest.raises(m.MemBenchmarkError, match="SEMANTIC_CLI_NO_VALID_TOPK"):
        m.parse_mempalace_sources("No results", allowed=files)


def test_deduplicate_multiple_chunks_from_same_document_before_top3():
    raw = "Source: syn-03.md\nSource: syn-03.md\nSource: syn-02.md"
    assert m.parse_mempalace_sources(raw, allowed={"syn-03.md", "syn-02.md"}) == (
        "syn-03.md", "syn-02.md"
    )


def test_output_must_be_new_private_folder_not_inside_any_git_checkout(tmp_path):
    pristine = tmp_path / "private_root"
    pristine.mkdir()
    assert m.ensure_off_git(pristine) == pristine
    repo = tmp_path / "checkout"
    repo.mkdir()
    (repo / ".git").mkdir()
    private = repo / "private"
    private.mkdir()
    with pytest.raises(m.MemBenchmarkError, match="INSIDE_GIT_CHECKOUT"):
        m.ensure_off_git(private)
    (pristine / "current").mkdir()
    with pytest.raises(m.MemBenchmarkError, match="NEW_EMPTY"):
        m.ensure_off_git(pristine)


def test_create_current_and_retired_docs_but_checksum_sources_without_real_data(tmp_path):
    corpus = m.docs()
    receipts = m.create_files(tmp_path, corpus)
    assert len(receipts) == 20
    assert len(list((tmp_path / "current").glob("*.md"))) == 10
    assert len(list((tmp_path / "historical").glob("*.md"))) == 10
    assert all(len(x) == 64 for x in receipts.values())
    with pytest.raises(FileExistsError):
        m.create_files(tmp_path, corpus)


def test_mempalace_requires_actual_installed_cli_and_offline_cache(tmp_path):
    with pytest.raises(m.MemBenchmarkError, match="NOT_INSTALLED_OR_MODEL_CACHE_MISSING"):
        m.environ_for_mempalace(tmp_path, tmp_path / "isolated")


def test_lexical_query_does_not_embed_document_target_identifier():
    for item in m.docs():
        assert item["file"] not in item["query"]
        assert item["query"].casefold().find(item["current_content"].split("FICTICIO ")[1].split(" ")[0].casefold()) < 0
        query = m.tokenize(item["query"])
        assert " OR " in query
