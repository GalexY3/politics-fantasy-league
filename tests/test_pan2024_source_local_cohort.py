"""Fixture-only QA of a source-local plan inventory; never inspect IAEN."""
import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pan2024_local_cohort.py"
spec = importlib.util.spec_from_file_location("pan2024_local_cohort", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def synthetics():
    return (
        (37, "2024\nI. PRUEBAS\n1. Reales Decretos\n"
             "REAL DECRETO SINTETICO UNO\n"
             "Objetivo: evaluar un ejemplo inexistente.\n"
             "Ministerio: MINISTERIO FICTICIO A\n"
             "Coproponentes: FICTICIO B\n"),
        (38, "2024\nII. OTRO BLOQUE\n1. Leyes Organicas\n"
             "LEY ORGÁNICA SINTETICA DOS\n"
             "Objetivo: inventar otro ejemplo.\n"
             "Ministerio: MINISTERIO FICTICIO B\n"),
        (39, "2024\n2. Leyes\nLEY SINTETICA TRES\n"
             "Objetivo: demostrar trazabilidad local.\n"
             "Ministerio: MINISTERIO FICTICIO C\n"),
    )


def test_three_source_local_entries_preserve_types_pages_and_unknown_outcomes():
    rows = mod.identify_plan_items(synthetics())
    assert len(rows) == 3
    assert [x["normative_class"] for x in rows] == [
        "ROYAL_DECREE", "ORGANIC_LAW", "LAW"]
    assert [x["objective_pdf_page"] for x in rows] == [37, 38, 39]
    assert all(x["IAEN_link"] is None and x["actual_approval_outcome"] is None
               and x["first_public_at"] is None for x in rows)
    assert all(x["text_extraction_is_not_manual_transcription"] is True for x in rows)
    assert len({x["source_local_id"] for x in rows}) == 3


def test_aggregate_counts_are_source_local_not_independent_denominator():
    result = mod.audit_source_local_counts(
        mod.identify_plan_items(synthetics()),
        expected={"ROYAL_DECREE": 1, "ORGANIC_LAW": 1, "LAW": 1},
    )
    assert result["provisional_source_local_items"] == 3
    assert result["independent_register_denominator_certified"] is False
    assert result["first_public_at_verified"] is False
    assert result["R5"] == "STOP"
    assert result["AB_scientific_cycles"] == 0


def test_false_denominator_or_type_distribution_stops():
    rows = mod.identify_plan_items(synthetics())
    with pytest.raises(mod.CohortGateError, match="198_AND_CLASS_DISTRIBUTION"):
        mod.audit_source_local_counts(rows, expected={"ROYAL_DECREE": 2, "LAW": 1})


def test_missing_ministry_rejects_even_if_objective_present():
    pages = ((37, "REAL DECRETO FICTICIO\nObjetivo: algo.\n"),)
    with pytest.raises(mod.CohortGateError, match="MISSING_OBJECTIVE_OR_MINISTRY"):
        mod.identify_plan_items(pages)


def test_missing_title_anchor_never_infers_a_regulation():
    pages = ((37, "NORMA NO CLASIFICADA\nObjetivo: algo.\nMinisterio: FICTICIO\n"),)
    with pytest.raises(mod.CohortGateError, match="ENTRY_WITHOUT_TITLE_ANCHOR"):
        mod.identify_plan_items(pages)


def test_reversed_sequence_does_not_pretend_to_be_a_complete_entry():
    pages = ((37, "Ministerio: FICTICIO\nREAL DECRETO FICTICIO\nObjetivo: algo.\n"),)
    with pytest.raises(mod.CohortGateError, match="OBJECTIVE_MINISTRY_ORDER_AMBIGUOUS"):
        mod.identify_plan_items(pages)


def test_page_order_or_invalid_input_rejected():
    for pages in ((), ((38, "A"), (37, "B")),
                  ((37, "REAL DECRETO\nObjetivo: test\nMinisterio: X"),) * 252):
        with pytest.raises(mod.CohortGateError, match="INVALID_PAGE_ORDER_OR_INPUT"):
            mod.identify_plan_items(pages)


def test_source_and_output_inside_git_are_forbidden(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    pdf = repo / "PAN_2024.pdf"
    pdf.write_bytes(b"%PDF-1.7\nSYNTHETIC")
    outdir = tmp_path / "private"
    outdir.mkdir()
    with pytest.raises(mod.CohortGateError, match="SOURCE_OR_OUTPUT_NOT_OUTSIDE_REPO"):
        mod.run(pdf_path=pdf, out_dir=outdir, repo_root=repo)


def test_unauthenticated_changed_original_is_rejected_before_pdf_parse(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    private = tmp_path / "private"
    private.mkdir()
    pdf = private / "PAN_2024.pdf"
    pdf.write_bytes(b"%PDF-1.7\nOTHER SYNTHETIC SOURCE")
    with pytest.raises(mod.CohortGateError, match="ORIGINAL_SHA256_CHANGED"):
        mod.run(pdf_path=pdf, out_dir=private, repo_root=repo)
